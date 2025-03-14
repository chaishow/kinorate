document.addEventListener('DOMContentLoaded', function () {
    const rateMovieModal = document.getElementById('rateMovieModal');
    const ratingSlider = document.getElementById('ratingSlider');
    const ratingValue = document.getElementById('ratingValue');
    const submitRatingButton = document.getElementById('submitRating');
    let currentFilmId = null;
  
    // Обновляем значение оценки при изменении ползунка
    ratingSlider.addEventListener('input', function () {
      ratingValue.textContent = this.value;
    });
  
    // Обработчик открытия модального окна
    rateMovieModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget; // Кнопка, которая открыла модальное окно
      currentFilmId = button.dataset.filmId; // Получаем ID фильма
      console.log('Открыто модальное окно для фильма с ID:', currentFilmId);
    });
  
    // Обработчик отправки оценки
    submitRatingButton.addEventListener('click', function () {
      const rating = ratingSlider.value;
      console.log('Отправка оценки:', rating, 'для фильма с ID:', currentFilmId);
  
      fetch(`/film/${currentFilmId}/rate/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rating: Number(rating) })
      })
        .then(response => {
          if (response.ok) {
            console.log('Оценка успешно отправлена');
            location.reload(); // Перезагружаем страницу
          } else {
            alert('Ошибка при отправке оценки');
          }
        })
        .catch(error => console.error('Ошибка:', error));
    });
  
    // Функция для получения CSRF-токена
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });