from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()  

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_superadmin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Açık')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages= db.relationship('TicketMessage', backref='ticket', cascade = "all, delete-orphan", lazy='dynamic')

    user = db.relationship('User', backref='tickets')

class TicketMessage(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender=db.relationship('User', backref='messages')