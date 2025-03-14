document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('editCollectionModal');
    const collectionId = document.querySelector('[data-collection-id]').dataset.collectionId;
  
    // Обработчик для кнопок "Добавить" и "Удалить"
    modal.addEventListener('click', function (event) {
      const target = event.target;
  
      // Если нажата кнопка "Добавить"
      if (target.classList.contains('add-film-button')) {
        const filmId = target.dataset.filmId;
        moveFilm(filmId, 'add', target);
      }
  
      // Если нажата кнопка "Удалить"
      if (target.classList.contains('remove-film-button')) {
        const filmId = target.dataset.filmId;
        moveFilm(filmId, 'remove', target);
      }
    });
  
    // Функция для перемещения фильма и отправки запроса
    function moveFilm(filmId, action, button) {
      const url = `/collection/${collectionId}/${filmId}/`;
      const method = action === 'add' ? 'POST' : 'DELETE';
  
      fetch(url, {
        method: method,
        headers: {
          'X-CSRFToken': getCookie('csrftoken'), // Получаем CSRF-токен
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          if (response.ok) {
            // Перемещаем карточку фильма
            const filmCard = button.closest('.col');
            const targetGrid = action === 'add'
              ? document.querySelector('.collection-films .row')
              : document.querySelector('.available-films .row');
  
            // Меняем кнопку
            if (action === 'add') {
              button.classList.replace('btn-outline-primary', 'btn-outline-danger');
              button.textContent = 'Удалить';
              button.classList.replace('add-film-button', 'remove-film-button');
            } else {
              button.classList.replace('btn-outline-danger', 'btn-outline-primary');
              button.textContent = 'Добавить';
              button.classList.replace('remove-film-button', 'add-film-button');
            }
  
            // Перемещаем карточку
            targetGrid.appendChild(filmCard);
          } else {
            alert('Ошибка при выполнении действия');
          }
        })
        .catch(error => console.error('Ошибка:', error));
    }
  
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
  
    // Перезагрузка страницы при закрытии модального окна
    modal.addEventListener('hidden.bs.modal', function () {
      console.log('Модальное окно закрыто, перезагружаем страницу...');
      location.reload();
    });
  });