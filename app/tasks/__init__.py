from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models  import Task, User, db
from datetime import timezone, datetime

tasks = Blueprint('tasks', __name__, template_folder='templates')

# Маршрут для удаления задачи
@tasks.route('/remove_task', methods=['POST'])
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
@tasks.route('/add_task', methods=['POST'])
@jwt_required(locations=['cookies'])
def add_task():
    current_user = get_jwt_identity()

    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    task_title = data.get('task_title')
    task_description = data.get('task_description')

    if len(task_title) > 50:
        return make_response(jsonify({'message': 'Название заголовка должно быть не более 50 символов'}), 400)

    if len(task_description) > 2048:
        return make_response(jsonify({'message': 'Описание должно быть не более 2048 символов'}), 400)

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
@tasks.route('/complete_task', methods=['POST'])
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
    if not task_id:
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