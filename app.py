from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import signal
import sys
import os
import google.generativeai as genai
from flask_cors import CORS
from sqlalchemy import inspect 

def shutdown_handler(signum, frame):
    print("\nShutting down server...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure PostgreSQL database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'caresync.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure the Gemini API (place this outside routes)
def initialize_gemini():
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return False

# Function to generate AI responses
def get_response_from_llm(query, patient_info=None):
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Create a context-aware prompt with patient information if available
        prompt = "You are a medical assistant. Provide helpful and safe responses."
        if patient_info:
            prompt += f"\nPatient context: {patient_info}"
        prompt += f"\nUser query: {query}"
        
        # Generate a response
        response = model.generate_content(prompt)
        
        # Check if response was blocked
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
            return "Sorry, I cannot provide a response to that query due to safety concerns."
        
        return response.text
    except Exception as e:
        print(f"LLM Error: {e}")
        return f"I apologize, but I'm having trouble generating a response right now. Please try again later."




# Define Models (Tables)
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_patient = db.Column(db.Boolean, nullable=False)
    is_clinician = db.Column(db.Boolean, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255), unique=True)
    aadhar_number = db.Column(db.String(20), unique=True)
    diabetes = db.Column(db.Boolean, default=False)
    hypertension = db.Column(db.Boolean, default=False)
    heart_disease = db.Column(db.Boolean, default=False)
    asthma = db.Column(db.Boolean, default=False)
    stroke = db.Column(db.Boolean, default=False)
    other_conditions = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    no_allergies = db.Column(db.Boolean, default=False)
    medication_allergies = db.Column(db.Text)
    food_allergies = db.Column(db.Text)
    environmental_allergies = db.Column(db.Text)
    family_diabetes = db.Column(db.Text)
    family_heart_disease = db.Column(db.Text)
    family_stroke = db.Column(db.Text)
    family_cancer = db.Column(db.Text)
    family_mental_health = db.Column(db.Text)
    smoking_status = db.Column(db.String(20))
    alcohol_use = db.Column(db.String(20))
    exercise_frequency = db.Column(db.String(20))
    diet = db.Column(db.String(20))
    anxiety = db.Column(db.Boolean, default=False)
    depression = db.Column(db.Boolean, default=False)
    ptsd = db.Column(db.Boolean, default=False)
    adhd = db.Column(db.Boolean, default=False)
    bipolar = db.Column(db.Boolean, default=False)
    other_mental_health = db.Column(db.Text)
    additional_info = db.Column(db.Text)

class Clinician(db.Model):
    __tablename__ = 'clinicians'
    clinician_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    medical_reg_number = db.Column(db.String(50), unique=True, nullable=False)
    specialization = db.Column(db.Text, nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    affiliated_hospitals = db.Column(db.Text)
    aadhar_number = db.Column(db.String(20), unique=True, nullable=False)

class Chatbot(db.Model):
    __tablename__ = 'chatbot'
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id', ondelete='CASCADE'))
    clinician_id = db.Column(db.Integer, db.ForeignKey('clinicians.clinician_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Query(db.Model):
    __tablename__ = 'queries'
    query_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chatbot.chat_id', ondelete='CASCADE'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id', ondelete='CASCADE'))
    clinician_id = db.Column(db.Integer, db.ForeignKey('clinicians.clinician_id', ondelete='SET NULL'))
    query_text = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    query_status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create Tables
# After all model definitions but before route definitions
def init_db():
    try:
        with app.app_context():
            print("Starting database initialization...")
            db.create_all()
            
            # Verify tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Successfully created tables: {tables}")
            
            if not tables:
                raise Exception("No tables were created")
                
            return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False



# Routes to serve HTML templates
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/verification')
def verification():
    return render_template('verification.html')

@app.route('/patient_dashboard')
def patient_dashboard():
    return render_template('index2.html')


@app.route('/clinician_dashboard')
def clinician_dashboard():
    # Example medical history data
    medical_history = {
        'fullName': 'John Doe',
        'dob': '1990-01-01',
        'gender': 'Male',
        'height': '175',
        'weight': '70',
        'conditions': 'Hypertension, Diabetes',
        'medications': 'Metformin, Lisinopril',
        'allergies': 'None',
        'familyHistory': 'Father: Diabetes, Mother: Hypertension',
        'lifestyle': 'Non-smoker, Occasional alcohol',
        'mentalHealth': 'None',
        'additionalInfo': 'None'
    }
    return render_template('index3.html', medical_history=medical_history)


# API routes for authentication
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    # Check if we're getting email or userId
    email = data.get('email')
    user_id = data.get('userId')
    password = data.get('password')
    
    user = None
    
    # First, try to find user by email (checking in Patient or Clinician tables)
    if email:
        # Try patient first
        patient = Patient.query.filter_by(email=email).first()
        if patient:
            user = User.query.filter_by(user_id=patient.user_id).first()
        
        # If not found in patients, try clinicians
        if not user:
            clinician = Clinician.query.filter_by(email=email).first()
            if clinician:
                user = User.query.filter_by(user_id=clinician.user_id).first()
    
    # If not found by email or no email provided, try user_id
    if not user and user_id is not None:
        # Convert user_id to int if it's a string
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)
            
        user = User.query.filter_by(user_id=user_id).first()
    
    # Check credentials and return appropriate response
    if user and user.password_hash == password:  # In production, use proper password hashing
        if user.is_patient:
            patient = Patient.query.filter_by(user_id=user.user_id).first()
            return jsonify({
                "success": True, 
                "is_patient": True, 
                "patient_id": patient.patient_id,
                "full_name": patient.full_name,
                "user_id": user.user_id
            })
        elif user.is_clinician:
            clinician = Clinician.query.filter_by(user_id=user.user_id).first()
            return jsonify({
                "success": True, 
                "is_clinician": True, 
                "clinician_id": clinician.clinician_id,
                "full_name": clinician.full_name,
                "user_id": user.user_id
            })
    
    # Debug info
    print(f"Login attempt - Email: {email}, UserID: {user_id}, User found: {user is not None}")
    
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

#Add a new endpoint to handle AI queries
@app.route('/api/ai_query', methods=['POST'])
def ai_query():
    try:
        data = request.json
        if not data or 'query_text' not in data:
            return jsonify({"success": False, "message": "Invalid request data"}), 400

        query_text = data.get('query_text')
        patient_id = data.get('patient_id')

        # Get patient information for context
        patient_context = None
        if patient_id:
            patient = Patient.query.get(patient_id)
            if patient:
                patient_context = f"Patient: {patient.full_name}, {patient.gender}, Age: {datetime.now().year - patient.dob.year}."

        # Generate AI response
        response = get_response_from_llm(query_text, patient_context)

        # Save the query to the database
        chat_id = data.get('chat_id')
        if not chat_id:
            new_chat = Chatbot(patient_id=patient_id)
            db.session.add(new_chat)
            db.session.commit()
            chat_id = new_chat.chat_id

        new_query = Query(
            chat_id=chat_id,
            patient_id=patient_id,
            query_text=query_text,
            response=response,
            query_status='Pending'
        )
        db.session.add(new_query)
        db.session.commit()

        return jsonify({
            "success": True,
            "response": response,
            "query_id": new_query.query_id,
            "chat_id": chat_id
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error in ai_query: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

# API routes for patient signup
@app.route('/api/patient/signup', methods=['POST'])
def patient_signup():
    try:
        data = request.form  # If using form data
        # data = request.json  # If using JSON data
        
        print("Received signup data:", data)  # Debug log
        
        # Create user first
        new_user = User(
            is_patient=True,
            is_clinician=False,
            password_hash=data.get('password')
        )
        db.session.add(new_user)
        db.session.flush()  # Get the user_id before committing
        
        # Create patient
        new_patient = Patient(
            user_id=new_user.user_id,
            full_name=data.get('fullName'),
            dob=datetime.strptime(data.get('dob'), '%Y-%m-%d').date(),
            gender=data.get('gender'),
            height=data.get('height'),
            weight=data.get('weight'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        db.session.add(new_patient)
        db.session.commit()
        
        print(f"Successfully created patient with ID: {new_patient.patient_id}")  # Debug log
        return jsonify({"success": True, "patient_id": new_patient.patient_id})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in patient_signup: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

# # API routes for clinician signup
@app.route('/api/clinician/signup', methods=['POST'])
def clinician_signup():
    data = request.json
    
    try:
        # Create a new user
        new_user = User(
            is_patient=False,
            is_clinician=True,
            password_hash=data.get('password')
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Create a new clinician according to your actual model schema
        new_clinician = Clinician(
            user_id=new_user.user_id,
            full_name=f"{data.get('firstName', '')} {data.get('lastName', '')}",
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            password_hash=data.get('password'),
            medical_reg_number=data.get('medicalRegNumber', ''),
            specialization=data.get('specialization', ''),
            years_of_experience=int(data.get('yearsOfExperience', 0)),
            affiliated_hospitals=data.get('affiliatedHospitals', ''),
            aadhar_number=data.get('aadharNumber', '')
        )
        db.session.add(new_clinician)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Clinician registered successfully", 
            "clinician_id": new_clinician.clinician_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error during registration: {str(e)}"}), 500

    

# API routes for chat functionality
@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('session_id')
    # For demo purposes, return mock data
    mock_history = [
        {
            "role": "user",
            "parts": [{"text": "I've been having severe headaches lately, what could it be?"}]
        },
        {
            "role": "assistant",
            "parts": [{"text": "Headaches can be caused by various factors including stress, dehydration, lack of sleep, eye strain, or more serious conditions. If the headaches are severe or persistent, it's important to consult with a healthcare professional for proper diagnosis. In the meantime, ensure you're staying hydrated, getting adequate rest, and managing stress levels."}]
        },
        {
            "role": "user",
            "parts": [{"text": "What medications can help with migraines?"}]
        },
        {
            "role": "assistant", 
            "parts": [{"text": "Common medications for migraines include over-the-counter pain relievers like ibuprofen or aspirin, triptans (such as sumatriptan), anti-nausea medications, and preventive medications for those with frequent migraines. It's important to consult with a healthcare provider before starting any medication regimen for proper diagnosis and personalized treatment."}]
        }
    ]
    return jsonify({"history": mock_history})

@app.route('/api/verify_response', methods=['POST'])
def verify_response():
    data = request.json
    response = data.get('response')
    # In a real app, save the verified response to database
    return jsonify({"success": True})

@app.route('/api/edit_response', methods=['POST'])
def edit_response():
    data = request.json
    response = data.get('response')
    # In a real app, save the edited response to database
    return jsonify({"success": True})

# API routes for patient query history
@app.route('/api/queries', methods=['GET'])
def get_patient_queries():
    patient_id = request.args.get('patientId')
    
    if not patient_id:
        return jsonify({"error": "Patient ID required"}), 400
    
    queries = Query.query.filter_by(patient_id=patient_id).all()
    
    result = []
    for query in queries:
        result.append({
            "query_id": query.query_id,
            "query_text": query.query_text,
            "response": query.response,
            "status": query.query_status,
            "created_at": query.created_at.isoformat()
        })
    
    return jsonify(result)


# Routes for Patients
@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.json

    try:
        # Create a new user (if not already created)
        new_user = User(
            is_patient=True,
            is_clinician=False,
            password_hash=data.get('password')  # Ensure password is hashed in production
        )
        db.session.add(new_user)
        db.session.commit()

        # Create a new patient with all fields
        new_patient = Patient(
            user_id=new_user.user_id,
            full_name=data.get('full_name'),
            dob=datetime.strptime(data.get('dob'), '%Y-%m-%d').date(),
            gender=data.get('gender'),
            height=data.get('height'),
            weight=data.get('weight'),
            phone=data.get('phone'),
            email=data.get('email'),
            aadhar_number=data.get('aadhar_number'),
            diabetes=data.get('diabetes', False),
            hypertension=data.get('hypertension', False),
            heart_disease=data.get('heart_disease', False),
            asthma=data.get('asthma', False),
            stroke=data.get('stroke', False),
            other_conditions=data.get('other_conditions'),
            current_medications=data.get('current_medications'),
            no_allergies=data.get('no_allergies', False),
            medication_allergies=data.get('medication_allergies'),
            food_allergies=data.get('food_allergies'),
            environmental_allergies=data.get('environmental_allergies'),
            family_diabetes=data.get('family_diabetes'),
            family_heart_disease=data.get('family_heart_disease'),
            family_stroke=data.get('family_stroke'),
            family_cancer=data.get('family_cancer'),
            family_mental_health=data.get('family_mental_health'),
            smoking_status=data.get('smoking_status'),
            alcohol_use=data.get('alcohol_use'),
            exercise_frequency=data.get('exercise_frequency'),
            diet=data.get('diet'),
            anxiety=data.get('anxiety', False),
            depression=data.get('depression', False),
            ptsd=data.get('ptsd', False),
            adhd=data.get('adhd', False),
            bipolar=data.get('bipolar', False),
            other_mental_health=data.get('other_mental_health'),
            additional_info=data.get('additional_info')
        )
        db.session.add(new_patient)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Patient created successfully",
            "patient_id": new_patient.patient_id,
            "user_id": new_user.user_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error during patient creation: {str(e)}"
        }), 500

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        "patient_id": patient.patient_id,
        "full_name": patient.full_name,
        "dob": patient.dob.isoformat(),
        "gender": patient.gender,
        "height": patient.height,
        "weight": patient.weight,
        "phone": patient.phone,
        "email": patient.email,
        "aadhar_number": patient.aadhar_number,
        "diabetes": patient.diabetes,
        "hypertension": patient.hypertension,
        "heart_disease": patient.heart_disease,
        "asthma": patient.asthma,
        "stroke": patient.stroke,
        "other_conditions": patient.other_conditions,
        "current_medications": patient.current_medications,
        "no_allergies": patient.no_allergies,
        "medication_allergies": patient.medication_allergies,
        "food_allergies": patient.food_allergies,
        "environmental_allergies": patient.environmental_allergies,
        "family_diabetes": patient.family_diabetes,
        "family_heart_disease": patient.family_heart_disease,
        "family_stroke": patient.family_stroke,
        "family_cancer": patient.family_cancer,
        "family_mental_health": patient.family_mental_health,
        "smoking_status": patient.smoking_status,
        "alcohol_use": patient.alcohol_use,
        "exercise_frequency": patient.exercise_frequency,
        "diet": patient.diet,
        "anxiety": patient.anxiety,
        "depression": patient.depression,
        "ptsd": patient.ptsd,
        "adhd": patient.adhd,
        "bipolar": patient.bipolar,
        "other_mental_health": patient.other_mental_health,
        "additional_info": patient.additional_info
    })

# Routes for Clinicians
@app.route('/api/clinicians', methods=['POST'])
def create_clinician():
    data = request.json

    try:
        # Create a new user (if not already created)
        new_user = User(
            is_patient=False,
            is_clinician=True,
            password_hash=data.get('password')  # Ensure password is hashed in production
        )
        db.session.add(new_user)
        db.session.commit()

        # Create a new clinician with all fields
        new_clinician = Clinician(
            user_id=new_user.user_id,
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password_hash=data.get('password'),  # Ensure password is hashed in production
            medical_reg_number=data.get('medical_reg_number'),
            specialization=data.get('specialization'),
            years_of_experience=int(data.get('years_of_experience', 0)),
            affiliated_hospitals=data.get('affiliated_hospitals'),
            aadhar_number=data.get('aadhar_number')
        )
        db.session.add(new_clinician)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Clinician created successfully",
            "clinician_id": new_clinician.clinician_id,
            "user_id": new_user.user_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error during clinician creation: {str(e)}"
        }), 500


    # Get a specific clinician by ID
@app.route('/api/clinicians/<int:clinician_id>', methods=['GET'])
def get_clinician(clinician_id):
    clinician = Clinician.query.get_or_404(clinician_id)
    
    return jsonify({
        "clinician_id": clinician.clinician_id,
        "user_id": clinician.user_id,
        "full_name": clinician.full_name,
        "email": clinician.email,
        "phone": clinician.phone,
        "medical_reg_number": clinician.medical_reg_number,
        "specialization": clinician.specialization,
        "years_of_experience": clinician.years_of_experience,
        "affiliated_hospitals": clinician.affiliated_hospitals,
        "aadhar_number": clinician.aadhar_number
    })

# Routes for Queries
@app.route('/api/queries', methods=['POST'])
def create_query():
    data = request.json
    
    # Generate a chat_id if not provided
    if 'chat_id' not in data:
        # Generate a simple unique identifier based on timestamp
        data['chat_id'] = f"chat_{int(datetime.now().timestamp())}"
    
    # Create the query
    new_query = Query(
        chat_id=data['chat_id'],
        patient_id=data['patient_id'],
        clinician_id=data.get('clinician_id'),
        query_text=data['query_text'],
        response=data.get('response'),
        query_status=data.get('query_status', 'Pending')
    )
    db.session.add(new_query)
    db.session.commit()
    
    return jsonify({
        "message": "Query created successfully", 
        "query_id": new_query.query_id,
        "chat_id": new_query.chat_id
    }), 201

@app.route('/api/queries/<int:query_id>', methods=['GET'])
def get_query(query_id):
    query = Query.query.get_or_404(query_id)
    return jsonify({
        "query_id": query.query_id,
        "chat_id": query.chat_id,
        "patient_id": query.patient_id,
        "clinician_id": query.clinician_id,
        "query_text": query.query_text,
        "response": query.response,
        "query_status": query.query_status,
        "created_at": query.created_at.isoformat()
    })


# Get all patients
@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    try:
        print("Fetching all patients...")  # Debug log
        patients = Patient.query.all()
        print(f"Found {len(patients)} patients")  # Debug log
        
        if not patients:
            return jsonify({"message": "No patients found", "patients": []}), 200
            
        result = []
        for patient in patients:
            result.append({
                "patient_id": patient.patient_id,
                "user_id": patient.user_id,
                "full_name": patient.full_name,
                "email": patient.email,
                "dob": patient.dob.isoformat() if patient.dob else None,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
                "phone": patient.phone
            })
        print(f"Returning {len(result)} patients")  # Debug log
        return jsonify({"patients": result})
        
    except Exception as e:
        print(f"Error in get_all_patients: {str(e)}")  # Debug log
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Get all clinicians
@app.route('/api/clinicians', methods=['GET'])
def get_all_clinicians():
    clinicians = Clinician.query.all()
    result = []
    for clinician in clinicians:
        result.append({
            "clinician_id": clinician.clinician_id,
            "user_id": clinician.user_id,
            "full_name": clinician.full_name,
            "email": clinician.email,
            "specialization": clinician.specialization,
            "years_of_experience": clinician.years_of_experience,
            "affiliated_hospitals": clinician.affiliated_hospitals
            # Add other fields as needed
        })
    return jsonify(result)

# Get all users
@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "user_id": user.user_id,
            "is_patient": user.is_patient,
            "is_clinician": user.is_clinician
            # Exclude password_hash for security reasons
        })
    return jsonify(result)

# Get all queries
@app.route('/api/queries', methods=['GET'])
def get_all_queries():
    queries = Query.query.all()
    result = []
    for query in queries:
        result.append({
            "query_id": query.query_id,
            "chat_id": query.chat_id,
            "patient_id": query.patient_id,
            "clinician_id": query.clinician_id,
            "query_text": query.query_text,
            "response": query.response,
            "query_status": query.query_status,
            "created_at": query.created_at.isoformat() if query.created_at else None
        })
    return jsonify(result)

# Get database summary (counts of all entities)
@app.route('/api/db-summary', methods=['GET'])
def get_db_summary():
    return jsonify({
        "total_users": User.query.count(),
        "total_patients": Patient.query.count(),
        "total_clinicians": Clinician.query.count(),
        "total_queries": Query.query.count(),
        "pending_queries": Query.query.filter_by(query_status='Pending').count(),
        "completed_queries": Query.query.filter_by(query_status='Completed').count()
    })

# Get queries by patient ID
@app.route('/api/patients/<int:patient_id>/queries', methods=['GET'])
def get_queries_by_patient_id(patient_id):  # Renamed function
    # Verify patient exists
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all queries for this patient
    queries = Query.query.filter_by(patient_id=patient_id).all()
    result = []
    for query in queries:
        result.append({
            "query_id": query.query_id,
            "chat_id": query.chat_id,
            "query_text": query.query_text,
            "response": query.response,
            "query_status": query.query_status,
            "created_at": query.created_at.isoformat() if query.created_at else None
        })
    return jsonify(result)

# Get queries by clinician ID
@app.route('/api/clinicians/<int:clinician_id>/queries', methods=['GET'])
def get_queries_by_clinician_id(clinician_id):  # Use a unique name here too
    # Verify clinician exists
    clinician = Clinician.query.get_or_404(clinician_id)
    
    # Get all queries assigned to this clinician
    queries = Query.query.filter_by(clinician_id=clinician_id).all()
    result = []
    for query in queries:
        result.append({
            "query_id": query.query_id,
            "chat_id": query.chat_id,
            "patient_id": query.patient_id,
            "query_text": query.query_text,
            "response": query.response,
            "query_status": query.query_status,
            "created_at": query.created_at.isoformat() if query.created_at else None
        })
    return jsonify(result)

# Run the Flask App
# Run the Flask App
if __name__ == '__main__':
    # Initialize database
    if not init_db():
        print("Error: Could not initialize database. Exiting...")
        sys.exit(1)
        
    # Initialize Gemini API
    gemini_initialized = initialize_gemini()
    if gemini_initialized:
        print("Gemini API initialized successfully")
    else:
        print("Warning: Gemini API not initialized. AI responses will be unavailable.")
    
    # Start Flask app
    print("Starting Flask application...")
    app.run(debug=True)