document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');
    const addFightBtn = document.getElementById('addFightBtn');

    if (!fightList) return;

    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    async function sendRequest(url, method, body = null, extraHeaders = {}) {
        try {
            const headers = {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                ...extraHeaders
            };

            const response = await fetch(url, { method, headers, body });
            return response.json();
        } catch (error) {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        }
    }

    function updateFightList(data) {
        if (data?.success && data.fights_html) {
            fightList.innerHTML = data.fights_html;
            attachEventListeners(); // 🔥 Теперь обновляем обработчики после обновления списка боёв
        } else {
            alert(data?.error || 'Ошибка обновления списка боёв.');
        }
    }

    function createModal(id, title, content, submitCallback) {
        let modal = document.getElementById(id);
        if (modal) modal.remove(); // 🔥 Удаляем старое модальное окно, чтобы оно пересоздавалось

        const modalHtml = `
            <div id="${id}" class="modal-overlay">
                <div class="modal-content">
                    <span class="close" data-close="${id}">&times;</span>
                    <h3>${title}</h3>
                    <form id="${id}-form">${content}
                        <button type="submit">Сохранить</button>
                        <button type="button" class="cancel-btn" data-close="${id}">Отмена</button>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modal = document.getElementById(id);

        modal.addEventListener('click', event => {
            if (event.target.classList.contains('modal-overlay') || event.target.dataset.close === id) {
                modal.style.display = 'none';
            }
        });

        document.getElementById(`${id}-form`).addEventListener('submit', async function (e) {
            e.preventDefault();
            await submitCallback(modal);
        });

        return modal;
    }

    function attachEventListeners() {
        fightList.querySelectorAll('.finalDecision').forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                const fightUuid = this.dataset.id; // ✅ Получаем UUID именно для этого клика

                if (!fightUuid) {
                    console.error("❌ Ошибка: UUID боя не найден.");
                    return;
                }

                const modal = createModal('resultFightModal', 'Выбери победителя', `
                    <select id="winnerSelect" name="winner" required>
                        <option value="" disabled selected>Выбери победителя</option>
                        <option value="fighter_1">Боец 1</option>
                        <option value="fighter_2">Боец 2</option>
                        <option value="draw">Ничья</option>
                    </select>
                `, async function (modal) {
                    const winner = document.getElementById('winnerSelect').value;
                    if (!winner) {
                        alert("Выбери победителя!");
                        return;
                    }

                    fetch(`/set_winner/${fightUuid}/`, {
                        method: 'POST',
                        body: JSON.stringify({ winner: winner }),
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateFightList(data);
                            modal.style.display = 'none';
                        } else {
                            alert(data.error || 'Ошибка при установке победителя.');
                        }
                    })
                    .catch(error => {
                        console.error('❌ Ошибка AJAX:', error);
                        alert('Ошибка соединения');
                    });
                });

                modal.style.display = 'flex';
            });
        });
    }

    attachEventListeners(); // 🔥 Теперь инициализируем обработчики после загрузки страницы
});
