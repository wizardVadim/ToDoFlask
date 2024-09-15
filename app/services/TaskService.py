
from app.models.Task import getTasksByUserId, getTaskById, removeTaskById, addTask, completeTaskById
from app.models import db
from datetime import timezone, datetime


class TaskService:

    @staticmethod
    def get_tasks(user_id):
        return getTasksByUserId(user_id)

    @staticmethod
    def get_task(id):
        return getTaskById(id)

    @staticmethod
    def remove_task(id):

        task = getTaskById(id)

        # Проверка наличия задачи в БД
        if not task:
            return None, "Данной задачи нет в базе данных"

        try:
            removeTaskById(id)
            return True, None
        except Exception as e:
            db.session.rollback()
            print(e)
            return None, "Произошла ошибка при удалении из базы данных"

    @staticmethod
    def add_task(user_id, title, description):

        try:
            id = addTask(user_id, title, description)
            return True, id
        except Exception as e:
            db.session.rollback()
            print(e)
            return None, "Произошла ошибка при добавлении в базу данных"

    @staticmethod
    def complete_task(id, checked):

        # Найти задачу по id
        task = getTaskById(id)

        # Проверка существовани пользователя
        if not task:
            return None, "Не найдена задача"

        if checked:
            completed_at = datetime.now(timezone.utc)
        else:
            completed_at = None

        try:
            completeTaskById(id, checked, completed_at)
            return True, None
        except Exception as e:
            db.session.rollback()
            print(e)
            return None, "Произошла ошибка при выполнении в базе данных"

    @staticmethod
    def get_tasks_parameter(task, parameters_name):

        parameters_list = {
            'id': 0,
            'title': 1,
            'description': 2,
            'user_id': 3,
            'created_at': 4,
            'completed': 5,
            'completed_at': 6,
            'deleted': 7,
            'deleted_at': 8
        }

        return task[parameters_list[parameters_name]]
