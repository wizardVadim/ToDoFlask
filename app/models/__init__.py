from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app, settings):

    # Настройка строки подключения к PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + settings.getSetting(
        "postgres_user") + ':' + settings.getSetting("postgres_pass") + '@localhost:5432/todo_list'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    #  Создадим таблицы
    create_tables(app, db)


def create_tables(app, db):

    with app.app_context():

        # Открываем соединение
        connection = db.engine.connect()

        # Получаем текст запроса на создание таблиц
        with open('app/models/queries/create_tables.sql', 'r') as sql_file:
            sql = sql_file.read()

        connection.execute(text(sql))

        # Закрываем соединение
        connection.close()
