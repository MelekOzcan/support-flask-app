import os 

basedir=os.path.abspath(os.path.dirname(__file__))

from flask import Flask, abort, render_template, redirect, url_for, flash, request, session 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_migrate import Migrate
from models import db, User, Ticket
from forms import TicketForm, LoginForm, RegisterForm
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask.cli import with_appcontext
import click 

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'data.db')
app.config['SECRET_KEY'] = 'gizli-anahtar'

db.init_app(app)
migrate = Migrate(app, db)

@app.cli.command("create-admin")
@with_appcontext
def create_admin():
    username=input("Kullanıcı adı: ")
    password = input("Şifre: ")
    from werkzeug.security import generate_password_hash
    hashed_pw =generate_password_hash(password)
    new_user= User(username=username, password=hashed_pw, is_admin=True)
    db.session.add(new_user)
    db.session.commit()
    print("Adminn oluşturuldu.")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Başarıyla giriş yaptınız!", "success")

            if user.is_admin:
                return redirect(url_for('admin_tickets'))
            return redirect(url_for('tickets'))
        else:
            flash("Geçersiz kullanıcı adı veya şifre", "danger")
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hoşgeldin, {current_user.username}! Bu admin paneli gibi bir sayfa olabilir. "        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

@app.route('/tickets', methods=["GET", "POST"])
@login_required
def tickets(): 
    form = TicketForm()
    if form.validate_on_submit():
        new_ticket = Ticket(
            subject=form.subject.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash("Bilet oluşturuldu!", "success")  
        return redirect(url_for('tickets'))
    
    user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('tickets.html', form=form, tickets=user_tickets)

@app.route('/admin/tickets')
@login_required
@admin_required
def admin_tickets():
    biletler = Ticket.query.all()
    return render_template("admin_biletler.html", biletler=biletler)

@app.route("/admin/bilet/<int:bilet_id>/guncelle", methods=["POST"])
@login_required
@admin_required
def bilet_durum_guncelle(bilet_id):
    yeni_durum = request.form.get("status")
    if yeni_durum not in ["Açık", "Yanıtlandı", "Kapalı"]:
        abort(400, description= "Geçersiz durum")
    bilet = Ticket.query.get_or_404(bilet_id)
    bilet.status = yeni_durum
    db.session.commit()
    flash("Bilet durumu güncellendi.", "success")
    return redirect(url_for("admin_tickets"))  

@app.route('/register', methods=["GET", "POST"])
def register():
    form  =RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Bu kullanıcı zaten alınmış.", "danger")
            return render_template("register.html", form=form)
        
        hashed_pw =generate_password_hash(form.password.data)
        new_user =User(username=form.username.data, password=hashed_pw, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_tickets'))
        else:
            return redirect(url_for('tickets'))
    return redirect(url_for('login'))

@app.cli.command("create-sample-users")
@with_appcontext
def create_sample_users():
    from werkzeug.security import generate_password_hash

    users=[ 
        {"username": "admin1", "password":"admin123", "is_admin":True},
        {"username": "admin2", "password":"admin456", "is_admin":True},
        {"username": "user1", "password":"user147", "is_admin":False},
        {"username": "user2", "password":"user258", "is_admin":False},
        {"username": "user3", "password":"user369", "is_admin":False}    
        ]

    for u in users:
        if not User.query.filter_by(username=u['username']).first():
            hashed_pw = generate_password_hash(u["password"])
            new_user =User(username=u["username"], password=hashed_pw, is_admin=u["is_admin"])
            db.session.add(new_user)

    db.session.commit()

if __name__ == "__main__":  
    app.run(debug=True)