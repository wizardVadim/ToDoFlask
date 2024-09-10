from crypt import methods
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from flask_cors import CORS
from models import User, db, Task
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy.exc import IntegrityError
import settings
from datetime import timedelta
import logging

def check_token(token):
    try:
        decoded = decode_token(token)
        print("Токен декодирован успешно:", decoded)
    except Exception as e:
        print("Ошибка при декодировании токена:", e)

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir   = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
secret_key   = 'adminKeyJWT'

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app, supports_credentials=True)

# Настройка строки подключения к PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + settings.getSetting("postgres_user") + ':' + settings.getSetting("postgres_pass") +'@localhost:5432/todo_list'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Config
app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = secret_key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
# Включаем черный список токенов
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


# Включение отладки для JWT
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'  # Убедитесь, что сообщения об ошибках возвращаются в JSON-формате
logging.basicConfig(level=logging.DEBUG)

# Инициализация объекта SQLAlchemy
db.init_app(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# Механизм хранения черного списка
BLACKLIST_JWT = set()

with app.app_context():
    db.create_all()

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in BLACKLIST_JWT

# Обработчик неавторизованного доступа
@jwt.unauthorized_loader
def unauthorized_callback(callback):

    print(request.cookies.get('access_token'))
    print("JWT не был предоставлен или недействителен.")

    # Перенаправление на страницу входа, если токен недействителен или отсутствует
    return redirect(url_for('login'))

# Обработчик для ошибок истекшего токена
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("JWT токен истек.")
    return redirect(url_for('login'))

# Обработчик для других ошибок
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print("Неверный токен:", error_string)
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@jwt_required(locations=['cookies'])
def index():
    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    print("Текущий пользователь:", current_user)

    # Найти пользователя по его имени
    user = User.query.filter_by(username=current_user.get('username')).first()

    # Получить все задачи, связанные с пользователем
    tasks = Task.query.filter_by(user_id=user.id).all()

    # Преобразовать задачи в формат JSON
    tasks_data = [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for
                  task in tasks]

    for task in tasks:
        print(task.id)
        if (task.completed):
            print('comp')
        else:
            print('not comp')

    return render_template('index.html', username=str(current_user.get('username')), is_authenticated=is_authenticated, tasks=tasks_data)


# Маршрут для регистрации
@app.route('/register', methods=['POST', 'GET'])
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

    return render_template('register.html', is_authenticated=is_authenticated)

# Маршрут для входа
@app.route('/login', methods=['POST', 'GET'])
@jwt_required(optional=True)
def login():
    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form

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

    return render_template('login.html', is_authenticated=is_authenticated)

# Маршрут для выхода (удаление cookie с токеном)
@app.route('/logout', methods=['GET', 'POST'])
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

# Маршрут для удаления задачи
@app.route('/remove_task', methods=['POST'])
@jwt_required(locations=['cookies'])
def remove_task():
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    task_id = data.get('task_id')

    print('task_id: ' + task_id)

    # Проверка наличия данных
    if not task_id:
        return make_response(jsonify({'message': 'Отсутствует идентификатор задачи'}), 400)

    task = Task.query.filter_by(id=task_id).first()

    #Проверка наличия задачи в БД
    if not task:
        return make_response(jsonify({'message': 'Данной задачи нет в базе данных'}), 401)

    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return make_response(jsonify({'message': 'Произошла ошибка при удалении'}), 500)

    return make_response(jsonify({'message': 'Удаление прошло успешно'}), 200)

# Маршрут для добавления задачи
@app.route('/add_task', methods=['POST'])
@jwt_required(locations=['cookies'])
def add_task():
    current_user = get_jwt_identity()

    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    task_title = data.get('task_title')
    task_description = data.get('task_description')

    print(task_title + ' ' + task_description + ' - Данные задачи')

    # Проверка наличия данных
    if not task_title or not task_description:
        return make_response(jsonify({'message': 'Отсутствуют данные по задаче'}), 400)

    # Найти пользователя по его имени
    user = User.query.filter_by(username=current_user.get('username')).first()

    # Проверка существовани пользователя
    if not user:
        return make_response(jsonify({'message': 'Не найден текущий пользователь'}), 500)

    new_task = Task(user_id=user.id, title=task_title, description=task_description)

    try:
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return make_response(jsonify({'message': 'Произошла ошибка при добавлении в базу данных'}), 500)

    return make_response(jsonify({'message': 'Добавление прошло успешно', 'id': new_task.id}), 200)

# Маршрут для выполнения задачи
@app.route('/complete_task', methods=['POST'])
@jwt_required(locations=['cookies'])
def complete_task():

    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    task_id = data.get('task_id')
    checked = data.get('checked')

    if checked:
        print('checked')
    else:
        print('not checked')

    # print(task_id + ' ' + checked + ' - Данные задачи')

    # Проверка наличия данных
    if not task_id or not checked:
        return make_response(jsonify({'message': 'Отсутствуют данные по задаче'}), 400)

    # Найти задачу по id
    task = Task.query.filter_by(id=task_id).first()

    # Проверка существовани пользователя
    if not task:
        return make_response(jsonify({'message': 'Не найдена задача'}), 500)

    try:
        task.completed = checked
        if checked:
            task.completedAt = datetime.now(timezone.utc)
        else:
            task.completedAt = None

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(e)
        return make_response(jsonify({'message': 'Произошла ошибка при изменении в базе данных'}), 500)

    return make_response(jsonify({'message': 'Выполнение задачи прошло успешно'}), 200)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)


