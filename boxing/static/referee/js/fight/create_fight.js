document.addEventListener('DOMContentLoaded', function () {
    const addFightBtn = document.getElementById('addFightBtn');
    const fightList = document.getElementById('fight-list');

    if (!addFightBtn || !fightList) {
        return;
    }

    // ✅ Получаем UUID комнаты из fight-list
    const uuidRoom = fightList?.dataset.uuid;

    if (!uuidRoom) {
        console.error("❌ Ошибка: UUID комнаты не найден.");
        return;
    }

    // ✅ Создаём модальное окно через JS
    function createFightModal() {
        const modalHtml = `
            <div id="fightFormContainer" class="modal-overlay" style="display:none;">
                <div class="modal-content">
                    <span id="closeAddFight" class="close">&times;</span>
                    <form id="fightForm" method="POST">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name="csrfmiddlewaretoken"]').value}">
                        <label>Номер боя:</label>
                        <input type="number" name="number_fight" required>
                        <label>Боец 1:</label>
                        <input type="text" name="fighter_1" required>
                        <label>Боец 2:</label>
                        <input type="text" name="fighter_2" required>
                        <button type="submit">Добавить</button>
                        <button type="button" id="cancelAddFight">Отмена</button>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    createFightModal();  // Создаём модальное окно

    const fightFormContainer = document.getElementById('fightFormContainer');
    const fightForm = document.getElementById('fightForm');
    const cancelAddFight = document.getElementById('cancelAddFight');

    // ✅ Открытие модального окна
    addFightBtn.addEventListener('click', function () {
        fightFormContainer.style.display = 'flex';
    });

    // ✅ Закрытие модального окна (по кнопке отмены и по клику на фон)
    function closeModal() {
        fightFormContainer.style.display = 'none';
        fightForm.reset();
    }

    cancelAddFight.addEventListener('click', closeModal);
    fightFormContainer.addEventListener('click', function (event) {
        if (event.target === fightFormContainer) {
            closeModal();
        }
    });

    // ✅ Отправка формы через AJAX
    fightForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(fightForm);

        fetch(`/create_fight/${uuidRoom}/`, {  // Теперь UUID точно не undefined
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
                    fightForm.reset();
                    closeModal();
                } else {
                    alert(data.error || 'Ошибка при добавлении боя.');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                alert('Ошибка соединения');
            });
    });
});
