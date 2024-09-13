from flask import Blueprint, render_template, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.models import User, db
from app.__init__ import BLACKLIST_JWT
from .forms import RegistrationForm, LoginForm


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
        if form.validate():

            # Выводим ошибки валидации если они есть
            error_string = ''

            for field, errors in form.errors.items():
                for current_error in errors:
                    if error_string != '':
                        error_string += '\n'
                    error_string += f'{current_error}'

            return make_response(jsonify({'message': error_string}), 400)

        username = data.get('username')
        password = data.get('password')
        email    = data.get('email')

        print(str(type(username)) + str(type(password)))

        if User.query.filter_by(username=username).first():
            response = make_response(jsonify({"message": "Пользователь с таким именем уже существует"}), 409)
            return response

        if User.query.filter_by(email=email).first():
            response = make_response(jsonify({"message": "Пользователь с таким E-mail уже существует"}), 409)
            return response

        # Хеширование пароля
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            # Печать информации об ошибке для отладки
            print(str(e.orig))  # Выводит оригинальное сообщение об ошибке от psycopg2
            response = make_response(jsonify({"message": "Ошибка вставки данных в базу данных.", "error": str(e)}), 500)
            return response

        response = make_response(jsonify({"message": "Пользователь успешно зарегистрирован"}), 201)
        return response

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

        username = data.get('username')
        password = data.get('password')

        # Проверка наличия данных
        if not username or not password:
            return make_response(jsonify({'message': 'Отсутствует имя пользователя или пароль'}), 400)

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return make_response(jsonify({"message": "Неправильное имя пользователя или пароль"}), 401)

        # Создание JWT токена
        access_token = create_access_token(identity={'username': user.username})
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