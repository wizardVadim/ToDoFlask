const form = document.getElementById('todoForm');
const taskTitleInput = document.getElementById('taskTitleInput');
const taskDescriptionInput = document.getElementById('taskDescriptionInput');
const taskList = document.getElementById('taskList');

const liTasks = document.querySelectorAll('.task-item');

form.addEventListener('submit', function (e) {
    e.preventDefault();
    const taskTitle = taskTitleInput.value;
    const taskDescription = taskDescriptionInput.value;

    if (taskTitle.trim()) {
        fetch('/tasks/add_task', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ // Преобразуем в строку JSON
                'title': taskTitle,
                'description': taskDescription
            })
        })
        .then(response => {
            return response.json().then(data => ({ status: response.status, body: data }));
        })
        .then(({ status, body }) => {
            if (status === 200) {
                const li = document.createElement('li');
                li.id = `task-${body.id}`;
                li.className = 'list-group-item task-item';
                li.innerHTML = `
                    <div class="task-content">
                        <input type="checkbox" class="custom-checkbox complete-task mr-2" id="checkbox-${body.id}">
                        <div class="task-title" id="taskTitle-${body.id}">${taskTitle}</div>
                        <div class="task-description" id="taskDescription-${body.id}">${taskDescription}</div>
                        <button class="btn btn-sm btn-danger delete-btn">Удалить</button>
                    </div>
                `;

                // Добавление задачи в список
                taskList.appendChild(li);
                taskTitleInput.value = '';
                taskDescriptionInput.value = '';

                // Удалить элемент "Нет задач" при добавлении новой задачи
                const noTasksElement = document.getElementById('noTasks');
                if (noTasksElement) {
                    noTasksElement.remove();
                }


                // Добавление слушателя события для кнопки удаления
                addEventListenerRemoveForTask(li);

                // Добавление слушателя события для кнопки выполнения
                addEventListenerCompleteForTask(li);

            } else {
                document.getElementById('message').innerText = body.message;
            }
        })
        .catch(error => {
            console.error('Ошибка: ', error);
            document.getElementById('message').innerText = 'Произошла ошибка при выполнении запроса.';
        });
    }
});


function checkNoTasks() {
    if (taskList.children.length === 0) {
        const noTasksElement = document.createElement('li');
        noTasksElement.id = 'noTasks';
        noTasksElement.className = 'list-group-item';
        noTasksElement.textContent = 'Нет задач';
        taskList.appendChild(noTasksElement);
    }
}

liTasks.forEach(task => {
    addEventListenerRemoveForTask(task)
});

liTasks.forEach(task => {
    addEventListenerCompleteForTask(task)
});

function addEventListenerRemoveForTask(task) {

    const deleteButton = task.querySelector('.delete-btn');

    // Убедимся, что кнопка существует перед добавлением слушателя
    if (deleteButton) {
        deleteButton.addEventListener('click', function () {
            const taskId = task.id.replace('task-', ''); // Получаем id задачи, убираем префикс

            fetch('/tasks/remove_task', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'task_id': taskId
                })
            })
            .then(response => {
                return response.json().then(data => ({ status: response.status, body: data }));
            })
            .then(({ status, body }) => {
                if (status === 200) {
                    task.remove();
                    checkNoTasks(); // Проверяем, есть ли еще задачи
                } else {
                    document.getElementById('message').innerText = body.message;
                }
            })
            .catch(error => {
                console.error('Ошибка: ', error);
                document.getElementById('message').innerText = 'Произошла ошибка при выполнении запроса.';
            });
        });
    }

}

function addEventListenerCompleteForTask(task) {
    const completeButton = task.querySelector('.complete-task');

    // Убедимся, что кнопка существует перед добавлением слушателя
    if (completeButton) {
        completeButton.addEventListener('change', function () {
            const taskId = task.id.replace('task-', ''); // Получаем id задачи, убираем префикс
            const checked = this.checked;

            fetch('/tasks/complete_task', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'task_id': taskId,
                    'checked': checked
                })
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    // Действия при успешном запросе, например, обновление интерфейса
                    console.log('Task completion status updated successfully.');
                } else {
                    document.getElementById('message').innerText = body.message;
                }
            })
            .catch(error => {
                // console.error('Ошибка: ', error);
                document.getElementById('message').innerText = 'Произошла ошибка при выполнении запроса.';
            });
        });
    } else {
        console.warn('Complete button not found for task:', task);
    }
}
