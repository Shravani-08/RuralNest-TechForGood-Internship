# RuralNest – Mobile Maternal Healthcare Unit

## Project Structure
```
ruralnest/
├── app.py                  ← Flask application
├── requirements.txt
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/            ← Aadhaar uploads saved here
└── templates/
    ├── base.html            ← Shared nav + layout
    ├── login.html
    ├── home.html
    ├── services.html
    ├── appointments.html
    ├── emergency.html
    ├── health.html
    └── profile.html
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Anthropic API key (for Aadhaar OCR)
```bash
# Linux/Mac
export ANTHROPIC_API_KEY=your_api_key_here

# Windows
set ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run
```bash
python app.py
```

Visit: http://localhost:5000

## Features
- **Login** – Name + phone number (no OTP, no registration)
- **Home** – Hero, pillars, stats, about section
- **Services** – 6 maternal health services
- **Appointments** – Book + view appointments
- **Emergency** – SOS button, helplines, warning signs
- **Health Awareness** – Trimester guide, nutrition, newborn care, hygiene
- **Profile** – Upload Aadhaar (JPG/PNG/PDF), OCR auto-fills name/DOB/address/Aadhaar number

## Notes
- Data is stored in-memory (restart clears it). For production, replace `users` / `appointments` dicts with a database (SQLite/PostgreSQL).
- OCR uses Claude claude-opus-4-5 vision via the Anthropic API.
- Uploaded files are saved to `static/uploads/`.
