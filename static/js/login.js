document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault()
    
    const username = document.getElementById('username').value; // Извлекаем значение поля ввода
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        return response.json().then(data => ({ status: response.status, body: data }));
    })
    .then(({ status, body }) => {
        if (status === 200) {
            // Успешный вход - перенаправление на другую страницу
            window.location.href = '/';
        } else {
            // Ошибка - вывод сообщения пользователю
            document.getElementById('message').innerText = body.message;
        }
    })
    .catch(error => {
        console.error('Ошибка: ', error);
        document.getElementById('message').innerText = 'Произошла ошибка при выполнении запроса.';
    });
});

