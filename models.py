from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()



#  TABLE 1 – users

class User(db.Model):
    __tablename__ = "users"

    id               = db.Column(db.Integer,     primary_key=True)
    name             = db.Column(db.String(120),  nullable=False)
    phone            = db.Column(db.String(20),   unique=True, nullable=False)

    # Profile fields (filled manually or via Aadhaar OCR)
    dob              = db.Column(db.String(20))       # date of birth
    gender           = db.Column(db.String(20))
    aadhaar_number   = db.Column(db.String(20))
    address          = db.Column(db.Text)
    blood_group      = db.Column(db.String(10))
    edd              = db.Column(db.String(20))       # expected delivery date
    pregnancy_status = db.Column(db.String(60))

    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship("Appointment",    backref="user", lazy=True, cascade="all, delete-orphan")
    emergencies  = db.relationship("Emergency",      backref="user", lazy=True, cascade="all, delete-orphan")
    uploads      = db.relationship("AadhaarUpload",  backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.phone} – {self.name}>"



#  TABLE 2 – appointments

class Appointment(db.Model):
    __tablename__ = "appointments"

    id         = db.Column(db.Integer,     primary_key=True)
    user_id    = db.Column(db.Integer,     db.ForeignKey("users.id"), nullable=False)
    service    = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.String(20),  nullable=False)
    time       = db.Column(db.String(20))
    location   = db.Column(db.String(200))
    notes      = db.Column(db.Text)
    status     = db.Column(db.String(20),  default="confirmed")  # confirmed | pending | cancelled
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment {self.service} on {self.date}>"



#  TABLE 3 – emergencies

class Emergency(db.Model):
    __tablename__ = "emergencies"

    id        = db.Column(db.Integer,     primary_key=True)
    user_id   = db.Column(db.Integer,     db.ForeignKey("users.id"), nullable=False)
    location  = db.Column(db.String(200))
    message   = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Emergency by user_id={self.user_id} at {self.timestamp}>"


#  TABLE 4 – aadhaar_uploads

class AadhaarUpload(db.Model):
    __tablename__ = "aadhaar_uploads"

    id                = db.Column(db.Integer,     primary_key=True)
    user_id           = db.Column(db.Integer,     db.ForeignKey("users.id"), nullable=False)
    filename          = db.Column(db.String(200))

    # Fields extracted by OCR
    extracted_name    = db.Column(db.String(120))
    extracted_dob     = db.Column(db.String(20))
    extracted_gender  = db.Column(db.String(20))
    extracted_aadhaar = db.Column(db.String(20))
    extracted_address = db.Column(db.Text)

    uploaded_at       = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AadhaarUpload {self.filename} for user_id={self.user_id}>"



