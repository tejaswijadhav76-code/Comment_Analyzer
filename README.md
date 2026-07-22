# Sentiment IQ 🧠 - AI-Powered Comment & Feedback Analyzer

Sentiment IQ is a modern, responsive Django web application designed to analyze the sentiment of user comments, product feedback, or reviews. It provides automated classification of feedback into positive, negative, and neutral categories, extracts key actionable suggestions, and delivers a clean dashboard for visual insights.

The application leverages state-of-the-art **Google Gemini GenAI models** to provide structured, deep-dive semantic analysis and automatically switches to a **local NLP fallback engine (TextBlob / Heuristics)** if the API key is missing or rate limits are reached.

---

## 🌟 Key Features

- **Dual-Engine Architecture**: 
  - **Gemini AI Engine**: Utilizes Google's Gemini models (`gemini-2.5-flash`, `gemini-2.0-flash`) to generate structured JSON output with sentiment metrics, reasoning, and key product suggestions.
  - **Local NLP Fallback**: Uses `TextBlob` and rule-based keyword heuristics to analyze polarity locally when offline or when API limits are hit.
- **Premium User Interface**:
  - Styled with a high-fidelity glassmorphic dark theme, leveraging custom CSS, smooth hover transitions, and visual feedback cards.
  - Interactive sample preset buttons to quickly load dummy reviews for instant testing.
  - Interactive distribution bar charts showing percentages of positive, negative, and neutral comments.
- **Actionable AI Advice**: Summarizes recommendations, requested features, or pain points detected in the feedback block.
- **Robust Error Handling**: Displays clear status notices when falling back to the local engine due to rate limits or missing credentials.

---

## 📁 Project Structure

```
├── app/                      # Django App Directory
│   ├── templates/app/        # HTML Templates (home.html with responsive layout)
│   ├── views.py              # Sentiment analysis orchestration & API integrations
│   ├── models.py             # App models
│   ├── apps.py               # App config
│   └── tests.py              # Test cases
├── commentanlyz/             # Django Project Configuration
│   ├── settings.py           # Core settings (apps, DB, middleware)
│   ├── urls.py               # URL routing configuration
│   ├── wsgi.py / asgi.py     # Deployment entrypoints
├── project/                  # Python virtual environment (ignored in git)
├── db.sqlite3                # Local development database
├── manage.py                 # Django command-line execution utility
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚙️ Getting Started & Setup

Follow these instructions to set up and run the project locally on your machine.

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Activate the Virtual Environment
Activate the pre-configured virtual environment in the `project/` directory:
- **Windows (PowerShell)**:
  ```powershell
  .\project\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  project\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source project/bin/activate
  ```

### 3. Install Dependencies
Install all required libraries using the package manager `pip`:
```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key
To use the primary AI analyzer, obtain an API key from Google AI Studio and configure the environment variable:
- **Windows (PowerShell)**:
  ```powershell
  $env:GEMINI_API_KEY="your-api-key-here"
  ```
- **Windows (Command Prompt)**:
  ```cmd
  set GEMINI_API_KEY=your-api-key-here
  ```
- **macOS / Linux**:
  ```bash
  export GEMINI_API_KEY="your-api-key-here"
  ```

*Note: If no API key is set, the application will run, but it will automatically default to the local TextBlob NLP fallback engine and display a banner notice.*

### 5. Initialize the Database (Migrations)
Apply database migrations to set up the default sqlite structure:
```bash
python manage.py migrate
```

### 6. Run the Development Server
Start the local Django server:
```bash
python manage.py runserver
```
Once started, open your web browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🛠️ Technology Stack

- **Backend Framework**: [Django 6.0.7](https://www.djangoproject.com/)
- **AI / NLP Libraries**: 
  - [Google Generative AI SDK](https://pypi.org/project/google-generativeai/) (`google-generativeai`)
  - [TextBlob](https://textblob.readthedocs.io/)
- **Frontend / Styling**: 
  - Standard HTML5 & Semantic Elements
  - Vanilla CSS with CSS Custom Properties (Variables), Flexbox, Grid, and Glassmorphism
  - Google Fonts (Inter)
