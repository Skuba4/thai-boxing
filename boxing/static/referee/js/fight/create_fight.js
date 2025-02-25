document.addEventListener('DOMContentLoaded', function () {
    const fightForm = document.getElementById('fightForm');
    const fightFormContainer = document.getElementById('fightFormContainer');
    const addFightBtn = document.getElementById('addFightBtn');
    const closeAddFight = document.getElementById('closeAddFight');
    const fightList = document.getElementById('fight-list');

    if (!fightForm || !fightFormContainer || !addFightBtn || !fightList || !closeAddFight) {
        console.warn("⚠️ Пропуск скрипта create_fight.js — элементы не найдены.");
        return;
    }

    addFightBtn.addEventListener('click', function () {
        fightFormContainer.style.display = 'block';
    });

    closeAddFight.addEventListener('click', function () {
        fightForm.reset();
        fightFormContainer.style.display = 'none';
    });

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
                fightList.innerHTML = data.fights_html;
                fightForm.reset();
                fightFormContainer.style.display = 'none';
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
