# 🛠️ Support Ticket System – Flask App

This is a simple support ticket system built with Python and Flask.  
Users can register, log in, and submit support tickets.  
Admins can view all tickets and update their status (Open, Answered, Closed).

## ✨ Features
- User registration & login (Flask-Login)
- Admin panel with ticket management
- SQLAlchemy-based database
- Form validation (Flask-WTF)
- Bootstrap UI
- Deploy-ready (Render.com)

## 🚀 Live Demo
[Coming Soon]

## 💻 Installation

1. Clone the repository:  
   `git clone https://github.com/MelekOzcan/support-flask-app.git`

2. Navigate to the project directory:  
   `cd support-flask-app`

3. Create and activate a virtual environment:  
   - Windows:  
     `python -m venv venv`  
     `venv\Scripts\activate`  
   - Mac/Linux:  
     `python3 -m venv venv`  
     `source venv/bin/activate`

4. Install the dependencies:  
   `pip install -r requirements.txt`

5. Initialize the database:  
   `flask db upgrade`

6. Create admin users (optional):  
   `flask create-admin`

7. Run the application:  
   `flask run`

## 📂 Project Structure

- `app.py` – Main Flask application and routes  
- `models.py` – Database models for User and Ticket  
- `forms.py` – WTForms for login, registration, and tickets  
- `templates/` – HTML templates with Jinja2  
- `static/` – Static files (CSS, JS, images)  

## 🤝 Contribution

Feel free to open issues or submit pull requests!

---

© 2025 Melek Özcan  
