document.addEventListener('DOMContentLoaded', function () {
    const judgeList = document.getElementById('judge-list');

    if (!judgeList) {
        return;
    }

    // ✅ Переключение активности судьи
    judgeList.addEventListener('click', function (event) {
        if (event.target.classList.contains('activeJudge')) {
            event.preventDefault();

            const judgeId = event.target.dataset.id;
            const uuidRoom = judgeList.dataset.uuid;

            fetch(`/active_judge/${uuidRoom}/${judgeId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ✅ Обновляем список судей
                    judgeList.innerHTML = `<h4>Список судей:</h4>${data.judges_html}`;
                } else {
                    alert(data.error || 'Ошибка при смене статуса судьи.');
                }
            })
            .catch(error => {
                console.error('❌ Ошибка AJAX:', error);
                alert('Ошибка соединения');
            });
        }
    });
});

