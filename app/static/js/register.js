document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Предотвращаем стандартную отправку формы

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    fetch('/auth/register', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password,
            email: email
        })
    })
    .then(response => {
        return response.json().then(data => ({ status: response.status, body: data }));
    })
    .then(({ status, body }) => {
        if (status === 201) {
            // Успешная регистрация - перенаправление на страницу входа
            window.location.href = '/auth/login';
        } else {
            // Обработка ошибки - вывод сообщения пользователю
            document.getElementById('message').innerText = body.message;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('message').innerText = 'Произошла ошибка при выполнении запроса.';
    });
});
