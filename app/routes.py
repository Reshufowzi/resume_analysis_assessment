from flask import json, render_template, request, redirect, url_for, session, flash
import os
import spacy
import re
from werkzeug.utils import secure_filename
from app import app
import fitz  # PyMuPDF to read PDF
from flask import jsonify

# Load the spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Define allowed file extensions
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user_type = request.form['user_type']
        
        # Redirect based on user type
        if user_type == 'student':
            return redirect(url_for('student_dashboard', username=username))
        elif user_type == 'experienced':
            return redirect(url_for('experienced_dashboard', username=username))
    
    return render_template('login.html')

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to extract text from a PDF
def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = "".join(page.get_text("text") for page in doc)
    return text

def extract_name_from_text(resume_text):
    """
    Extracts the candidate's name from the top of the resume using the first valid line.
    """
    lines = resume_text.split("\n")
    incorrect_names = {"Java", "SQL", "Python", "C++", "Machine Learning", "Streamlit",
                       "Junior Software", "Thiruvalluvar University"}

    for line in lines:
        line = line.strip()
        if len(line) > 2 and line not in incorrect_names:
            return line

    return "Name not found"

def analyze_resume(filepath):
    resume_text = extract_text_from_pdf(filepath)
    doc = nlp(resume_text)

    extracted_name = extract_name_from_text(resume_text)

    predefined_skills = {
        "Python", "Java", "C++", "C#", "HTML", "CSS", "JavaScript",
        "SQL", "NoSQL", "MongoDB", "MySQL", "PostgreSQL",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "Data Science", "Data Analysis", "Pandas", "NumPy", "Scikit-learn",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux",
        "Flask", "Django", "REST API", "NLP", "Computer Vision",
        "Power BI", "Tableau", "Excel"
    }

    resume_text_lower = resume_text.lower()
    skills = set()
    ats_score = 0

    for skill in predefined_skills:
        if skill.lower() in resume_text_lower:
            skills.add(skill)
            ats_score += 10

    return extracted_name, resume_text, ats_score, list(skills)

@app.route('/student_dashboard/<username>', methods=['GET', 'POST'])
def student_dashboard(username):
    return render_template('student_dashboard.html', username=username)

@app.route('/student_results/<username>', methods=['GET', 'POST'])
def student_results(username):
    if 'resume' not in request.files:
        flash("No file selected, please upload your resume.", "error")
        return redirect(url_for('student_dashboard', username=username))

    resume_file = request.files['resume']

    if resume_file and allowed_file(resume_file.filename):
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)

        extracted_name, resume_text, ats_score, skills = analyze_resume(filepath)
        session['skills'] = skills

        return render_template('results.html', 
                               username=username, 
                               extracted_name=extracted_name,
                               resume_text=resume_text, 
                               ats_score=ats_score, 
                               skills=skills)

    flash("Invalid file type. Please upload a PDF, DOCX, or TXT file.", "error")
    return redirect(url_for('student_dashboard', username=username))

@app.route('/experienced_dashboard/<username>', methods=['GET', 'POST'])
def experienced_dashboard(username):
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash("No file selected, please upload your resume.", "error")
            return redirect(url_for('experienced_dashboard', username=username))

        resume_file = request.files['resume']
        total_experience = request.form.get('total_experience')
        current_position = request.form.get('current_position')
        current_company = request.form.get('current_company')

        if resume_file and allowed_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(filepath)

            extracted_name, resume_text, ats_score, skills = analyze_resume(filepath)
            session['skills'] = skills

            return render_template('experienced_results.html', 
                                   username=username,
                                   total_experience=total_experience,
                                   current_position=current_position,
                                   current_company=current_company,
                                   extracted_name=extracted_name,
                                   resume_text=resume_text,
                                   ats_score=ats_score,
                                   skills=skills)
        
        flash("Invalid file type. Please upload a PDF, DOCX, or TXT file.", "error")
        return redirect(url_for('experienced_dashboard', username=username))

    return render_template('experienced_dashboard.html', username=username)

@app.route('/experienced_results/<username>', methods=['GET', 'POST'])
def experienced_results(username):
    if 'resume' not in request.files:
        flash("No file selected, please upload your resume.", "error")
        return redirect(url_for('experienced_dashboard', username=username))

    resume_file = request.files['resume']

    if resume_file and allowed_file(resume_file.filename):
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)

        extracted_name, resume_text, ats_score, skills = analyze_resume(filepath)
        session['skills'] = skills

        return render_template('experienced_results.html', 
                               username=username, 
                               extracted_name=extracted_name,
                               resume_text=resume_text, 
                               ats_score=ats_score, 
                               skills=skills)

    flash("Invalid file type. Please upload a PDF, DOCX, or TXT file.", "error")
    return redirect(url_for('experienced_dashboard', username=username))


def load_assessment_questions():
    with open('app/static/data/questions.json', 'r') as f:
        return json.load(f)

@app.route('/start_assessment/<username>', methods=['POST', 'GET'])
def start_assessment(username):
    if 'skills' not in session:
        return "Skills not found. Please upload a resume first.", 400

    skills = session['skills']

    questions_data = load_assessment_questions()
    assessment_questions = []

    for skill in skills:
        if skill in questions_data:
            assessment_questions.extend(questions_data[skill])

    session['assessment_questions'] = assessment_questions
    session['username'] = username

    return render_template('assessment_page.html', username=username, questions=assessment_questions)

@app.route('/assessment_result', methods=['POST'])
def assessment_result():
    questions = session.get('assessment_questions', [])
    username = session.get('username', 'User')

    user_answers = request.form.getlist('answers[]')
    score = 0

    for idx, question in enumerate(questions):
        correct_answer = question["answer"]
        if idx < len(user_answers) and user_answers[idx] == correct_answer:
            score += 1

    return render_template('assessment_result.html', username=username, score=score, questions=questions)

@app.route('/start_demo_interview/<username>', methods=['POST', 'GET'])
def start_demo_interview(username):
    return render_template('demo_interview.html', username=username)

@app.route('/get_interview_questions/<username>', methods=['GET'])
def get_interview_questions(username):
    # Determine if the user is experienced or a student
    user_type = session.get('user_type', 'student')

    if user_type == 'experienced':
        # Experienced candidate interview questions
        questions = [
            "Tell me about the projects you have worked on.",
            "What was the most challenging project you have worked on?",
            "Describe a time when you had to lead a project.",
            "How do you approach problem-solving in complex projects?",
            "What technologies do you prefer to work with?",
            "How do you handle project deadlines and pressures?",
            "What was the most innovative project you worked on?",
            "How do you ensure your code is maintainable and scalable?"
        ]
    else:
        # Student interview questions
        questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Why should we hire you?",
            "Where do you see yourself in 5 years?",
            "Describe a challenge you faced and how you overcame it.",
            "What is your experience with Python?",
            "Explain the concept of Object-Oriented Programming.",
            "How do you handle work pressure?",
            "What motivates you to do your best on the job?",
            "What do you know about our company?"
        ]

    return jsonify({"questions": questions})
