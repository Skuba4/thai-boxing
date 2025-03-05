document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');

    if (!fightList) {
        return;
    }

    // ✅ Создаём модальное окно через JS
    function createResultFightModal() {
        const modalHtml = `
            <div id="resultFightModal" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <span id="closeResultFight" class="close">&times;</span>
                    <form id="resultFightForm" method="POST">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('[name="csrfmiddlewaretoken"]').value}">
                        <h3>Выбери победителя</h3>
                        <select id="winnerSelect" name="winner" required>
                            <option value="" disabled selected>Выбери победителя</option>
                            <option value="fighter_1">Боец 1</option>
                            <option value="fighter_2">Боец 2</option>
                            <option value="draw">Ничья</option>
                        </select>
                        <br><br>
                        <button type="submit">Сохранить</button>
                        <button type="button" id="cancelResultFight">Отмена</button>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    createResultFightModal();  // Создаём модальное окно

    const resultModal = document.getElementById('resultFightModal');
    const resultFightForm = document.getElementById('resultFightForm');
    const winnerSelect = document.getElementById('winnerSelect');
    const closeResultFight = document.getElementById('closeResultFight');
    const cancelResultFight = document.getElementById('cancelResultFight');

    let currentUuidFight = null;

    // ✅ Открытие модального окна при выборе победителя
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('finalDecision')) {
            event.preventDefault();
            currentUuidFight = event.target.dataset.id;

            if (!currentUuidFight) {
                console.error("❌ Ошибка: UUID боя не найден.");
                return;
            }

            resultModal.style.display = 'flex';
        }
    });

    // ✅ Закрытие модального окна (по кнопке "Отмена" и по клику на фон)
    function closeModal() {
        resultModal.style.display = 'none';
        resultFightForm.reset();
    }

    cancelResultFight.addEventListener('click', closeModal);
    resultModal.addEventListener('click', function (event) {
        if (event.target === resultModal) {
            closeModal();
        }
    });

    // ✅ Отправка формы через AJAX
    resultFightForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const winner = winnerSelect.value;

        if (!winner) {
            alert("Выбери победителя!");
            return;
        }

        fetch(`/set_winner/${currentUuidFight}/`, {
            method: 'POST',
            body: JSON.stringify({ winner: winner }),
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fightList.innerHTML = data.fights_html;
                closeModal();
            } else {
                alert(data.error || 'Ошибка при установке победителя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });
});
