from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Define the 'Persona'
config = types.GenerateContentConfig(
    system_instruction="You are a salty sea captain from the 1700s. Translate everything the user says into pirate speak. Keep it brief and gritty."
)

# 3. Get user input
user_text = input("What do you want to say to the captain? ")

# 4. Generate the response
response = client.models.generate_content(
    model="gemini-2.0-flash-lite",
    config=config,
    contents=user_text
)

print(f"\nCaptain says: {response.text}")