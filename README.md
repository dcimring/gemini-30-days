# 🏴‍☠️ Pirate Translator App

Ahoy, matey! Welcome aboard the **Pirate Translator**, a Flask-based web application that turns your landlubber talk into gritty pirate speak using the power of Google's **Gemini 2.0 Flash** AI model.

Not only can you translate text, but you can also show the Captain a map (upload an image), and he'll describe what he sees with his salty sea-dog eyes!

## ✨ Features

*   **🗣️ Text-to-Pirate Translation:** Type in any phrase, and get it back in authentic pirate slang.
*   **🖼️ Image Analysis:** Upload an image, and the AI Captain will describe the scene in pirate speak.
*   **🔐 User Authentication:** Secure Signup and Login system so every pirate has their own bunk.
*   **📜 History Log:** Keeps a personal log of all your past translations.
*   **🎨 Thematic UI:** A fully styled "parchment and wood" interface that feels like you're in the Captain's quarters.
*   **📱 Mobile Friendly:** Works on your desktop spyglass or your mobile compass.

## 🛠️ Tech Stack

*   **Backend:** Python 3.12, Flask
*   **Database:** SQLite, SQLAlchemy
*   **Authentication:** Flask-Login, Werkzeug Security
*   **AI Model:** Google Gemini 2.0 Flash (via `google-genai` SDK)
*   **Image Processing:** Pillow (PIL)
*   **Frontend:** HTML5, CSS3 (Custom Pirate Theme)

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

5.  **Initialize the Database:**
    Run the initialization script to create the user and translation tables.
    ```bash
    python init_db.py
    ```

6.  **Run the App:**
    ```bash
    python app.py
    ```

7.  **Board the Ship:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## 📖 Usage

1.  **Sign Up:** Create a new pirate alias and secret code.
2.  **Login:** Enter your credentials to access the translator.
3.  **Translate Text:** Type "Hello, how are you?" and click translate to get "Ahoy! How fare ye, matey?"
4.  **Upload Image:** Click the upload box to select an image. The Captain will tell you what's happening in the picture!

## 🧪 Running Tests

To test the authentication flows:
```bash
python test_auth.py
```

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Any contribution that makes the ship faster or the grog tastier is welcome!

## 📄 License

This project is open-source. Use it to sail the seven seas of code!