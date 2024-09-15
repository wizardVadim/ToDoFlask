from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.TaskService import TaskService
from app.services.UserService import UserService

from app.tasks.forms import TaskForm

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/', methods=['GET'])
@jwt_required(locations=['cookies'])
def index():
    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    print("Текущий пользователь:", current_user)

    # Найти пользователя по его имени
    user = UserService.get_user(current_user.get('username'))

    # Получить все задачи, связанные с пользователем
    tasks = TaskService.get_tasks(user.id)

    print(tasks)

    # Преобразовать задачи в формат JSON
    tasks_data = [{"id": TaskService.get_tasks_parameter(task,'id'),
                   "title": TaskService.get_tasks_parameter(task,'title'),
                   "description": TaskService.get_tasks_parameter(task,'description'),
                   "completed": TaskService.get_tasks_parameter(task,'completed')
                   } for
                  task in tasks]

    # Создаем экземпляр формы
    form = TaskForm()

    return render_template('index.html', form=form, username=str(current_user.get('username')), is_authenticated=is_authenticated, tasks=tasks_data)
