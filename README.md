# RuralNest – Mobile Maternal Healthcare Platform

## Overview

RuralNest is a digital healthcare platform designed to improve maternal healthcare accessibility in rural and underserved communities.

The system combines a Mobile Maternal Healthcare Unit with a web-based platform that enables women to:

* Register and manage healthcare profiles
* Auto-fill details using Aadhaar OCR
* Book healthcare appointments
* Request emergency support
* Access maternal healthcare information

The project aims to reduce barriers to healthcare access and improve maternal well-being through technology-enabled healthcare services.

## Features

### Aadhaar OCR Auto-Fill

* Upload Aadhaar card image or PDF
* Extracts Name, Aadhaar Number, DOB, Gender, and Address
* Uses EasyOCR for local processing
* No API key required

### User Profile Management

* Digital healthcare profile creation
* Editable personal and maternal health information
* Persistent storage using SQLite

### Appointment Booking

* Schedule healthcare appointments
* View upcoming healthcare services
* Store appointment records

### Emergency Support

* Submit emergency alerts
* Record emergency requests with timestamps
* Foundation for future ambulance integration

### Health Awareness

* Maternal healthcare information
* Preventive healthcare guidance
* Pregnancy care awareness


## Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### OCR

* EasyOCR
* Regex-based field extraction

### Database

* SQLite

### Development Tools

* Git
* GitHub
* Werkzeug


## System Architecture

Browser
↓
Flask Backend
↓
Jinja2 Templates (HTML/CSS/JS)
↓
EasyOCR Engine
↓
SQLite Database

## Current Limitations

* Emergency alerts are not connected to real ambulance services.
* OCR accuracy depends on image quality.
* GPS tracking is not yet implemented.
* SMS/WhatsApp notifications are not integrated.
* Prototype currently supports local deployment.


## Future Enhancements

* GPS-enabled ambulance tracking
* SMS and WhatsApp notifications
* Healthcare worker dashboard
* Cloud deployment
* Analytics and reporting
* AI-assisted maternal risk prediction


## Social Impact

RuralNest aims to bridge the healthcare accessibility gap in rural communities by providing digital support and mobile healthcare services for pregnant women. The platform focuses on improving maternal healthcare outcomes through timely intervention, easy registration, and emergency support.

## Developed For

TechForGood Internship Program 2026

Project Title:
**RuralNest – Mobile Maternal Healthcare Unit with Smart Emergency Support**
