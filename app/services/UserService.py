from app.models.User import getUserByUsername, addUser, getUserByEmail
from app.models import db
from flask import jsonify, make_response
from sqlalchemy.exc import IntegrityError

class UserService:

    @staticmethod
    def get_user(username):
        return getUserByUsername(username)

    @staticmethod
    def add_user(username, email, password):
        if getUserByUsername(username):
            return None, "Пользователь с таким именем уже существует"
        if getUserByEmail(email):
            return None, "Пользователь с таким E-mail уже существует"

        try:
            addUser(username, email, password)
            return True, None
        except IntegrityError as e:
            db.session.rollback()
            return None, "Ошибка вставки данных в базу данных"

    @staticmethod
    def get_users_parameter(user, parameters_name):

        parameters_list = {
            'id': 0,
            'username': 1,
            'password': 2,
            'email': 3
        }

        return user[parameters_list[parameters_name]]
