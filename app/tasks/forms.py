from struct import error

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):

    title = StringField(
        'Название задачи'
        , validators=[
            DataRequired(message='Название задачи обязательно для заполнения')
            , Length(max=50, message='Название задачи должно быть не более 50 символов')
        ]
    )

    description = TextAreaField(
        'Описание задачи'
        , validators=[
            DataRequired(message='Описание задачи обязательно для заполнения')
            , Length(max=2048, message='Описание задачи должно быть не более 2048 символов')
        ]
    )

    submit = SubmitField('Добавить')