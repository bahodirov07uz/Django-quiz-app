// === JAVASCRIPT FRONTEND CODE ===
const urlParams = new URLSearchParams(window.location.search);
const roundId = urlParams.get('round');

const topicsContainer = document.getElementById('topics-container');
const scoreDisplay = document.getElementById('score');
const questionDisplay = document.getElementById('question-display');
const questionText = document.getElementById('question-text');
const optionsContainer = document.getElementById('options-container');
let userRoundId = null;
let currentButton = null;
let currentQuestion = null;
let totalQuestions = 0;
let answeredQuestions = 0;
let settings = {
    questionAdvance: localStorage.getItem("questionAdvance") || "auto" // yoki "next"
};

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}


function showQuestion(question, button) {
    currentButton = button;
    currentQuestion = question;

    questionDisplay.style.display = 'block';
    questionText.innerHTML = '';
    optionsContainer.innerHTML = '';
    optionsContainer.classList.remove('correct-answer-bg'); // old bg ni tozalash

    const textEl = document.createElement('div');
    textEl.textContent = question.text;
    textEl.style.marginBottom = '10px';
    questionText.appendChild(textEl);
    questionStartTime = Date.now();

    // ==== Rasm logikasi (o'zgarmaydi) ====
    let multiImageMode = Array.isArray(question.image_urls) && question.image_urls.length > 1;
    let imgRow = null;
    if (multiImageMode) {
        imgRow = document.createElement('div');
        imgRow.className = 'img-row';
        questionText.appendChild(imgRow);
        const img = document.createElement('img');
        img.src = question.image_urls[0];
        img.alt = "Question image";
        img.className = 'question-image row-image';
        imgRow.appendChild(img);
    } else if (Array.isArray(question.image_urls) && question.image_urls.length === 1) {
        const img = document.createElement('img');
        img.src = question.image_urls[0];
        img.alt = "Question image";
        img.className = 'question-image row-image';
        questionText.appendChild(img);
    } else if (question.image_url) {
        const img = document.createElement('img');
        img.src = question.image_url;
        img.alt = "Question image";
        img.className = 'question-image';
        questionText.appendChild(img);
    }

    if (question.audio_url) {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = question.audio_url;
        audio.className = 'question-audio';
        questionText.appendChild(audio);
    }

    optionsContainer.dataset.answered = "false";

    // === TEXT TURIDAGI SAVOLLAR UCHUN ===
    if (question.type === 'text') {
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Enter your answer';
        input.className = 'text-answer-input';
        optionsContainer.appendChild(input);

        const submitBtn = document.createElement('button');
        submitBtn.textContent = 'Submit';
        submitBtn.className = 'option-btn submit-btn';
        submitBtn.onclick = () => {
            const userInput = input.value.trim();
            if (userInput === '') {
                alert("Please enter your answer.");
                return;
            }
            submitAnswer(userInput, input, submitBtn, multiImageMode, question, imgRow);
        };
        optionsContainer.appendChild(submitBtn);

        // PASS (SKIP) BUTTON
        const passBtn = document.createElement('button');
        passBtn.className = 'option-btn pass-btn';
        passBtn.textContent = 'Skip';
        passBtn.onclick = () => submitAnswer(null, input, passBtn, multiImageMode, question, imgRow);
        optionsContainer.appendChild(passBtn);

    } else {
        const options = [...question.options];
        options.sort(() => Math.random() - 0.5);

        options.forEach((opt, index) => {
            const optionBtn = document.createElement('button');
            optionBtn.className = 'option-btn';
            optionBtn.innerHTML = `<span class="option-letter">${String.fromCharCode(65 + index)}.</span> ${opt}`;
            optionBtn.onclick = () => submitAnswer(opt, null, optionBtn, multiImageMode, question, imgRow);
            optionsContainer.appendChild(optionBtn);
        });

        const passBtn = document.createElement('button');
        passBtn.className = 'option-btn pass-btn';
        passBtn.textContent = 'Skip';
        passBtn.onclick = () => submitAnswer(null, null, passBtn, multiImageMode, question, imgRow);
        optionsContainer.appendChild(passBtn);
    }

    // Next tugmasi dastlab ko‘rinmaydi
    let nextBtn = document.createElement('button');
    nextBtn.className = 'option-btn next-btn';
    nextBtn.textContent = 'Next';
    nextBtn.style.marginTop = "10px";
    nextBtn.style.display = "none";
    nextBtn.onclick = showNextUnansweredQuestion;
    optionsContainer.appendChild(nextBtn);
}

// settings globalda yoki yuqorida e'lon qilinadi
// let settings = { questionAdvance: "auto" }  // yoki "next"


// Yashil bg uchun CSS (oq emas, chiroyli va aniq)
if (!document.getElementById('custom-correct-style')) {
    const style = document.createElement('style');
    style.id = "custom-correct-style";
    style.textContent = `
    .correct-answer-bg {
        background: linear-gradient(90deg, #1a1a1a 0%, #1a1a1a 100%) !important;
        border-radius: 15px;
        box-shadow: 0 0 0 2px #1a1a1a;
        transition: background 0.18s, box-shadow 0.18s;
    }
        `;
    document.head.appendChild(style);
}


function saveUserRound(roundId, score) {
    const roundTimeSpent = Date.now() - roundStartTime;
    fetch('/api/save-user-round/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            round_id: roundId,
            score: score,
            end: true,
            time_spent: roundTimeSpent,
            user_round_id: userRoundId,
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'created' || data.status === 'updated') {
                showToastMessage("Congratulations! Your best score was updated: " + data.score, "success");
            } else {
                showToastMessage("You have already completed this round. Best score: " + data.score, "info");
            }
        })
        .catch(() => {
            showToastMessage("An error occurred. Please try again.", "error");
        });
}

function showToastMessage(message, type = "success") {
    // Type: success, info, warning, error
    const old = document.querySelector('.custom-toast');
    if (old) old.remove();

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;

    // Icons
    let icon = "";
    if (type === "success") icon = "✅";
    else if (type === "info") icon = "ℹ️";
    else if (type === "warning") icon = "⚠️";
    else if (type === "error") icon = "❌";

    toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-msg">${message}</span>
        `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3200);
}

// CSS is only added once
if (!document.getElementById('custom-toast-style')) {
    const style = document.createElement('style');
    style.id = "custom-toast-style";
    style.textContent = `
    .custom-toast {
        position: fixed;
        top: 22px;
        left: 50%;
        transform: translateX(-50%) scale(0.96);
        min-width: 220px;
        max-width: 90vw;
        background: #23213a;
        color: #fff;
        border-radius: 14px;
        box-shadow: 0 8px 32px #0006;
        font-size: 1.07rem;
        font-weight: 500;
        z-index: 99999;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 22px;
        opacity: 0;
        pointer-events: none;
        transition: all 0.33s cubic-bezier(.68,-0.55,.27,1.55);
        border: 2px solid #382e7a;
    }
    .custom-toast .toast-icon { font-size: 1.3em; }
    .custom-toast.success { border-color: #2ecc40; }
    .custom-toast.error { border-color: #ff4545; }
    .custom-toast.warning { border-color: #ffc107; color: #fff3cd; }
    .custom-toast.info { border-color: #17a2b8; }
    .custom-toast.show {
        opacity: 1;
        pointer-events: all;
        transform: translateX(-50%) scale(1);
    }
    @media (max-width: 480px) {
        .custom-toast { font-size: 0.99rem; min-width: 140px; padding: 9px 8vw; }
    }
        `;
    document.head.appendChild(style);
}


function submitAnswer(selected, textInput = null, pressedBtn = null, multiImageMode = false, question = null, imgRow = null) {
    const csrfToken = getCookie('csrftoken');
    const timeSpentMs = Date.now() - questionStartTime;
    let btns = optionsContainer.querySelectorAll('.option-btn:not(.next-btn)');

    fetch('/api/submit-answer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            question_id: currentQuestion.question_id,
            selected_answer: selected,
            time_spent: timeSpentMs,
            user_round_id: userRoundId,
        })
    })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) throw new Error(data.error || 'An error occurred.');

            updateScore(data.score_change, data.user_round_score);
            console.log(data.score_change)
            showMessage(data.result, data.correct_answer, data.result === 'correct');
            if (currentButton) {
                currentButton.disabled = true;
                currentButton.classList.add('answered');
            }
            let roundKey = 'answered_' + roundId;
            let answered = JSON.parse(sessionStorage.getItem(roundKey) || "[]");
            if (!answered.includes(currentQuestion.question_id)) {
                answered.push(currentQuestion.question_id);
                sessionStorage.setItem(roundKey, JSON.stringify(answered));
            }
            if (data.result === 'correct') {
                optionsContainer.classList.add('correct-answer-bg');
            } else {
                optionsContainer.classList.remove('correct-answer-bg');
            }
            if (currentQuestion.type !== 'text') {
                let btns = optionsContainer.querySelectorAll('.option-btn:not(.next-btn)');
                btns.forEach(btn => {
                    let btnText = btn.innerText.replace(/^[A-Z]\.\s*/, '').trim();
                    if (btn.classList.contains('pass-btn')) {
                        if (data.result === 'passed') btn.classList.add('skipped');
                    } else if (btnText === data.correct_answer) {
                        btn.classList.add('correct');
                    } else if (btnText === selected && data.result === 'incorrect') {
                        btn.classList.add('incorrect');
                    }
                });
            } else {
                let passBtn = optionsContainer.querySelector('.pass-btn');
                if (data.result === 'passed' && passBtn) passBtn.classList.add('skipped');
            }
            // === 2. Ikkinchi rasmni ko‘rsatish ===
            // === 2. Ikkinchi rasmni ko‘rsatish ===
            if (multiImageMode && question && Array.isArray(question.image_urls) && question.image_urls.length > 1) {
                if (imgRow) {
                    imgRow.innerHTML = ''; // eski rasm(lar)ni o'chirish
                    const img2 = document.createElement('img');
                    img2.src = question.image_urls[1];
                    img2.alt = "Question image 2";
                    img2.className = 'question-image row-image';
                    imgRow.appendChild(img2);
                }
            }



            // === 3. Submit va inputni YASHIRISH ===
            if (pressedBtn && pressedBtn.classList.contains('submit-btn')) {
                pressedBtn.style.display = 'none';
            }
            if (textInput) textInput.style.display = 'none';

            // Barcha boshqa option/pass tugmalarni disable qilamiz
            let btns = optionsContainer.querySelectorAll('.option-btn:not(.next-btn)');
            btns.forEach(btn => btn.disabled = true);
            // "Skip" tugmasini ham yashiramiz
            let passBtn = optionsContainer.querySelector('.pass-btn');
            if (passBtn) passBtn.style.display = 'none';

            if (currentButton) currentButton.classList.add("answered");

            let nextBtn = optionsContainer.querySelector('.next-btn');

            // === SHU QISIM MUHIM ===
            if (settings.questionAdvance === "auto") {
                // Avtomatik keyingi savol
                if (nextBtn) nextBtn.style.display = "none";
                setTimeout(showNextUnansweredQuestion, 2000); // 0.7s delay for UX
            } else {
                // Next tugmasi ishlaydi
                if (nextBtn) {
                    nextBtn.disabled = false;
                    nextBtn.style.display = "inline-block";
                }
            }
            // === /SHU QISIM MUHIM ===

            answeredQuestions++;
            if (answeredQuestions === totalQuestions) {
                setTimeout(showFinalModal, 500);
            }
        })
        .catch(err => {
            console.error('Error submitting answer:', err.message);
            showError(err.message);
        });
}

// Yashil fon uchun CSS qo‘shing
if (!document.getElementById('custom-correct-style')) {
    const style = document.createElement('style');
    style.id = "custom-correct-style";
    style.textContent = `
    .correct-answer-bg {
        background: linear-gradient(90deg, #eaffed 0%, #b0edc4 100%) !important;
        transition: background 0.18s;
    }
        `;
    document.head.appendChild(style);
}

function showNextUnansweredQuestion() {
    const buttons = document.querySelectorAll('.question-btn');
    for (let btn of buttons) {
        if (!btn.classList.contains("answered")) {
            btn.click();
            return;
        }
    }
}

function updateScore(change, total) {
    scoreDisplay.textContent = total;
}


async function ensureUserRound(roundId) {
    // Avval sessionStoragedan tekshiramiz
    userRoundId = sessionStorage.getItem('user_round_id_' + roundId);

    // Agar topilmasa, yangi yaratamiz
    if (!userRoundId) {
        try {
            const response = await fetch(`/api/start-user-round/?round=${roundId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            userRoundId = data.user_round_id;
            sessionStorage.setItem('user_round_id_' + roundId, userRoundId);
            console.log('Yangi UserRound yaratildi:', userRoundId);
        } catch (error) {
            console.error('UserRound yaratishda xato:', error);
            throw error; // Yuqori levelda ushlab olish uchun
        }
    }

    return userRoundId; // Muhim: userRoundId qaytarilishi kerak
}

console.log('UserRound ID:', userRoundId, 'Round ID:', roundId);

// Yangi UserRound yaratish (yoki mavjudini qayta olish)
function startUserRound(roundId) {
    return fetch(`/api/start-user-round/?round=${roundId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
        .then(res => res.json())
        .then(data => {
            userRoundId = data.user_round_id;
            sessionStorage.setItem('user_round_id_' + roundId, userRoundId);
            console.log('UserRound created:', userRoundId); // <-- LOG QILING!
        });
}

// O'yin ma'lumotlarini yuklash va UserRound yaratilganiga ishonch hosil qilish
function loadGameData() {
    roundStartTime = Date.now();
    ensureUserRound(roundId).then(() => {
        fetch(`/api/topics/?round=${roundId}`)
            .then(res => res.json())
            .then(topics => {
                return Promise.all(
                    topics.map(topic =>
                        fetch(`/api/questions/?topic=${topic.id}`)
                            .then(res => res.json())
                            .then(questions => ({ topic, questions }))
                    )
                );
            })
            .then(allData => {
                totalQuestions = allData.reduce((sum, { questions }) => sum + questions.length, 0);
                renderGameBoard(allData);
            })
            .catch(err => {
                console.error("Error loading data:", err);
                topicsContainer.innerHTML = `<div class="error">Error: ${err.message}</div>`;
            });
    });
}

function renderGameBoard(allData) {
    topicsContainer.innerHTML = '';
    let roundKey = 'answered_' + roundId;
    let answered = JSON.parse(sessionStorage.getItem(roundKey) || "[]");
    answeredQuestions = answered.length;
    totalQuestions = allData.reduce((sum, { questions }) => sum + questions.length, 0);

    if (answeredQuestions === totalQuestions && totalQuestions > 0) {
        setTimeout(showFinalModal, 200);
        return
    }

    allData.forEach(({ topic, questions }) => {
        const row = document.createElement('div');
        row.className = 'topic-row';

        const label = document.createElement('div');
        label.className = 'topic-label';
        label.textContent = topic.title;
        row.appendChild(label);

        questions.sort((a, b) => a.score - b.score).forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'question-btn';
            btn.textContent = q.score;
            // Agar javob berilgan bo‘lsa, disable qilamiz:
            if (answered.includes(q.id)) {
                btn.classList.add("answered");
                btn.disabled = true;
            }
            btn.onclick = () => {
                if (btn.disabled) return; // Bosib bo‘lmaydi
                fetch(`/api/submit-answer/?question=${q.id}`)
                    .then(res => res.json())
                    .then(data => {
                        showQuestion(data, btn);
                    });
            };
            row.appendChild(btn);
        });

        topicsContainer.appendChild(row);
    });
}

function showFinalModal() {
    const modal = document.createElement('div');
    modal.className = 'final-modal';
    modal.innerHTML = `
            <div class="modal-content">
                <h2>Game Over 🎉</h2>
                <p>Congratulations! You have answered all the questions.</p>
                <div class="modal-buttons">
                    <button class="modal-btn" onclick="window.location.href='/'">🏠 Home</button>
                    <button class="modal-btn" onclick="goToNextRound()">➡️ Next round</button>
                </div>
            </div>
        `;
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('active');
    }, 50);
    saveUserRound(roundId, parseInt(scoreDisplay.textContent || "0"));
    let roundKey = 'answered_' + roundId;
    sessionStorage.removeItem(roundKey);
    saveUserRound(roundId, parseInt(scoreDisplay.textContent || "0"));
    sessionStorage.removeItem('user_round_id_' + roundId);
}
function goToNextRound() {
    fetch('/api/rounds/')
        .then(res => res.json())
        .then(rounds => {
            const nextRound = parseInt(roundId) + 1;
            const roundExists = rounds.some(r => r.id === nextRound);
            if (roundExists) {
                window.location.href = `?round=${nextRound}`;
            } else {
                showNoNextRoundModal();
            }
        })
        .catch(err => {
            console.error("Error checking next round:", err);
            alert("An error occurred while checking for the next round.");
        });
}
function showNoNextRoundModal() {
    const modal = document.createElement('div');
    modal.className = 'final-modal';
    modal.innerHTML = `
            <div class="modal-content">
                <h2>You have reached the last round 👏</h2>
                <p>All available rounds have been completed.</p>
                <div class="modal-buttons">
                    <button class="modal-btn" onclick="window.location.href='/'">🏠 Home</button>
                </div>
            </div>
        `;
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('active');
    }, 50);
}

// === MESSAGE DISPLAY FUNCTIONS ===

function showMessage(result, correctAnswer, isCorrect) {
    const messageBox = document.createElement('div');
    messageBox.className = `message-box ${result}`;
    let icon, text;
    switch (result) {
        case 'correct':
            icon = '✅';
            text = 'Correct!';
            break;
        case 'incorrect':
            icon = '❌';
            text = 'Incorrect!';
            break;
        case 'passed':
            icon = '⏭️';
            text = 'Skipped';
            break;
    }

    messageBox.innerHTML = `
            <div class="message-content">
                <span class="message-icon">${icon}</span>
                <span class="message-text">${text}</span>
                <div class="correct-answer">Correct answer: ${correctAnswer}</div>
            </div>
        `;

    document.body.appendChild(messageBox);

    setTimeout(() => {
        messageBox.classList.add('show');
    }, 10);

    setTimeout(() => {
        messageBox.classList.remove('show');
        setTimeout(() => {
            messageBox.remove();
        }, 400);
    }, 3000);
}


// === ERROR MESSAGE DISPLAY ===

function showError(message) {
    const errorBox = document.createElement('div');
    errorBox.className = 'message-box error';
    errorBox.innerHTML = `
            <div class="message-content">
                <span class="message-icon">⚠️</span>
                <span class="message-text">${message}</span>
            </div>
        `;

    document.body.appendChild(errorBox);

    setTimeout(() => {
        errorBox.classList.add('show');
    }, 10);

    setTimeout(() => {
        errorBox.classList.remove('show');
        setTimeout(() => {
            errorBox.remove();
        }, 300);
    }, 3000);
}

window.addEventListener('DOMContentLoaded', loadGameData);

