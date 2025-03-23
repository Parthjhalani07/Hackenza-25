markdown
# CareSync Documentation

## Overview  
CareSync is a web application facilitating interactions between patients and clinicians, integrating **Flask**, **Google Gemini AI**, and **SQLite** for AI-driven health query responses. The system includes user authentication, patient and clinician management, query processing, and chatbot integration.

## Tech Stack  
- **Backend**: Flask, Flask-CORS, Google Gemini API, SQLAlchemy  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: SQLite (caresync.db)  

---

## Backend  
The backend serves the frontend, handles authentication, processes user queries, and integrates AI-generated responses via **Google Gemini API**.

### Project Structure  
- **app.py**: Main Flask application that serves frontend and handles API requests.
- **model.py**: Handles AI-powered responses via Google Gemini API.
- **database.py**: Defines the database schema and manages SQLite interactions.

### Setup Instructions  
#### Prerequisites  
- Python 3.x  
- Google Gemini API Key  
- SQLite  

#### Install Dependencies  

 ⁠bash
pip install flask flask-cors google-generativeai sqlalchemy


⁠ #### Set API Key  

 ⁠bash
export GEMINI_API_KEY="your_api_key_here"


⁠ #### Running the Backend  

 ⁠bash
python app.py


By default, the server runs on http://127.0.0.1:5000.

### API Endpoints  
•⁠  ⁠*Authentication*  
  - POST /api/login - User login  
  - POST /api/patient/signup - Patient registration  
  - POST /api/clinician/signup - Clinician registration  

•⁠  ⁠*Patient & Clinician Management*  
  - POST /api/patients - Create new patient  
  - GET /api/patients/<patient_id> - Retrieve patient details  
  - POST /api/clinicians - Create new clinician  
  - GET /api/clinicians/<clinician_id> - Retrieve clinician details  

•⁠  ⁠*Query Management*  
  - POST /api/queries - Create new query  
  - GET /api/queries - Retrieve patient queries  
  - POST /api/verify_response - Verify responses  
  - POST /api/edit_response - Edit responses  

•⁠  ⁠*Chat History*  
  - GET /api/chat_history?session_id={session_id} - Retrieve chat history  

•⁠  ⁠*Google Gemini Integration*  
  - AI-powered query processing using *gemini-1.5-flash-latest* model.

---

## Frontend  
The frontend provides a user-friendly interface for patients and clinicians. It is built using *HTML, CSS, and JavaScript*.

### Project Structure  
•⁠  ⁠*HTML Files*:  
  - index.html - Login and Signup  
  - index2.html - Patient Dashboard  
  - index3.html - Clinician Dashboard  
  - history.html - Medical History Questionnaire  
  - verification.html - Clinician Sign-up Verification  

•⁠  ⁠*CSS Files*:  
  - style.css - Login and Signup styling  
  - style2.css - Patient Dashboard styling  
  - style3.css - Clinician Dashboard styling  
  - history.css - Medical History Questionnaire styling  

•⁠  ⁠*JavaScript Files*:  
  - index.js - Handles login/signup toggling  
  - dashboard.js - Manages patient dashboard functionality  
  - clinician.js - Handles clinician dashboard  
  - history.js - Controls multi-step form navigation  

### Key Features  
•⁠  ⁠*Login & Signup*: Separate flows for patients and clinicians.  
•⁠  ⁠*Patient Dashboard*: Query submission and history tracking.  
•⁠  ⁠*Clinician Dashboard*: Query review and verification.  
•⁠  ⁠*Medical History Questionnaire*: Multi-step form with validation.  
•⁠  ⁠*Clinician Verification*: Secure multi-step onboarding process.  
•⁠  ⁠*Accessibility*: Screen reader compatibility, adaptive UI.  

### Backend Integration  
•⁠  ⁠Fetch queries: GET /api/queries?patientId={patientId}  
•⁠  ⁠Submit queries: POST /api/queries  
•⁠  ⁠Verify responses: POST /api/verify_response  
•⁠  ⁠Edit responses: POST /api/edit_response  

---

## Database Schema  
CareSync uses *SQLite* with the following tables:

### *Users Table*  
•⁠  ⁠user_id (Primary Key)  
•⁠  ⁠is_patient (Boolean)  
•⁠  ⁠is_clinician (Boolean)  
•⁠  ⁠is_admin (Boolean)  
•⁠  ⁠password_hash  

### *Patients Table*  
•⁠  ⁠patient_id (Primary Key)  
•⁠  ⁠user_id (Foreign Key)  
•⁠  ⁠full_name, dob, gender, contact details  
•⁠  ⁠*Medical Information*: medical history, medications, allergies, lifestyle, mental health  

### *Clinicians Table*  
•⁠  ⁠clinician_id (Primary Key)  
•⁠  ⁠user_id (Foreign Key)  
•⁠  ⁠full_name, email, phone, specialization, experience  
•⁠  ⁠*Verification*: medical_reg_number, aadhar_number  

### *Chatbot Table*  
•⁠  ⁠chat_id (Primary Key)  
•⁠  ⁠patient_id, clinician_id (Foreign Keys)  
•⁠  ⁠created_at (Timestamp)  

### *Queries Table*  
•⁠  ⁠query_id (Primary Key)  
•⁠  ⁠chat_id (Foreign Key)  
•⁠  ⁠patient_id, clinician_id (Foreign Keys)  
•⁠  ⁠query_text, response, query_status, created_at  

---

## Access Control  
CareSync implements role-based access control (RBAC) to manage user permissions:

### *Admin*  
•⁠  ⁠*Access*: Full access to all functionalities, including patient and clinician management, query history, and system settings.  
•⁠  ⁠*Permissions*:  
  - Create, read, update, and delete patients and clinicians.  
  - View all queries and responses.  
  - Manage system configurations.  

### *Clinician*  
•⁠  ⁠*Access*: Access to patient history, patient queries, and responses.  
•⁠  ⁠*Permissions*:  
  - View and respond to patient queries.  
  - Verify and edit responses.  
  - Access patient medical history.  

### *Patient*  
•⁠  ⁠*Access*: Access to their own queries and responses.  
•⁠  ⁠*Permissions*:  
  - Submit new queries.  
  - View responses from clinicians.  
  - Access their own medical history.  

---
