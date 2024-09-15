from flask import Blueprint, render_template, request, jsonify, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.__init__ import BLACKLIST_JWT
from .forms import RegistrationForm, LoginForm
import app.services.UserService
from ..services.UserService import UserService

auth = Blueprint('auth', __name__, template_folder='templates')

# Маршрут для регистрации
@auth.route('/register', methods=['POST', 'GET'])
@jwt_required(optional=True)
def register():
    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    if request.method == 'POST':

        if request.content_type == 'application/json':
            # Если запрос содержит JSON-данные
            data = request.get_json()
        else:
            # Если запрос содержит данные формы
            data = request.form

        # Получение экземпляра формы
        form = RegistrationForm(data=data)

        # Проверка валидации
        if not form.validate():

            # Выводим ошибки валидации если они есть
            error_string = ''

            for field, errors in form.errors.items():
                for current_error in errors:
                    if error_string != '':
                        error_string += '\n'
                    error_string += f'{current_error}'

            return make_response(jsonify({'message': error_string}), 400)

        # Хеширование пароля
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Используем сервис для добавления в базу данных
        success, error_message = UserService.add_user(form.username.data, form.email.data, hashed_password)

        if not success:
            return make_response(jsonify({'message': error_message}), 409)

        return make_response(jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201)

    # Выведем для Get запроса страницу
    form = RegistrationForm()

    return render_template('register.html', form=form, is_authenticated=is_authenticated)

# Маршрут для входа
@auth.route('/login', methods=['POST', 'GET'])
@jwt_required(optional=True)
def login():

    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form

        form = LoginForm(data=data)

        if not form.validate():
            # Выводим ошибки валидации если они есть
            error_string = ''

            for field, errors in form.errors.items():
                for current_error in errors:
                    if error_string != '':
                        error_string += '\n'
                    error_string += f'{current_error}'

            return make_response(jsonify({'message': error_string}), 400)

        # Проверка наличия данных
        if not form.username.data or not form.password.data:
            return make_response(jsonify({'message': 'Отсутствует имя пользователя или пароль'}), 400)

        user = UserService.get_user(form.username.data)

        print(user)

        if not user or not check_password_hash(UserService.get_users_parameter(user, 'password'), form.password.data):
            return make_response(jsonify({"message": "Неправильное имя пользователя или пароль"}), 401)

        # Создание JWT токена
        access_token = create_access_token(identity={'username': UserService.get_users_parameter(user, 'username')})
        response = make_response(jsonify({"message": "Пользователь успешно вошел"}), 200)

        # Установите новый токен в куки
        response.set_cookie(
            'access_token_cookie',
            access_token,
            httponly=True,
            secure=True,
            samesite='None'
        )

        # Отладочная печать установленных куки
        print("Установленная кука access_token:", response.headers.get('Set-Cookie'))

        return response

    form = LoginForm()

    return render_template('login.html', form=form, is_authenticated=is_authenticated)

# Маршрут для выхода (удаление cookie с токеном)
@auth.route('/logout', methods=['GET', 'POST'])
@jwt_required(locations=['cookies'])
def logout():
    # Проверка, что токен действителен
    try:
        jti = get_jwt()['jti']
        BLACKLIST_JWT.add(jti)  # Добавляем токен в черный список
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"msg": "Ошибка при выходе"}), 400

    response = make_response(jsonify({"msg": "Выход выполнен успешно"}), 200)
    response.delete_cookie('access_token_cookie')  # Удаляем токен из cookies
    return response