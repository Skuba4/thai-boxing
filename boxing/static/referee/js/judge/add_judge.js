document.addEventListener('DOMContentLoaded', function () {
    const addJudgeBtn = document.getElementById('addJudgeBtn');
    const addJudgeContainer = document.getElementById('addJudgeContainer');
    const addJudgeForm = document.getElementById('addJudgeForm');
    const closeAddJudge = document.getElementById('closeAddJudge');
    const judgeList = document.getElementById('judge-list');

    if (!addJudgeForm || !addJudgeContainer || !addJudgeBtn || !judgeList) {
        return;
    }

    // ✅ Открытие формы
    addJudgeBtn.addEventListener('click', function () {
        addJudgeContainer.style.display = 'block';
    });

    // ✅ Закрытие формы
    closeAddJudge.addEventListener('click', function () {
        addJudgeContainer.style.display = 'none';
        addJudgeForm.reset();
    });

    // ✅ Отправка формы через AJAX
    addJudgeForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const username = document.getElementById('judgeUsername').value.trim();
        const uuidRoom = addJudgeForm.dataset.uuid;

        if (!username) {
            alert('Введите имя пользователя.');
            return;
        }

        fetch(`/add_judge/${uuidRoom}/`, {
            method: 'POST',
            body: JSON.stringify({ username: username }),
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // ✅ Обновляем весь список судей
                judgeList.innerHTML = `<h4>Список судей:</h4>${data.judges_html}`;
                addJudgeForm.reset();
                addJudgeContainer.style.display = 'none';
            } else {
                alert(data.error || 'Ошибка при добавлении судьи.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });
});


