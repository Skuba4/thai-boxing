document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');
    const editModal = document.getElementById('editFightModal');
    const editFightForm = document.getElementById('editFightForm');
    const fightForm = document.getElementById('fightForm');
    const fightFormContainer = document.getElementById('fightFormContainer');
    const addFightBtn = document.getElementById('addFightBtn');

    if (!fightList || !editModal || !editFightForm || !fightForm) {
        console.error("❌ Ошибка: Не найден один из элементов (fightList, editFightModal, editFightForm, fightForm)");
        return;
    }

    // ✅ Открытие формы добавления боя
    if (addFightBtn) {
        addFightBtn.addEventListener('click', function () {
            fightFormContainer.style.display = 'block';
        });
    }

    // ✅ Отправка формы добавления боя через AJAX
    fightForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(fightForm);
        const uuidRoom = fightForm.dataset.uuid;

        fetch(`/create_fight/${uuidRoom}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fightList.innerHTML = data.fights_html;  // ✅ Обновляем список боёв
                fightForm.reset();  // ✅ Очищаем форму
                fightFormContainer.style.display = 'none';  // ✅ Скрываем форму
            } else {
                alert('Ошибка при добавлении боя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });

    // ✅ Открытие формы редактирования
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('editFight')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id;  // ✅ Теперь тут UUID

            const fightDiv = event.target.closest('.fight');
            if (!fightDiv) {
                console.error("❌ Ошибка: Не найден элемент боя");
                return;
            }

            const numberFightElement = fightDiv.querySelector('.fight-number');
            const fighter1Element = fightDiv.querySelector('.fighter-1');
            const fighter2Element = fightDiv.querySelector('.fighter-2');

            if (!numberFightElement || !fighter1Element || !fighter2Element) {
                console.error("❌ Ошибка: Не найдены бойцы в DOM");
                return;
            }

            document.getElementById('editNumberFight').value = numberFightElement.textContent;
            document.getElementById('editFighter1').value = fighter1Element.textContent;
            document.getElementById('editFighter2').value = fighter2Element.textContent;
            editFightForm.dataset.uuid = uuidFight;  // ✅ Теперь храним UUID боя

            editModal.style.display = 'block';
        }
    });

    // ✅ Отправка формы редактирования через AJAX
    editFightForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(editFightForm);
        const uuidFight = editFightForm.dataset.uuid;  // ✅ Берём UUID из data-атрибута

        fetch(`/change/${uuidFight}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fightList.innerHTML = data.fights_html;  // ✅ Обновляем список боёв
                editModal.style.display = 'none';  // ✅ Закрываем модалку
            } else {
                alert('Ошибка при редактировании боя.');
            }
        })
        .catch(error => {
            console.error('Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });

    // ✅ Удаление боя через AJAX
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('deleteFight')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id;  // ✅ Теперь удаляем по UUID

            if (!confirm("Ты точно хочешь удалить этот бой?")) {
                return;
            }

            fetch(`/delete_fight/${uuidFight}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fightList.innerHTML = data.fights_html;  // ✅ Обновляем список боёв
                } else {
                    alert('Ошибка при удалении боя.');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                alert('Ошибка соединения');
            });
        }
    });

    // ✅ Закрытие модального окна редактирования
    document.getElementById('closeEditFight').addEventListener('click', function () {
        editModal.style.display = 'none';
    });
});
