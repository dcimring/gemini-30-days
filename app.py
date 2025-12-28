from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types
from PIL import Image
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey") # Change this in production!

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('instance', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB limit

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

    def __repr__(self):
        return f'<Translation {self.id}>'

# Initialize the Database
with app.app_context():
    db.create_all()

# Initialize the Gemini client
# Ensure your .env file has GEMINI_API_KEY set
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    translated_text = ""
    original_text = ""
    
    if request.method == 'POST':
        file = request.files.get('file')
        text_input = request.form.get('text')
        
        contents = []
        model_input = ""
        
        try:
            # Handle Image Upload
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Open image for Gemini
                image = Image.open(filepath)
                contents.append(image)
                model_input = "Describe what is happening in this image as a salty pirate."
                original_text = "[Image Uploaded]"
                
                # Add text context if provided
                if text_input:
                     model_input += f" Also, consider this text from the user: {text_input}"
                     original_text += f" + Text: {text_input}"

                contents.append(model_input)
                
            elif text_input:
                original_text = text_input
                contents.append(text_input)
                
            if contents:
                config = types.GenerateContentConfig(
                    system_instruction="You are a salty sea captain from the 1700s. Translate everything the user says into pirate speak. Keep it brief, gritty, and use nautical slang. If an image is provided, describe it in pirate speak."
                )
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    config=config,
                    contents=contents
                )
                translated_text = response.text
                
                # Save to database
                new_translation = Translation(
                    original_text=original_text, 
                    translated_text=translated_text,
                    user_id=current_user.id
                )
                db.session.add(new_translation)
                db.session.commit()
                
                # Clean up uploaded file
                if file and allowed_file(file.filename):
                    if os.path.exists(filepath):
                        os.remove(filepath)

        except Exception as e:
            translated_text = f"Arrr! The winds be against us. Error: {str(e)}"
    
    # Fetch history from database (newest first) for the current user
    history = Translation.query.filter_by(user_id=current_user.id).order_by(Translation.timestamp.desc()).all()
        
    return render_template('index.html', translated_text=translated_text, original_text=original_text, history=history, username=current_user.username)

if __name__ == '__main__':
    app.run(debug=True)
