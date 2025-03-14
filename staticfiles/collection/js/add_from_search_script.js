function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Добавляем обработчик для всех кнопок "Хочу посмотреть"
document.querySelectorAll('.horizontal-movie-card .btn').forEach(button => {
  button.addEventListener('click', () => {
    // Находим родительскую карточку фильма
    const card = button.closest('.horizontal-movie-card');

    // Собираем данные с карточки
    const movieData = {
      id: Number(card.dataset.filmId),
    };

    // Отправляем данные на сервер
    addToCollection(movieData);
  });
});

// Функция для отправки данных на сервер
async function addToCollection(movieData) {
  try {
    const csrfToken = getCookie('csrftoken'); // Получаем CSRF-токен

    const response = await fetch('add_movie/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(movieData), // Отправляем JSON
    });

    const data = await response.json();

    if (data.success) {
      alert('Фильм добавлен в коллекцию!');
    } else {
      alert('Ошибка: ' + data.message);
    }
  } catch (error) {
    console.error('Ошибка при отправке запроса:', error);
    alert('Произошла ошибка при добавлении фильма.');
  }
}