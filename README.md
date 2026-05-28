# KisaanSuvida — Smart Crop Recommendation System

A comprehensive agricultural support web application that helps Indian farmers make informed crop decisions using a **Hybrid Prediction Engine** combining Machine Learning with regional heuristics.

---

##  Features

- **ML-Powered Crop Recommendation** — Trained Random Forest model on soil & weather parameters
- **Regional Heuristics** — Validates ML output against state, season, and soil-type rules
- **Live Weather Integration** — Fetches real-time data via OpenWeatherMap API
- **OTP Authentication** — Twilio-based SMS OTP for secure user registration
- **Bilingual Support** — Full English & Hindi interface
- **Crop Suitability Analysis** — Day-by-day feasibility analysis for a chosen crop
- **User History** — Logs all past recommendations and analyses per user
- **Support Portal** — Contact form with Gmail SMTP integration

---

##  Architecture

```
KisaanSuvida/
├── app.py                    # Main Flask app — routes, business logic
├── crop_data.py              # Data dictionaries, regional rules, helper functions
├── trained_model.py          # Script to retrain model.pkl from scratch
├── model.pkl                 # Pre-trained Scikit-Learn RandomForest model
│
├── users.csv                 # User credentials store (header only — data not committed)
├── user details/             # Per-user history CSVs (gitignored)
│
├── templates/                # Jinja2 HTML templates
│   ├── login.html            # Login & Signup
│   ├── language.html         # Language selection
│   ├── choose.html           # Choose action (recommend / analyse)
│   ├── crop.html             # Crop recommendation form
│   ├── analysis.html         # Crop suitability analysis form
│   ├── status.html           # Recommendation results
│   ├── history.html          # User activity log
│   ├── schemes.html          # Government schemes info
│   ├── support.html          # Support/contact form
│   └── crop_error.html       # Error page
│
├── crop_conditions.json      # Crop-specific growing conditions
├── seasonal_rainfall.json    # Seasonal rainfall data by state
├── state_crops.json          # Crops grown per state
├── states-and-districts.json # India states & districts data
│
├── database/
│   └── kisan_schema.sql      # SQL schema for future DB migration
│
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
└── system_design.md          # Detailed system design document
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/KisaanSuvida.git
cd KisaanSuvida
```

### 2. Create a virtual environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in all the required keys (see [Environment Variables](#-environment-variables) below).

### 5. Run the app
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Environment Variables

| Variable | Description | Where to get it |
|---|---|---|
| `SECRET_KEY` | Flask session secret key | Generate a random string |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | [Twilio Console](https://console.twilio.com) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | [Twilio Console](https://console.twilio.com) |
| `TWILIO_PHONE_NUMBER` | Twilio sender phone number | [Twilio Console](https://console.twilio.com) |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | [openweathermap.org/api](https://openweathermap.org/api) |
| `MAIL_USERNAME` | Gmail address for support emails | Your Gmail account |
| `MAIL_PASSWORD` | Gmail App Password | [Google App Passwords](https://support.google.com/accounts/answer/185833) |

---

##  Retraining the ML Model

If you want to retrain the model on the included dataset:

```bash
python trained_model.py
```

This reads `Crop_recommendation.csv`, trains a `RandomForestClassifier`, and saves `model.pkl`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML | Scikit-Learn, NumPy, Pandas |
| Frontend | HTML5, CSS3, JavaScript, Jinja2 |
| SMS/OTP | Twilio |
| Weather | OpenWeatherMap API |
| Email | Flask-Mail (Gmail SMTP) |
| Storage | CSV-based file system |

---

##  Known Limitations & Future Improvements

- **Database**: Currently uses CSV files. Migration to PostgreSQL/MySQL with SQLAlchemy is recommended for production.
- **Password Hashing**: Implement `bcrypt` or `werkzeug.security` for proper password security.
- **Concurrency**: CSV-based storage is not thread-safe under high traffic.
- **model.pkl**: Large binary file (~7MB). Consider storing it in [Git LFS](https://git-lfs.github.com/) or as a GitHub Release asset.

See `system_design.md` for full architectural details.

---

## 📄 License

This project is open source. Feel free to use and modify it.
