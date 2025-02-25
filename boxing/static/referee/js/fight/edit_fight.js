document.addEventListener('DOMContentLoaded', function () {
    const fightList = document.getElementById('fight-list');
    const editModal = document.getElementById('editFightModal');
    const editFightForm = document.getElementById('editFightForm');

    if (!fightList || !editModal || !editFightForm) {
        return;
    }

    fightList.addEventListener('click', function (event) {
        if (event.target.classList.contains('editFight')) {
            event.preventDefault();
            const uuidFight = event.target.dataset.id;

            const fightDiv = event.target.closest('.fight');
            if (!fightDiv) {
                console.error("❌ Ошибка: Не найден элемент боя");
                return;
            }

            const numberFightElement = fightDiv.querySelector('.fight-number');
            const fighter1Element = fightDiv.querySelector('.fighter-1');
            const fighter2Element = fightDiv.querySelector('.fighter-2');

            if (!numberFightElement || !fighter1Element || !fighter2Element) {
                console.error("❌ Ошибка: Не найдены бойцы в DOM");
                return;
            }

            document.getElementById('editNumberFight').value = numberFightElement.textContent.trim();
            document.getElementById('editFighter1').value = fighter1Element.textContent.trim();
            document.getElementById('editFighter2').value = fighter2Element.textContent.trim();
            editFightForm.dataset.uuid = uuidFight;

            editModal.style.display = 'block';
        }
    });

    editFightForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(editFightForm);
        const uuidFight = editFightForm.dataset.uuid;

        fetch(`/edit/${uuidFight}/`, {
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
                editModal.style.display = 'none';
            } else {
                alert(data.error || 'Ошибка при редактировании боя.');
            }
        })
        .catch(error => {
            console.error('❌ Ошибка AJAX:', error);
            alert('Ошибка соединения');
        });
    });

    document.getElementById('closeEditFight')?.addEventListener('click', function () {
        editModal.style.display = 'none';
    });
});

