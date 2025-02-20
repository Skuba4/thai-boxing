document.addEventListener('DOMContentLoaded', function () {
    const fightForm = document.getElementById('fightForm');
    const fightFormContainer = document.getElementById('fightFormContainer');
    const addFightBtn = document.getElementById('addFightBtn');
    const closeAddFight = document.getElementById('closeAddFight'); // ✅ Кнопка "Отмена"
    const fightList = document.getElementById('fight-list');

    if (!fightForm || !fightFormContainer || !addFightBtn || !fightList || !closeAddFight) {
        console.error("❌ Ошибка: Не найден один из элементов для добавления боя.");
        return;
    }

    // ✅ Открытие формы добавления боя
    addFightBtn.addEventListener('click', function () {
        fightFormContainer.style.display = 'block';
    });

    // ✅ Закрытие формы добавления боя по кнопке "Отмена"
    closeAddFight.addEventListener('click', function () {
        fightForm.reset();  // ✅ Очистка формы
        fightFormContainer.style.display = 'none';  // ✅ Скрытие формы
    });

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
                alert(data.error || 'Ошибка при добавлении боя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });
});
