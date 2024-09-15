from datetime import timedelta
from flask import Flask, redirect, url_for, request, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app import settings
import logging
from app.models import init_db

# Механизм хранения черного списка
BLACKLIST_JWT = set()

# Создание экземпляра приложения Flask
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

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

    # WTF Config
    app.config['WTF_CSRF_ENABLED'] = False

    logging.basicConfig(level=logging.DEBUG)

    # Инициализация объекта SQLAlchemy
    init_db(app, settings)

    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)

    # Обработчики JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in BLACKLIST_JWT

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        print(request.cookies.get('access_token'))
        print("JWT не был предоставлен или недействителен.")
        return redirect(url_for('auth.login'))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("JWT токен истек.")
        with app.test_client() as client:
            # Делаете POST запрос к маршруту logout
            response = client.post(url_for('auth.logout'))

        return redirect(url_for('auth.login'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print("Неверный токен:", error_string)
        return redirect(url_for('auth.login'))

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
