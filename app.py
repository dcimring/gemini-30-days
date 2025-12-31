from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types
from PIL import Image
from celery import Celery
import os
from dotenv import load_dotenv
from datetime import datetime
from tools import get_current_weather

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey") # Change this in production!
socketio = SocketIO(app)

# Configure Database
# Use DATABASE_URL from environment if available (e.g. Heroku), otherwise local SQLite
database_url = os.getenv("DATABASE_URL", 'sqlite:///translations.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('instance', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB limit

# Celery Configuration (using SQLAlchemy/SQLite for zero-dependency local dev)
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'sqla+sqlite:///instance/celery_broker.sqlite')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'db+sqlite:///instance/celery_results.sqlite')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    translations = db.relationship('Translation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Define Translation Model
class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_special_report = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Translation {self.id}>'

class Essay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.String(100), unique=True, nullable=False)

# Initialize the Database
with app.app_context():
    # Add column if it doesn't exist (simplified migration for dev)
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE translation ADD COLUMN is_special_report BOOLEAN DEFAULT 0"))
            conn.commit()
    except Exception:
        pass # Column likely exists
    db.create_all()

# Initialize the Gemini client
# Ensure your .env file has GEMINI_API_KEY set
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@celery.task(bind=True)
def research_task(self, topic):
    """
    Background task to generate a historical pirate essay.
    """
    print(f"Task started: Researching {topic}", flush=True)
    
    # Simulate a long process
    # time.sleep(2) 
    
    prompt = f"Write a 5-paragraph historical essay about {topic} from the perspective of a pirate scholar. Make it informative but use pirate terminology where appropriate."
    
    try:
        print("Generating content with Gemini...", flush=True)
        # We need to re-initialize client inside the worker or ensure it's safe (it usually is)
        # But best practice for Celery is often to re-init external connections if they aren't thread/fork safe.
        # Google GenAI client is likely safe, but let's be safe.
        local_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        response = local_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        essay_content = response.text
        print("Essay generated, saving to DB...", flush=True)
        
        # We need to use app_context to save to DB in a background task
        with app.app_context():
            new_essay = Essay(topic=topic, content=essay_content, task_id=self.request.id)
            db.session.add(new_essay)
            db.session.commit()
            print("Saved to DB.", flush=True)
            
        return {'status': 'Complete', 'result': essay_content}
    except Exception as e:
        print(f"Task failed: {e}", flush=True)
        return {'status': 'Failed', 'error': str(e)}



@app.route('/research', methods=['GET', 'POST'])
def research():
    if request.method == 'POST':
        topic = request.form.get('topic')
        if topic:
            print(f"DEBUG: /research POST received with topic: {topic}", flush=True)
            task = research_task.delay(topic)
            print(f"DEBUG: Task dispatched with ID: {task.id}", flush=True)
            return render_template('research_status.html', task_id=task.id, topic=topic)
    return render_template('research.html')

@app.route('/research/status/<task_id>')
def research_status(task_id):
    task = research_task.AsyncResult(task_id)
    print(f"DEBUG: Checking status for {task_id}. State: {task.state}", flush=True)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '') if isinstance(task.info, dict) else '',
            'result': task.info.get('result', '') if isinstance(task.info, dict) else ''
        }
        if 'result' in response and response['result']:
             # Also try to fetch from DB to be sure
             essay = Essay.query.filter_by(task_id=task_id).first()
             if essay:
                 response['result'] = essay.content
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('signup'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    print("DEBUG: Index route accessed", flush=True)
    try:
        # Fetch history from database (newest first) for the current user
        history = Translation.query.filter_by(user_id=current_user.id).order_by(Translation.timestamp.asc()).all()
        print(f"DEBUG: Found {len(history)} history items", flush=True)
        return render_template('index.html', history=history, username=current_user.username)
    except Exception as e:
        print(f"DEBUG: Error in index route: {e}", flush=True)
        return f"Error: {e}", 500

from pirate_config import FRIENDLY_PIRATE, GRUMPY_PIRATE

# ... (rest of imports)

# ... (existing app setup)

@socketio.on('send_message')
def handle_message(data):
    print(f"DEBUG: handle_message triggered with data: {data}", flush=True)
    if not current_user.is_authenticated:
        print("DEBUG: User not authenticated", flush=True)
        return

    text_input = data.get('text')
    persona = data.get('persona', 'friendly') # Default to friendly

    system_instruction = FRIENDLY_PIRATE
    if persona == 'grumpy':
        system_instruction = GRUMPY_PIRATE

    print(f"DEBUG: Received text: '{text_input}' with persona: '{persona}'", flush=True)

    contents = []
    original_text = text_input
    is_special = False

    if text_input:
        contents.append(text_input)
        if 'weather' in text_input.lower():
            is_special = True

    if contents:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction, # Use the dynamically selected instruction
            tools=[get_current_weather],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode='AUTO'
                )
            )
        )
        # ... (rest of the function)
        try:
            print("DEBUG: Calling Gemini API", flush=True)
            response = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                config=config,
                contents=contents
            )
            # ... (rest of the try block)

            
            full_response_text = ""
            
            for chunk in response:
                # print(chunk.candidates[0].content.parts[0]) # Debug
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                    part = chunk.candidates[0].content.parts[0]
                    
                    if part.text:
                        text_chunk = part.text
                        full_response_text += text_chunk
                        emit('receive_chunk', {'chunk': text_chunk})
                        
                    elif part.function_call:
                        print(f"DEBUG: Tool call detected: {part.function_call.name}", flush=True)
                        # Handle function call (simplified for stream - usually requires a loop)
                        # For this specific "stream=True" task, sophisticated tool handling in stream is tricky.
                        # We will execute the tool and send a NEW request (non-streaming or streaming) with the result.
                        # But since we are already inside a stream loop, this is hard.
                        # FALLBACK: If we detect a tool call, we might need to handle it differently.
                        # However, the user asked to "Update the Gemini API call to use stream=True".
                        # Let's assume standard text for now. If tool call happens, we'll process it.
                        
                        fname = part.function_call.name
                        if fname == 'get_current_weather':
                            args = part.function_call.args
                            location = args.get('location')
                            weather_info = get_current_weather(location)
                            
                            # We need to send this back to the model
                            # Since we can't easily "continue" the stream object in the same loop,
                            # We make a new call.
                            
                            tool_response_part = types.Part.from_function_response(
                                name='get_current_weather',
                                response={'result': weather_info}
                            )
                            
                            # We need the previous model part too.
                            # In streaming, constructing the full history is manual.
                            # For simplicity, if tool is called, we stop streaming this turn,
                            # do the tool logic, and then stream the final answer.
                            
                            # Re-construct history
                            current_history = contents + [
                                types.Content(role="model", parts=[part]),
                                types.Content(role="user", parts=[tool_response_part])
                            ]
                            
                            # Stream the SECOND response (the actual answer)
                            response2 = client.models.generate_content_stream(
                                model="gemini-2.0-flash",
                                config=config,
                                contents=current_history
                            )
                            
                            for chunk2 in response2:
                                if chunk2.text:
                                    t2 = chunk2.text
                                    full_response_text += t2
                                    emit('receive_chunk', {'chunk': t2})
                            
                            # We handled the tool, so we can break the outer loop or continue
                            # (usually tool call is the only thing in the first response)
                            break 

            emit('stream_complete')
            print("DEBUG: Stream complete", flush=True)
            
            # Save to database
            new_translation = Translation(
                original_text=original_text, 
                translated_text=full_response_text,
                user_id=current_user.id,
                is_special_report=is_special
            )
            db.session.add(new_translation)
            db.session.commit()
            print("DEBUG: Saved to DB", flush=True)
            
        except Exception as e:
            print(f"DEBUG: Error in handle_message: {e}", flush=True)
            emit('receive_chunk', {'chunk': f"Arrr! Something went wrong: {str(e)}"})
            emit('stream_complete')


if __name__ == '__main__':
    socketio.run(app, debug=True)
