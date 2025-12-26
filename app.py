from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Translation Model
class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Translation {self.id}>'

# Initialize the Database
with app.app_context():
    db.create_all()

# Initialize the Gemini client
# Ensure your .env file has GEMINI_API_KEY set
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = ""
    original_text = ""
    
    if request.method == 'POST':
        original_text = request.form.get('text')
        if original_text:
            try:
                config = types.GenerateContentConfig(
                    system_instruction="You are a salty sea captain from the 1700s. Translate everything the user says into pirate speak. Keep it brief, gritty, and use nautical slang."
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    config=config,
                    contents=original_text
                )
                translated_text = response.text
                
                # Save to database
                new_translation = Translation(original_text=original_text, translated_text=translated_text)
                db.session.add(new_translation)
                db.session.commit()
                
            except Exception as e:
                translated_text = f"Arrr! The winds be against us. Error: {str(e)}"
    
    # Fetch history from database (newest first)
    history = Translation.query.order_by(Translation.timestamp.desc()).all()
        
    return render_template('index.html', translated_text=translated_text, original_text=original_text, history=history)

if __name__ == '__main__':
    app.run(debug=True)
