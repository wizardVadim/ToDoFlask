from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, email, Email


class RegistrationForm(FlaskForm):

    username = StringField(
        'Имя пользователя'
        , validators=[
            DataRequired(message='Имя пользователя обязательно для заполнения')
            , Length(min=5, max=50, message='Имя пользователя должно быть от 5 до 50 символов')
        ]
    )

    email = StringField(
        'Email'
        , validators=[
            DataRequired(message='E-mail обязателен для заполнения')
            , Email(message='E-mail введен некорректно')
            , Length(max=120, message='Электронная почта должна содержать не более 120 символов')
        ]
    )

    password = PasswordField(
        'Пароль'
        , validators=[
            DataRequired(message='Пароль обязателен для заполнения')
            , Length(min=6, max=128, message='Пароль должен быть от 6 до 128 символов')
        ]
    )

    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):

    username = StringField(
        'Имя пользователя'
        , validators=[
            DataRequired(message='Имя пользователя обязательно для заполнения')
            , Length(min=5, max=50, message='Имя пользователя должно быть от 5 до 50 символов')
        ]
    )

    password = PasswordField(
        'Пароль'
        , validators=[
            DataRequired(message='Пароль обязателен для заполнения')
            , Length(min=6, max=128, message='Пароль должен быть от 6 до 128 символов')
        ]
    )

    submit = SubmitField('Войти')