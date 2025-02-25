document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');
    const resultModal = document.getElementById('resultFightModal');
    const resultFightForm = document.getElementById('resultFightForm');
    const winnerSelect = document.getElementById('winnerSelect');
    const closeResultFight = document.getElementById('closeResultFight');

    if (!fightList || !resultModal || !resultFightForm || !winnerSelect) {
        return;
    }

    let currentUuidFight = null;

    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('finalDecision')) {
            event.preventDefault();
            currentUuidFight = event.target.dataset.id;

            if (!currentUuidFight) {
                console.error("❌ Ошибка: UUID боя не найден.");
                return;
            }

            resultModal.style.display = 'block';
        }
    });

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
                resultModal.style.display = 'none';
                resultFightForm.reset();
            } else {
                alert(data.error || 'Ошибка при установке победителя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });

    closeResultFight?.addEventListener('click', function () {
        resultModal.style.display = 'none';
        resultFightForm.reset();
    });
});

