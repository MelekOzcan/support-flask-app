from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    usssername= StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators = [DataRequired()])
    submit = SubmitField('Giriş Yap')

class TicketForm(FlaskForm):
    subject = StringField('Konu', validators=[DataRequired()])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Bileti Gönder')