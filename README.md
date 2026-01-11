# 🏴‍☠️ Pirate App - Gemini Series

Ahoy, matey! Welcome aboard the **Pirate App**, a Flask-based web application that evolves daily, showcasing the power of Google's **Gemini** AI models. What started as a simple translator has become a multi-featured AI-powered application.

## ✨ Features

*   **🗣️ Real-time Pirate Chat:** Type in any phrase and get a streamed response back in authentic pirate slang.
*   **🎭 Dynamic Personas:** Switch between a "Friendly" and "Grumpy" pirate AI on the fly, powered by dynamic system instructions.
*   **🧠 Google Search Grounding:** Ask about real-world news or make a historical claim! The pirate can now use Google Search to find information and fact-check, and will show its sources.
*   **🖼️ Image Analysis:** Upload an image, and the AI Captain will describe the scene in pirate speak.
*   **🔐 User Authentication:** Secure Signup and Login system so every pirate has their own bunk.
*   **📜 History Log:** Keeps a personal log of all your past conversations.
*   **🎨 Thematic UI:** A fully styled "parchment and wood" interface that feels like you're in the Captain's quarters.
*   **📱 Mobile Friendly:** Works on your desktop spyglass or your mobile compass.

### Day 16: Google Search Grounding & Fact-Checking
- **System Instruction Update:** The pirate personas are now encouraged to use Google Search to look up real-world news or fact-check historical claims.
- **Tool Integration:** The backend now includes the `GoogleSearch` tool in its calls to the Gemini API.
- **Source Citing:** The UI now displays clickable "chips" showing the web sources the AI used for its response, thanks to processing the `grounding_metadata` from the API.

### Day 13: Dynamic Personas
- **Centralized Config:** Created a `pirate_config.py` to manage different AI personalities.
- **UI Toggle:** Added a switch to the chat interface to dynamically change the `system_instruction` between "Friendly" and "Grumpy" modes for each message.

## 🛠️ Tech Stack

*   **Backend:** Python 3.12, Flask, Flask-SocketIO
*   **AI Model:** Google Gemini 2.0 Flash (via `google-genai` SDK)
*   **Tools:** Google Search (Grounding)
*   **Database:** SQLite, SQLAlchemy
*   **Authentication:** Flask-Login, Werkzeug Security
*   **Frontend:** HTML5, CSS3, JavaScript

## 🚀 Getting Started

Follow these steps to get the ship sailing on your local machine.

### Prerequisites

*   Python 3.12+
*   A Google Cloud Project with the **Gemini API** enabled.
*   An API Key from Google AI Studio.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dcimring/gemini-30-days.git
    cd gemini-30-days
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API key and a secret key for sessions:
    ```ini
    GEMINI_API_KEY=your_actual_api_key_here
    SECRET_KEY=your_random_secret_string
    ```

5.  **Run the App:**
    ```bash
    python app.py
    ```

6.  **Board the Ship:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## 📖 Usage

1.  **Sign Up:** Create a new pirate alias and secret code.
2.  **Login:** Enter your credentials to access the chat.
3.  **Select a Persona:** Use the toggle to switch between the Friendly and Grumpy pirate.
4.  **Chat:** Type a message. Ask about the news or state a "fact" about pirates to test the new search and fact-checking abilities.
5.  **Check Sources:** Look for the `🔗` source links that appear below grounded responses.

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Any contribution that makes the ship faster or the grog tastier is welcome!

## 📄 License

This project is open-source. Use it to sail the seven seas of code!
