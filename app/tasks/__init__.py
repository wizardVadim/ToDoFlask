from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import timezone, datetime
from app.services.TaskService import TaskService
from app.services.UserService import UserService

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

    success, error_message = TaskService.remove_task(task_id)

    if not success:
        return make_response(jsonify({'message': error_message}), 409)

    return make_response(jsonify({'message': 'Задача успешно удалена'}), 200)


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
    user = UserService.get_user(current_user.get('username'))

    # Проверка существовани пользователя
    if not user:
        return make_response(jsonify({'message': 'Не найден текущий пользователь'}), 500)

    # Получение формы валидации
    form = TaskForm(data=data)

    if not form.validate():

        # Выводим ошибки валидации если они есть
        error_string = ''

        for field, errors in form.errors.items():
            for current_error in errors:
                if error_string != '':
                    error_string += '\n'
                error_string += f'{current_error}'

        return make_response(jsonify({'message': error_string}), 400)

    success, message = TaskService.add_task(UserService.get_users_parameter(user, 'id'), form.title.data, form.description.data)

    if not success:
        return make_response(jsonify({'message': message}), 409)

    return make_response(jsonify({'message': 'Задача успешно добавлена', 'id': message}), 200)



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

    success, error_message = TaskService.complete_task(task_id, checked)

    if not success:
        return make_response(jsonify({'message': error_message}), 409)

    return make_response(jsonify({'message': 'Задача успешно выполнена'}), 200)