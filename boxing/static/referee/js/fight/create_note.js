document.addEventListener("DOMContentLoaded", function () {
    const modal = document.createElement("div");
    modal.classList.add("judge-note-modal");
    modal.innerHTML = `
        <h2>СУДЕЙСКАЯ ЗАПИСКА</h2>
        <div class="form-group">
            <label>Дата:</label>
            <input type="date" id="note-date" readonly>
            <label>Бой №:</label>
            <input type="number" id="note-fight-number" readonly>
            <label>Судья:</label>
            <input type="text" id="note-judge" class="long-input" readonly>
        </div>
        <hr>
        <div class="corner-labels">
            <div class="red-corner">КРАСНЫЙ УГОЛ</div>
            <div class="vs-text">VS</div>
            <div class="blue-corner">СИНИЙ УГОЛ</div>
        </div>
        <div class="fighter-info">
            <input type="text" id="note-red-fighter" readonly>
            <input type="text" id="note-blue-fighter" readonly>
        </div>
        <table>
            <tr>
                <th>Замечания</th>
                <th>Раунд</th>
                <th>Замечания</th>
            </tr>
            <tr>
                <td><input type="text" id="note-red-remark" class="remark-input"></td>
                <td><input type="number" id="note-round" readonly></td>
                <td><input type="text" id="note-blue-remark" class="remark-input"></td>
            </tr>
        </table>
        <div class="winner-selection">
            <label for="note-winner">ВЫБЕРИ ПОБЕДИТЕЛЯ:</label>
            <select id="note-winner">
                <option value="" selected disabled>-- Выбери победителя --</option>
                <option value="red">Красный угол</option>
                <option value="blue">Синий угол</option>
            </select>
        </div>
        <div class="button-container">
            <button class="save-btn" id="save-note">Сохранить</button>
            <button class="cancel-btn" id="cancel-note">Отмена</button>
        </div>
    `;

    const overlay = document.createElement("div");
    overlay.classList.add("modal-overlay");

    document.body.appendChild(modal);
    document.body.appendChild(overlay);

    // Функция очистки формы
    function resetForm() {
        document.getElementById("note-red-remark").value = "";
        document.getElementById("note-blue-remark").value = "";
        document.getElementById("note-winner").value = ""; // Сброс выбора победителя
    }

    // Функция закрытия формы
    function closeModal() {
        resetForm();
        modal.style.display = "none";
        overlay.style.display = "none";
    }

    // Открытие модального окна
    document.querySelectorAll(".viewNotes").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const fightUUID = this.dataset.id;
            const roundNumber = this.dataset.round;

            const fightElement = document.querySelector(`.fight[data-fight-id="${fightUUID}"]`);
            const fightNumber = fightElement.querySelector(".fight-number").textContent;
            const redFighter = fightElement.querySelector(".fighter-1").textContent;
            const blueFighter = fightElement.querySelector(".fighter-2").textContent;

            // Подставляем данные
            document.getElementById("note-date").value = new Date().toISOString().split("T")[0];
            document.getElementById("note-round").value = roundNumber;
            document.getElementById("note-fight-number").value = fightNumber;
            document.getElementById("note-red-fighter").value = redFighter;
            document.getElementById("note-blue-fighter").value = blueFighter;
            document.getElementById("note-judge").value = document.querySelector(".user").textContent.trim();

            modal.dataset.fightUuid = fightUUID;
            modal.style.display = "flex";
            overlay.style.display = "block";
        });
    });

    // Закрытие модального окна (кнопка Отмена)
    document.getElementById("cancel-note").addEventListener("click", closeModal);

    // Закрытие модального окна (клик на overlay)
    overlay.addEventListener("click", closeModal);

    // Отправка формы через AJAX
    document.getElementById("save-note").addEventListener("click", function () {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        const fightUUID = modal.dataset.fightUuid;

        const winnerSelect = document.getElementById("note-winner");
        if (winnerSelect.value === "") {
            alert("Выбери победителя!");
            return;
        }

        const data = {
            fight_id: fightUUID,
            round: document.getElementById("note-round").value,
            judge: document.getElementById("note-judge").value,
            red_fighter: document.getElementById("note-red-fighter").value,
            blue_fighter: document.getElementById("note-blue-fighter").value,
            red_remark: document.getElementById("note-red-remark").value,
            blue_remark: document.getElementById("note-blue-remark").value,
            winner: winnerSelect.value,
        };

        fetch("/save_note/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeModal(); // ✅ Закрываем форму без alert'а
            } else {
                alert("Ошибка сохранения");
            }
        });
    });
});
