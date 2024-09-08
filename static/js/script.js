const form = document.getElementById('todoForm');
        const taskInput = document.getElementById('taskInput');
        const taskList = document.getElementById('taskList');

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const taskText = taskInput.value;
            if (taskText.trim()) {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center task-item';
                li.innerHTML = `<span>${taskText}</span> <button class="btn btn-sm btn-danger delete-btn">Удалить</button>`;
                taskList.appendChild(li);
                taskInput.value = '';

                // Удалить элемент "Нет задач" при добавлении новой задачи
                const noTasksElement = document.getElementById('noTasks');
                if (noTasksElement) {
                    noTasksElement.remove(); // Удаляет элемент "Нет задач"
                }

                li.querySelector('.delete-btn').addEventListener('click', function () {
                    li.remove();
                    checkNoTasks();
                })
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

