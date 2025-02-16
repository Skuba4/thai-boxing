document.addEventListener('DOMContentLoaded', function() {
    const addFightBtn = document.getElementById('addFightBtn');
    const fightFormContainer = document.getElementById('fightFormContainer');
    const fightForm = document.getElementById('fightForm');
    const fightList = document.getElementById('fight-list');

    // Логируем попытку обновления страницы
    window.addEventListener('beforeunload', function () {
        console.log('🔄 Страница обновляется или перезагружается!');
    });

    if (addFightBtn) {
        addFightBtn.addEventListener('click', function() {
            fightFormContainer.style.display = 'block';
        });
    }

    if (fightForm) {
        fightForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(fightForm);
            const uuidRoom = fightForm.dataset.uuid;

            console.log('📡 Отправляем AJAX-запрос...');

            fetch(`/create_fight/${uuidRoom}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('✅ AJAX-запрос успешно отправлен!');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('🎯 AJAX успешно обработан, обновляем список боёв!');
                    fightList.innerHTML = data.fights_html;
                    fightForm.reset();
                    fightFormContainer.style.display = 'none';
                } else {
                    alert('Ошибка при создании боя');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                alert('Ошибка соединения');
            });
        });
    }
});