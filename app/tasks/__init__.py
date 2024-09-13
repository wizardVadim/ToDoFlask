from http.client import error

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models  import Task, User, db
from datetime import timezone, datetime

from app.tasks.forms import TaskForm

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

    print(data)

    # Найти пользователя по его имени
    user = User.query.filter_by(username=current_user.get('username')).first()

    # Проверка существовани пользователя
    if not user:
        return make_response(jsonify({'message': 'Не найден текущий пользователь'}), 500)

    # Получение формы валидации
    form = TaskForm(data=data)

    if form.validate():

        new_task = Task(user_id=user.id, title=form.title.data, description=form.description.data)

        try:
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response(jsonify({'message': 'Произошла ошибка при добавлении в базу данных'}), 500)

        return make_response(jsonify({'message': 'Добавление прошло успешно', 'id': new_task.id}), 200)

    # Выводим ошибки валидации если они есть
    error_string = ''

    for field, errors in form.errors.items():
        for current_error in errors:
            if error_string != '':
                error_string += '\n'
            error_string += f'{current_error}'

    return make_response(jsonify({'message': error_string}), 400)



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