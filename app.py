from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user
from flask_migrate import Migrate
from models import Ticket, db, User
from forms import TicketForm, LoginForm
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'gizli-anahtar'

db.init_app(app)
migrate = Migrate(app,db)

login_manager= LoginManager()
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
        return f(*args,**kwargs)
    return decorated_function

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('tickets'))
        else:
            flash("Geçersiz kullanıcı adı veya şifre", "danger")
    return render_template('login.html', form=form)

@app.route('/tickets', methods=["GET","POST"])
@login_required
def admin_tickets():
    biletler = Ticket.query.all()
    return render_template("admin_biletler.html", biletler=biletler)
def tickets():
    form = TicketForm()
    if form.validate_on_submit():
        new_ticket =Ticket(
            subject=form.subject.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash("Bilet oluşturuldu!", "succes")
        return redirect(url_for('tickets'))
    
    user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('tickets.html', form=form, tickets=user_tickets)

@app.route('/admin/biletler')
@login_required
@admin_required
def admin_biletler():
    biletler = Ticket.query.all()
    return render_template("admin_biletler.html", biletler=biletler)

@app.route("/admin/bilet<int:bilet_id>/guncelle", methods=["POST"])
@login_required
@admin_required
def bilet_durum_guncelle(bilet_id):
    yeni_durum= request.form.get("status")
    bilet = Ticket.query.get_or_404(bilet_id)
    bilet.status= yeni_durum
    db.session.commit()
    flash("Bilet durumu gücellendi.", "success")
    return redirect(url_for("admin_biletler"))

@app.route("/")
def index():
    return redirect(url_for('tickets'))

if __name__ == "__main__":
    app.run(debug=True)