import os 

basedir=os.path.abspath(os.path.dirname(__file__))

from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_migrate import Migrate
from models import db, User, Ticket, TicketMessage
from forms import TicketForm, LoginForm, RegisterForm, AdminResponseForm, UserReplyForm, MessageForm
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask.cli import with_appcontext
from flask_wtf import FlaskForm
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
    return db.session.get(User, int(user_id))

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

            if user.is_superadmin:
                return redirect(url_for("superadmin_dashboard"))
            elif user.is_admin:
                return redirect(url_for('admin_tickets'))
            else:
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
    tickets = Ticket.query.all()
    forms = {ticket.id: AdminResponseForm() for ticket in tickets}
    return render_template("admin_tickets.html", tickets=tickets, forms=forms)

@app.route("/admin/ticket/<int:ticket_id>/update", methods=["POST"])
@login_required
@admin_required
def update_ticket_status(ticket_id):
    new_status = request.form.get("status")
    if new_status not in ["Açık", "Yanıtlandı", "Kapandı"]:
        abort(400, description= "Geçersiz durum")
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = new_status
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
        if current_user.is_superadmin:
            return redirect(url_for("superadmin_dashboard"))
        elif current_user.is_admin:
            return redirect(url_for('admin_tickets'))
        else:
            return redirect(url_for('tickets'))
    return redirect(url_for('login'))

@app.route("/admin/ticket/<int:ticket_id>/response", methods=["POST"])
@login_required
@admin_required
def respond_ticket(ticket_id):
    form=AdminResponseForm(request.form)
    ticket = Ticket.query.get_or_404(ticket_id)

    if form.validate_on_submit():
        new_msg=TicketMessage(
            ticket_id = ticket.id,
            sender_id = current_user.id,
            content = f"[Admin Yanıtı]: {form.description.data}"
        )
        db.session.add(new_msg)
        ticket.status= "Yanıtlandı"
        db.session.commit()

    return redirect(url_for("admin_tickets"))

@app.route("/user/ticket/<int:ticket_id>/response", methods=["POST"])
@login_required
def user_response(ticket_id):
    form = UserReplyForm()
    ticket = Ticket.query.get_or_404(ticket_id)

    if form.validate_on_submit():
        new_msg = TicketMessage(
            ticket_id = ticket.id,
            sender_id = current_user.id,
            content = f"[Kullanıcı Yanıtı]: {form.description.data}"
        )
        db.session.add(new_msg)
        ticket.status ="Açık"
        db.session.commit()
        flash("Yanıt gönderildi", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket.id))

@app.route("/ticket/<int:ticket_id>", methods=["GET","POST"])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form =MessageForm()

    if form.validate_on_submit():
        new_msg = TicketMessage(
            ticket_id =ticket.id,
            sender_id = current_user.id,
            content =  form.content.data
        )
        db.session.add(new_msg)

        if current_user.is_admin:
            ticket.status = "Yanıtlandı"
        else:
            ticket.status =  "Açık"

        db.session.commit()
        flash("Mesaj gönderildi.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket.id))
        
    messages =ticket.messages.order_by(TicketMessage.timestamp.asc()).all()
    return render_template("ticket_detail.html", ticket=ticket, messages=messages, form=form)

@app.route("/ticket/<int:ticket_id>/user-close", methods=["POST"])
@login_required
def user_close_ticket(ticket_id):
    ticket =Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        abort(403)

    answer = request.form.get("cevap")
    if answer =="evet":
        ticket.status ="Kapandı"
        db.session.commit()
        flash("Bilet kapandı. İyi günler!", "success")
    elif answer =="hayir":
        flash("Lütfen sorununuzu daha detaylı bize aktarın.", "info")
    else:
        flash("Geçersiz seçim", "danger")
    return redirect(url_for("ticket_detail", ticket_id=ticket.id))


def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superadmin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/overview")
@login_required
@superadmin_required
def superadmin_dashboard():
    total_tickets = Ticket.query.count()
    total_users = User.query.filter_by(is_admin=False, is_superadmin=False).count()
    total_admin = User.query.filter_by(is_admin=True, is_superadmin=False).count()
    

    open_count = Ticket.query.filter_by(status="Açık").count()
    answered_count= Ticket.query.filter_by(status="Yanıtlandı").count()
    closed_count = Ticket.query.filter_by(status="Kapandı").count()

    last_admintickets = User.query.filter_by(is_admin=True, is_superadmin=False).order_by(User.id.desc()).limit(10).all()
    last_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()

    return render_template("superadmin_dashboard.html",
        total_tickets = total_tickets,
        total_users = total_users,
        total_admin = total_admin,
        open_count=open_count,
        answered_count = answered_count,
        closed_count = closed_count,
        last_admintickets = last_admintickets,
        last_tickets = last_tickets
        )

@app.cli.command("create-sample-superadmin")
@with_appcontext
def create_Sample_superadmin():
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username="superadmin").first():
        hashed_pw = generate_password_hash("superadmin0000")
        new_user =User(username="superadmin", password=hashed_pw, is_superadmin=True)
        db.session.add(new_user)
        db.session.commit()

@app.cli.command("create-sample-users")
@with_appcontext
def create_sample_users():
    from werkzeug.security import generate_password_hash

    users=[ 
        {"username": "admin1", "password":"admin123", "is_admin":True},
        {"username": "admin2", "password":"admin456", "is_admin":True},
        {"username": "user1", "password":"user147", "is_admin":False},
        {"username": "user2", "password":"user258", "is_admin":False},
        {"username": "user3", "password":"user369", "is_admin":False},
        {"username": "superadmin","password":"superadmin0000", "is_superadmin": True}  
        ]

    for u in users:
        if not User.query.filter_by(username=u['username']).first():
            hashed_pw = generate_password_hash(u["password"])
            new_user =User(username=u["username"],
                        password=hashed_pw,
                        is_admin=u.get("is_admin", False),
                        is_superadmin=u.get("is_superadmin", False))
            db.session.add(new_user)

    db.session.commit()

if __name__ == "__main__":  
    app.run(debug=True)

with app.app_context():
    db.create_all()