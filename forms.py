from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username= StringField('Kullanıcı Adı', validators=[DataRequired(message="Kullanıcı adı gerekli.")])
    password = PasswordField('Şifre', validators = [DataRequired(message="Şİfre gerekli.")])
    submit = SubmitField('Giriş Yap')

class TicketForm(FlaskForm):
    subject = StringField('Konu', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Açıklama', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Bileti Gönder')


class RegisterForm(FlaskForm):
    username=StringField('Kullanıcı Adı', validators=[DataRequired(message="Kullanıcı adı gerekli."), Length(min=3, max=150)])
    password= PasswordField('Şifre', validators=[DataRequired(message=("Şifre gerekli.")), Length(min=6)])
    submit= SubmitField('Kayıt Ol')

class AdminResponseForm(FlaskForm):
    description = TextAreaField('Yanıt', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Yanıtı Gönder')

class UserReplyForm(FlaskForm):
    description = TextAreaField('Kullanıcı Yanıtı', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Kullanıcı Yanıtını Gönder')

class MessageForm(FlaskForm):
    content = TextAreaField("Mesajınız", validators=[DataRequired()])
    submit = SubmitField("Gönder")