document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');

    if (!fightList) {
        return;
    }

    // ✅ Создаём модальное окно через JS
    function createEditFightModal() {
        const modalHtml = `
            <div id="editFightModal" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <span id="closeEditFight" class="close">&times;</span>
                    <form id="editFightForm" method="POST">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name="csrfmiddlewaretoken"]').value}">
                        <label>Номер боя:</label>
                        <input type="number" name="number_fight" id="editNumberFight" required>
                        <label>Боец 1:</label>
                        <input type="text" name="fighter_1" id="editFighter1" required>
                        <label>Боец 2:</label>
                        <input type="text" name="fighter_2" id="editFighter2" required>
                        <button type="submit">Сохранить</button>
                        <button type="button" id="cancelEditFight">Отмена</button>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    createEditFightModal();  // Создаём модальное окно

    const editModal = document.getElementById('editFightModal');
    const editFightForm = document.getElementById('editFightForm');
    const closeEditFight = document.getElementById('closeEditFight');
    const cancelEditFight = document.getElementById('cancelEditFight');

    // ✅ Открытие модального окна с подгрузкой данных боя
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('editFight')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id;

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

            document.getElementById('editNumberFight').value = numberFightElement.textContent.trim();
            document.getElementById('editFighter1').value = fighter1Element.textContent.trim();
            document.getElementById('editFighter2').value = fighter2Element.textContent.trim();
            editFightForm.dataset.uuid = uuidFight;

            editModal.style.display = 'flex';
        }
    });

    // ✅ Закрытие модального окна (по кнопке "Отмена" и по клику на фон)
    function closeModal() {
        editModal.style.display = 'none';
    }

    cancelEditFight.addEventListener('click', closeModal);
    editModal.addEventListener('click', function (event) {
        if (event.target === editModal) {
            closeModal();
        }
    });

    // ✅ Отправка формы через AJAX
    editFightForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(editFightForm);
        const uuidFight = editFightForm.dataset.uuid;

        fetch(`/edit/${uuidFight}/`, {
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
                fightList.innerHTML = data.fights_html;
                closeModal();
            } else {
                alert(data.error || 'Ошибка при редактировании боя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });
});
