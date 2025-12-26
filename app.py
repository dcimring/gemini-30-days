from flask import Flask, render_template, request
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
            except Exception as e:
                translated_text = f"Arrr! The winds be against us. Error: {str(e)}"
        
    return render_template('index.html', translated_text=translated_text, original_text=original_text)

if __name__ == '__main__':
    app.run(debug=True)