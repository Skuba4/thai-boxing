document.addEventListener("DOMContentLoaded", function () {
    // Создаём модальное окно для просмотра записок
    const notesModal = document.createElement("div");
    notesModal.classList.add("judge-note-modal"); // Используем те же стили
    notesModal.innerHTML = `
        <div id="round-links" class="button-container">
            <button class="round-btn" data-round="1">ЗАПИСКИ РАУНДА №1</button>
            <button class="round-btn" data-round="2">ЗАПИСКИ РАУНДА №2</button>
            <button class="round-btn" data-round="3">ЗАПИСКИ РАУНДА №3</button>
        </div>
        <div id="notes-content-wrapper">
            <div id="notes-content"></div> <!-- Здесь будут появляться записки -->
        </div>
        <div class="button-container">
            <button class="cancel-btn" id="close-notes-modal">Закрыть</button>
        </div>
    `;

    const overlay = document.createElement("div");
    overlay.classList.add("modal-overlay");

    document.body.appendChild(notesModal);
    document.body.appendChild(overlay);

    function closeNotesModal() {
        notesModal.style.display = "none";
        overlay.style.display = "none";
        document.getElementById("notes-content").innerHTML = ""; // Очищаем записи
    }

    overlay.addEventListener("click", closeNotesModal);
    document.getElementById("close-notes-modal").addEventListener("click", closeNotesModal);

    // Открываем модальное окно при клике на "Записки"
    document.querySelectorAll(".viewFightNotes").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const fightUUID = this.dataset.id;
            notesModal.dataset.fightUuid = fightUUID;
            notesModal.style.display = "flex";
            overlay.style.display = "block";
        });
    });

    // Загрузка записок по раунду при нажатии на кнопку
    document.querySelectorAll(".round-btn").forEach(button => {
        button.addEventListener("click", function () {
            const fightUUID = notesModal.dataset.fightUuid;
            const roundNumber = this.dataset.round;
            const notesContent = document.getElementById("notes-content");

            fetch(`/get_notes/${fightUUID}/${roundNumber}/`)
                .then(response => response.json())
                .then(data => {
                    console.log("Пришли данные:", data);  // Проверяем ответ от сервера

                    notesContent.innerHTML = `<h3 class="round-title">ЗАПИСКИ РАУНДА №${roundNumber}</h3>`; // Добавляем заголовок

                    if (data.success) {
                        data.notes.forEach(note => {
                            const winnerColor = note.winner === "Красный угол" ? "red" : "blue";

                            const noteBlock = document.createElement("div");
                            noteBlock.classList.add("judge-note-display");
                            noteBlock.innerHTML = `
                                <div class="form-group">
                                    <label>Дата:</label>
                                    <input type="date" value="${note.date}" readonly>
                                    <label>Раунд:</label>
                                    <input type="number" value="${note.round_number}" readonly>
                                    <label>Судья:</label>
                                    <input type="text" value="${note.judge}" class="long-input" readonly>
                                </div>
                                <hr>
                                <div class="corner-labels">
                                    <div class="red-corner">КРАСНЫЙ УГОЛ</div>
                                    <div class="vs-text">VS</div>
                                    <div class="blue-corner">СИНИЙ УГОЛ</div>
                                </div>
                                <div class="fighter-info">
                                    <input type="text" value="${note.red_fighter}" readonly>
                                    <input type="text" value="${note.blue_fighter}" readonly>
                                </div>
                                <table>
                                    <tr>
                                        <th>Замечания</th>
                                        <th>Раунд</th>
                                        <th>Замечания</th>
                                    </tr>
                                    <tr>
                                        <td><input type="text" value="${note.red_remark}" class="remark-input" readonly></td>
                                        <td><input type="number" value="${note.round_number}" readonly></td>
                                        <td><input type="text" value="${note.blue_remark}" class="remark-input" readonly></td>
                                    </tr>
                                </table>
                                <div class="winner-selection">
                                    <label>ПОБЕДИТЕЛЬ:</label>
                                    <span style="color: ${winnerColor}; font-weight: bold;">${note.winner}</span>
                                </div>
                            `;
                            notesContent.appendChild(noteBlock);
                        });
                    } else {
                        notesContent.innerHTML += "<p>Нет записок для этого раунда.</p>";
                    }
                })
                .catch(error => {
                    console.error("Ошибка загрузки записок:", error);
                    notesContent.innerHTML = "<p>Ошибка загрузки данных.</p>";
                });
        });
    });
});
