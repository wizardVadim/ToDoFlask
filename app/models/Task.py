from app.models import db
from sqlalchemy.sql import text

# Поиск задач по идентификатору пользователя
def getTasksByUserId(user_id):
    result = db.session.execute(text("SELECT * FROM tasks WHERE user_id = :user_id ORDER BY id"), {'user_id': user_id})
    return result.fetchall()

# Найти задачу по идентификатору
def getTaskById(id):
    print(id)
    result = db.session.execute(text("SELECT * FROM tasks WHERE id = :id"), {'id': id})
    return result.fetchone()

# Удалить задачу из базы данных по идентификатору
def removeTaskById(id):
    result = db.session.execute(text("DELETE FROM tasks WHERE id = :id"), {'id': id})
    db.session.commit()
    return result.rowcount

# Добавить задачу в базу данных
def addTask(user_id, title, description):

    current_query = """
            INSERT INTO tasks (user_id, title, description)
            VALUES (:user_id, :title, :description)
            RETURNING id
        """

    params = {
        'user_id': user_id,
        'title': title,
        'description': description
    }

    result = db.session.execute(text(current_query), params)
    new_id = result.scalar()  # Получаем первый (и единственный) результат запроса

    db.session.commit()
    print(f"Inserted task ID: {new_id}")
    return new_id

def completeTaskById(id, checked, completed_at):
    current_query = """
                UPDATE tasks
                SET completed = :checked
                , completed_at = :completed_at
                WHERE id = :id
            """

    params = {
        'id': id,
        'checked': checked,
        'completed_at': completed_at
    }

    result = db.session.execute(text(current_query), params)
    db.session.commit()
    return result.rowcount