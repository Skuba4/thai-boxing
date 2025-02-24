document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');

    if (!fightList) {
        console.error("❌ Ошибка: Не найден элемент fight-list.");
        return;
    }

    // ✅ Удаление боя через AJAX
    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('deleteFight')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id; // ✅ Удаление по UUID

            if (!uuidFight) {
                console.error("❌ Ошибка: UUID боя не найден.");
                return;
            }

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
                    fightList.innerHTML = data.fights_html;  // ✅ Обновляем список боёв без алерта
                } else {
                    alert(data.error || 'Ошибка при удалении боя.');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                alert('Ошибка соединения');
            });
        }
    });
});
