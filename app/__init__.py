from crypt import methods
from datetime import timedelta
from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from app.models import User, db, Task
from flask_jwt_extended import JWTManager
from app import settings
import logging

# Механизм хранения черного списка
BLACKLIST_JWT = set()


# Создание экземпляра приложения Flask
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # Настройка строки подключения к PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + settings.getSetting(
        "postgres_user") + ':' + settings.getSetting("postgres_pass") + '@localhost:5432/todo_list'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT Config
    secret_key = settings.getSetting("secret_key_jwt")
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = secret_key
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

    logging.basicConfig(level=logging.DEBUG)

    # Инициализация объекта SQLAlchemy
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)

    with app.app_context():
        db.create_all()

    # Обработчики JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in BLACKLIST_JWT

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        print(request.cookies.get('access_token'))
        print("JWT не был предоставлен или недействителен.")
        return redirect(url_for('login'))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("JWT токен истек.")
        return redirect(url_for('login'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print("Неверный токен:", error_string)
        return redirect(url_for('login'))

    # Перенаправление на main
    @app.route('/', methods=['GET'])
    def home_redirect():
        return redirect(url_for('main.index'))

    # Регистрация Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .tasks import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix='/tasks')

    return app
