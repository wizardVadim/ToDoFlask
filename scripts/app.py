from crypt import methods

from flask import Flask, request, jsonify, render_template
from models import User, db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

app = Flask(__name__, template_folder=template_dir)

# Настройка строки подключения к PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://app:12341234@localhost:5432/todo_list'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'adminKeyJWT'

# Инициализация объекта SQLAlchemy
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Маршрут для регистрации
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Пользователь с таким именем уже существует"}), 409

        # Хеширование пароля
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Пользователь успешно зарегистрирован"}), 201

    return render_template('register.html')

# Маршрут для входа
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Неправильное имя пользователя или пароль"}), 401

        # Создание JWT токена
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200

    return render_template('login.html')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)


