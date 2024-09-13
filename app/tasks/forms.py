from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Описание задачи', validators=[DataRequired(), Length(max=2048)])
    submit = SubmitField('Добавить задачу')