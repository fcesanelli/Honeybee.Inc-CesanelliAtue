
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,validators, IntegerField
from wtforms.validators import Required


class LoginForm(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[Required()])
    password = PasswordField('Contraseña', validators=[Required()])
    enviar = SubmitField('Ingresar')

class RegistrarForm(LoginForm):
    password_check = PasswordField('Verificar Contraseña', validators=[Required()])
    enviar = SubmitField('Registrarse')

class ClienteForm(FlaskForm):
    consulta = StringField('Ingrese cliente')
    enviar = SubmitField('Enviar')

class ProductoForm(FlaskForm):
    consulta = StringField('Ingrese producto')
    enviar = SubmitField('Enviar')
