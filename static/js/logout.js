document.getElementById('logoutBtn').addEventListener('click', function(event) {
    event.preventDefault();

    fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/login';  // Перенаправляем на страницу входа
        } else {
            console.error('Ошибка при выходе');
        }
    })
    .catch(error => console.error('Ошибка:', error));
});