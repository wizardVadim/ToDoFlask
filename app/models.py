from enum import unique

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Связь с таблицей задач
    tasks = db.relationship('Task', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True) # Идентификатор задачи
    title = db.Column(db.String(50), unique=False, nullable=False) # Заголовок (наименование) задачи
    description = db.Column(db.String(2048), unique=False, nullable=False) # Описание задачи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Связь с пользователем, создавшим задачу
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)  # Время создания
    completed = db.Column(db.Boolean, default=False, nullable=False)  # Маркер выполнения
    deleted = db.Column(db.Boolean, default=False, nullable=False)  # Маркер удаления
    completed_at = db.Column(db.DateTime, nullable=True)  # Время выполнения задачи (если выполнена)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Время удаления задачи (если удалена)

    def __repr__(self):
        return f'<User {self.username}>'