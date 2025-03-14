document.addEventListener('DOMContentLoaded', () => {
  // Обработчик для кнопки "Редактировать"
  document.querySelectorAll('.edit-button').forEach(button => {
    button.addEventListener('click', () => {
      const listItem = button.closest('.list-group-item');
      const collectionName = listItem.querySelector('.collection-name');
      const editForm = listItem.querySelector('.edit-form');

      // Скрываем название и показываем форму
      collectionName.style.display = 'none';
      editForm.style.display = 'block';
    });
  });

  // Обработчик для кнопки "Отмена"
  document.querySelectorAll('.cancel-edit').forEach(button => {
    button.addEventListener('click', () => {
      const listItem = button.closest('.list-group-item');
      const collectionName = listItem.querySelector('.collection-name');
      const editForm = listItem.querySelector('.edit-form');

      // Скрываем форму и показываем название
      editForm.style.display = 'none';
      collectionName.style.display = 'inline';
    });
  });

  // Обработчик для формы редактирования
  document.querySelectorAll('.edit-form').forEach(form => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault(); // Предотвращаем стандартное поведение формы

      const listItem = form.closest('.list-group-item');
      const collectionId = listItem.dataset.collectionId;
      const newName = form.querySelector('.edit-input').value;

      try {
        // Отправляем PATCH-запрос на сервер
        const response = await fetch(`/collection/${collectionId}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Добавляем CSRF-токен
          },
          body: JSON.stringify({ name: newName }),
        });

        const data = await response.json();

        if (data.success) {
          // Обновляем название коллекции на странице
          const collectionName = listItem.querySelector('.collection-name');
          collectionName.textContent = newName;

          // Скрываем форму и показываем название
          form.style.display = 'none';
          collectionName.style.display = 'inline';
        } else {
          alert('Ошибка: ' + data.message);
        }
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error);
        alert('Произошла ошибка при обновлении названия.');
      }
    });
  });

  // Обработчик для кнопки "Удалить"
  document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', async () => {
      const listItem = button.closest('.list-group-item');
      const collectionId = listItem.dataset.collectionId;

      if (confirm('Вы уверены, что хотите удалить эту коллекцию?')) {
        try {
          // Отправляем DELETE-запрос на сервер
          const response = await fetch(`/collection/${collectionId}/`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'), // Добавляем CSRF-токен
            },
          });

          const data = await response.json();

          if (data.success) {
            // Удаляем элемент коллекции из DOM
            listItem.remove();
          } else {
            alert('Ошибка: ' + data.message);
          }
        } catch (error) {
          console.error('Ошибка при отправке запроса:', error);
          alert('Произошла ошибка при удалении коллекции.');
        }
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  // Поиск контейнеров для фильмов
  const availableFilmsContainer = document.querySelector('.available-films .row');
  const addedFilmsContainer = document.querySelector('.added-films .row');

  // Если контейнеры не найдены, завершаем выполнение
  if (!availableFilmsContainer || !addedFilmsContainer) {
    return;
  }

  // Функция для перемещения фильма в блок "Добавленные"
  function moveFilmToAdded(filmCard, button) {
    addedFilmsContainer.appendChild(filmCard);

    // Меняем кнопку на "Убрать"
    button.textContent = 'Убрать';
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-outline-danger');
    button.removeEventListener('click', addFilmHandler);
    button.addEventListener('click', removeFilmHandler);
  }

  // Функция для перемещения фильма обратно в блок "Доступные"
  function moveFilmToAvailable(filmCard, button) {
    availableFilmsContainer.appendChild(filmCard);

    // Меняем кнопку на "Добавить"
    button.textContent = 'Добавить';
    button.classList.remove('btn-outline-danger');
    button.classList.add('btn-outline-primary');
    button.removeEventListener('click', removeFilmHandler);
    button.addEventListener('click', addFilmHandler);
  }

  // Обработчик для кнопки "Добавить"
  function addFilmHandler() {
    const filmCard = this.closest('.col');
    moveFilmToAdded(filmCard, this);
  }

  // Обработчик для кнопки "Убрать"
  function removeFilmHandler() {
    const filmCard = this.closest('.col');
    moveFilmToAvailable(filmCard, this);
  }

  // Инициализация обработчиков для кнопок "Добавить"
  const addFilmButtons = document.querySelectorAll('.add-film-button');
  if (addFilmButtons.length > 0) {
    addFilmButtons.forEach(button => {
      button.addEventListener('click', addFilmHandler);
    });
  }

  // Обработчик для формы создания коллекции
  const createCollectionForm = document.getElementById('createCollectionForm');
  if (createCollectionForm) {
    createCollectionForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const collectionName = document.getElementById('collectionName').value;
      const addedFilmIds = Array.from(addedFilmsContainer.querySelectorAll('.add-film-button')).map(button => Number(button.dataset.filmId));

      try {
        // Отправляем POST-запрос на сервер для создания коллекции
        const response = await fetch('/collections/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ 
            name: collectionName,
            film_ids: addedFilmIds,
          }),
        });

        const data = await response.json();

        if (data.success) {
          alert('Коллекция успешно создана!');
          window.location.reload();
        } else {
          alert('Ошибка: ' + data.message);
        }
      } catch (error) {
        alert('Произошла ошибка при создании коллекции.');
      }
    });
  }
});

// Функция для получения CSRF-токена из куки
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