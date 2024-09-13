from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Task
from app.tasks.forms import TaskForm

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/', methods=['GET'])
@jwt_required(locations=['cookies'])
def index():
    current_user = get_jwt_identity()
    is_authenticated = current_user is not None

    print("Текущий пользователь:", current_user)

    # Найти пользователя по его имени
    user = User.query.filter_by(username=current_user.get('username')).first()

    # Получить все задачи, связанные с пользователем
    tasks = Task.query.filter_by(user_id=user.id).all()

    # Преобразовать задачи в формат JSON
    tasks_data = [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for
                  task in tasks]

    # Отладка
    for task in tasks:
        print(task.id)
        if (task.completed):
            print('comp')
        else:
            print('not comp')

    return render_template('index.html', username=str(current_user.get('username')), is_authenticated=is_authenticated, tasks=tasks_data)
