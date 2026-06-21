from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import easyocr
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf2image import convert_from_path
from models import db, User, Appointment, Emergency, AadhaarUpload 


app = Flask(__name__)
app.secret_key = "ruralnest_secret_key_2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ruralnest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

reader = easyocr.Reader(['en', 'hi'])



def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        user = User.query.get(session["user_id"])

        if not user:
            session.clear()
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated

# ======================= AUTH =======================

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
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
            user = User.query.filter_by(phone=phone).first()

            if not user:
                user = User(
                    name=name,
                    phone=phone
                )

                db.session.add(user)
                db.session.commit()

            session["user_id"] = user.id
            session["name"] = user.name
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
    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("login"))
    return render_template("home.html", user=user)

@app.route("/services")
@login_required
def services():
    user = User.query.get(session["user_id"])
    return render_template("services.html", user=user) 

@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments_page():

    user = User.query.get(session["user_id"])

    success = None

    if request.method == "POST":

        appointment = Appointment(
            user_id=user.id,
            service=request.form.get("service"),
            date=request.form.get("date"),
            time=request.form.get("time"),
            location=request.form.get("location"),
            notes=request.form.get("notes")
        )

        db.session.add(appointment)
        db.session.commit()

        success = "Appointment booked successfully."

    appt_list = Appointment.query.filter_by(
    user_id=user.id
    ).order_by(Appointment.id.desc()).all()

    return render_template(
        "appointments.html",
        user=user,
        appointments=appt_list,
        success=success
    )

@app.route("/emergency", methods=["GET", "POST"])
@login_required
def emergency():

    user = User.query.get(session["user_id"])

    sos_sent = False

    if request.method == "POST":

        message = request.form.get(
            "message",
            "SOS Emergency Alert"
        )

        emergency = Emergency(
            user_id=user.id,
            location="Not Provided",
            message=message
        )

        db.session.add(emergency)
        db.session.commit()

        sos_sent = True

    return render_template(
        "emergency.html",
        user=user,
        sos_sent=sos_sent
    )

@app.route("/health")
@login_required
def health():
    user = User.query.get(session["user_id"])
    return render_template("health.html", user=user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    user = User.query.get(session["user_id"])

    success = None

    if request.method == "POST":

        user.name = request.form.get("name")
        user.dob = request.form.get("dob")
        user.aadhaar_number = request.form.get("aadhaar_number")
        user.gender = request.form.get("gender")
        user.address = request.form.get("address")
        user.phone = request.form.get("phone")
        user.blood_group = request.form.get("blood_group")
        user.edd = request.form.get("edd")
        user.pregnancy_status = request.form.get("pregnancy_status")

        db.session.commit()

        session["name"] = user.name

        success = "Profile saved successfully!"

    return render_template(
        "profile.html",
        user=user,
        profile=user,
        success=success
    )
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
        user = User.query.get(session["user_id"])

        upload = AadhaarUpload(
            user_id=user.id,
            filename=filename,
            extracted_name=data["name"],
            extracted_dob=data["dob"],
            extracted_gender=data["gender"],
            extracted_aadhaar=data["aadhaar_number"],
            extracted_address=data["address"]
        )

        print("Saving upload...")
        db.session.add(upload)
        db.session.commit()
        print("Upload saved")

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

    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000) 
