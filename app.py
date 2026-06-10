from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import easyocr
import re
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf2image import convert_from_path


app = Flask(__name__)
app.secret_key = "ruralnest_secret_key_2026"

DATABASE = "ruralnest.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

reader = easyocr.Reader(['en', 'hi'])

# ---------- In-memory data stores (replace with DB in production) ----------
users = {}        # phone -> {name, phone, profile}
appointments = {} # phone -> [list of appointments]
emergencies = []  # list of emergency alerts

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        phone = session.get("phone")

        if not phone:
            return redirect(url_for("login"))

        if phone not in users:
            session.clear()
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated

# ======================= AUTH =======================

@app.route("/", methods=["GET", "POST"])
def login():
    if "phone" in session:
        return redirect(url_for("home"))
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name or len(name) < 2:
            error = "Please enter a valid full name."
        elif not phone or len(phone) < 10:
            error = "Please enter a valid phone number."
        else:
            if phone not in users:
                users[phone] = {
                    "name": name,
                    "phone": phone,
                    "profile": {"name": name, "phone": phone}
                }
                appointments[phone] = [
                    {"service": "Prenatal Check-up", "date": "2026-06-15", "time": "10:00 AM", "location": "Nagpur Rural Camp", "status": "confirmed"},
                    {"service": "Immunization", "date": "2026-06-22", "time": "2:00 PM", "location": "Wardha Block", "status": "pending"},
                ]
            session["phone"] = phone
            session["name"] = users[phone]["name"]
            return redirect(url_for("home"))
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ======================= PAGES =======================

@app.route("/home")
@login_required
def home():
    phone = session.get("phone")

    if phone not in users:
        session.clear()
        return redirect(url_for("login"))

    user = users[phone]
    return render_template("home.html", user=user)

@app.route("/services")
@login_required
def services():
    user = users[session["phone"]]
    return render_template("services.html", user=user)

@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments_page():
    phone = session["phone"]
    user = users[phone]
    success = None
    if request.method == "POST":
        svc = request.form.get("service")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location", "").strip()
        notes = request.form.get("notes", "").strip()
        if svc and date and location:
            appointments[phone].insert(0, {
                "service": svc,
                "date": date,
                "time": time,
                "location": location,
                "notes": notes,
                "status": "confirmed"
            })
            success = f"Appointment for '{svc}' booked on {date} at {time}."
    appt_list = appointments.get(phone, [])
    return render_template("appointments.html", user=user, appointments=appt_list, success=success)

@app.route("/emergency", methods=["GET", "POST"])
@login_required
def emergency():
    user = users[session["phone"]]
    sos_sent = False
    if request.method == "POST":
        alert = {
            "user": user["name"],
            "phone": user["phone"],
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
            "location": request.form.get("location", "Not provided"),
            "message": request.form.get("message", "SOS Alert"),
        }
        emergencies.append(alert)
        sos_sent = True
    return render_template("emergency.html", user=user, sos_sent=sos_sent)

@app.route("/health")
@login_required
def health():
    user = users[session["phone"]]
    return render_template("health.html", user=user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    phone = session["phone"]
    user = users[phone]
    success = None
    if request.method == "POST":
        fields = ["name","dob","aadhaar_number","gender","address","blood_group","edd","pregnancy_status","phone"]
        for f in fields:
            val = request.form.get(f, "").strip()
            if val:
                user["profile"][f] = val
        users[phone] = user
        session["name"] = user["profile"].get("name", user["name"])
        success = "Profile saved successfully!"
    return render_template("profile.html", user=user, profile=user.get("profile", {}), success=success)

# ======================= OCR API =======================

@app.route("/api/ocr", methods=["POST"])
@login_required
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    ext = filename.rsplit(".", 1)[1].lower()

    if ext == "pdf":
        pages = convert_from_path(filepath) 
        image_path = filepath.replace(".pdf", ".jpg")
        pages[0].save(image_path, "JPEG")
        filepath = image_path

    try:
        results = reader.readtext(filepath, detail=0)

        text = " ".join(results)

        aadhaar = re.search(
            r"\b\d{4}\s?\d{4}\s?\d{4}\b",
            text
        )

        dob = re.search(
            r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
            text
        )

        gender = ""

        if "female" in text.lower():
            gender = "Female"
        elif "male" in text.lower():
            gender = "Male"

        name = ""
        address = ""

        for line in results:
            line = line.strip()

            if len(line) < 3:
                continue

            if any(x in line.lower() for x in [
                "government",
                "india",
                "authority",
                "aadhaar",
                "uidai",
                "male",
                "female",
                "dob",
                "year"
            ]):
                continue

            if re.search(r"\d", line):
                continue

            if len(line.split()) >= 2:
                name = line
                break

        for i, line in enumerate(results):
            if "address" in line.lower():
                address = " ".join(results[i:i+5])
                break

        data = {
            "name": name,
            "dob": dob.group(0) if dob else "",
            "aadhaar_number": aadhaar.group(0) if aadhaar else "",
            "gender": gender,
            "address": address
        }

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
