document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');

    if (!fightList) {
        console.error("❌ Ошибка: Элемент fight-list не найден.");
        return;
    }

    // Обработчик клика для кнопки "Записки"
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('viewNotes')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id;
            const notesContainer = document.getElementById(`notes-${uuidFight}`);

            // Если контейнер уже видим, скрываем его
            if (notesContainer.style.display === 'block') {
                notesContainer.style.display = 'none';
                notesContainer.innerHTML = ''; // Очищаем записи
                return;
            }

            // Получаем записки через AJAX
            fetch(`/view_notes/${uuidFight}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Формируем HTML для записок
                    let notesHtml = '<h4>Судейские записки:</h4>';
                    data.notes.forEach(note => {
                        notesHtml += `
                            <div class="round-note">
                                <strong>Раунд ${note.round_number}:</strong><br>
                                Судья 1: ${note.decision_1}<br>
                                Судья 2: ${note.decision_2}<br>
                                Судья 3: ${note.decision_3}<br>
                            </div><hr>
                        `;
                    });

                    notesContainer.innerHTML = notesHtml;
                    notesContainer.style.display = 'block';
                } else {
                    notesContainer.innerHTML = '<p>Ошибка при загрузке записок.</p>';
                    notesContainer.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                notesContainer.innerHTML = '<p>Ошибка соединения.</p>';
                notesContainer.style.display = 'block';
            });
        }
    });
});
