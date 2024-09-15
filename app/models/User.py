from app.models import db
from sqlalchemy.sql import text

# Поиск пользователя по идентификатору
def getUserById(id):
    result = db.session.execute(text("SELECT * FROM users WHERE id = :id"), {'id': id})
    return result.fetchone()

# Поиск пользователя по имени пользователя
def getUserByUsername(username):
    result = db.session.execute(text("SELECT * FROM users WHERE username = :username"), {'username': username})
    return result.fetchone()

# Поиск пользователя по почте
def getUserByEmail(email):
    result = db.session.execute(text("SELECT * FROM users WHERE email = :email"), {'email': email})
    return result.fetchone()

# Добавление пользователя в таблицу users
def addUser(username, email, password):

    current_query = """
        INSERT INTO users (username, password, email)
        VALUES (:username, :password, :email)
    """

    params = {
        'username': username,
        'password': password,
        'email': email
    }

    result = db.session.execute(text(current_query), params)
    db.session.commit()
    return result.rowcount