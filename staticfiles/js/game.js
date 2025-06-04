document.addEventListener('DOMContentLoaded', function () {
    const roundTitle = document.getElementById('round-title');
    const totalScore = document.getElementById('score');
    const topicsContainer = document.getElementById('topics-container');
    const questionDisplay = document.getElementById('question-display');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');

    // Modal yaratish
    const resultModal = document.createElement('div');
    resultModal.id = 'result-modal';
    resultModal.className = 'modal';
    resultModal.innerHTML = `
        <div class="modal-content">
            <h2 id="result-title"></h2>
            <p id="result-message"></p>
            <button id="next-round-btn">Keyingi Raund</button>
            <button id="close-result">Yopish</button>
        </div>
    `;
    document.body.appendChild(resultModal);

    let currentRound = 1;
    let score = 0;
    let answeredQuestions = [];
    let currentTopicQuestions = [];
    let currentQuestionIndex = 0;
    let currentQuestion = null;

    function initGame() {
        loadRound(currentRound);
        updateScoreDisplay();
    }

    function loadRound(roundId) {
        fetch(`/api/rounds/${roundId}/`)
            .then(res => res.json())
            .then(round => {
                roundTitle.textContent = round.title;
                loadTopics(roundId);
            });
    }

    function loadTopics(roundId) {
        fetch(`/api/topics/?round=${roundId}`)
            .then(res => res.json())
            .then(topics => {
                topicsContainer.innerHTML = '';
                topics.forEach(topic => renderTopic(topic));
            });
    }

    function renderTopic(topic) {
        const topicEl = document.createElement('div');
        topicEl.className = 'topic-column';
        topicEl.innerHTML = `
            <h2>${topic.title}</h2>
            <div class="questions-grid" id="topic-${topic.id}-questions"></div>
        `;
        topicsContainer.appendChild(topicEl);
        loadQuestions(topic.id);
    }

    function loadQuestions(topicId) {
        fetch(`/api/questions/?topic=${topicId}`)
            .then(res => res.json())
            .then(questions => {
                const grid = document.getElementById(`topic-${topicId}-questions`);
                grid.innerHTML = '';
                questions.forEach(question => {
                    const btn = document.createElement('button');
                    btn.className = 'question-btn';
                    btn.textContent = question.score;
                    btn.dataset.questionId = question.id;
                    if (answeredQuestions.includes(question.id)) {
                        btn.disabled = true;
                        btn.classList.add('answered');
                    } else {
                        btn.addEventListener('click', () => {
                            startQuestionSequence(question, topicId);
                        });
                    }
                    grid.appendChild(btn);
                });
            });
    }

    function startQuestionSequence(question, topicId) {
        fetch(`/api/questions/?topic=${topicId}`)
            .then(res => res.json())
            .then(questions => {
                currentTopicQuestions = questions.filter(q => !answeredQuestions.includes(q.id));
                currentQuestionIndex = currentTopicQuestions.findIndex(q => q.id === question.id);
                showQuestion(currentTopicQuestions[currentQuestionIndex]);
            });
    }

    function showQuestion(question) {
        currentQuestion = question;
        questionText.textContent = question.text;
        optionsContainer.innerHTML = '';

        if (question.question_type === 'MC') {
            const options = [question.option_1, question.option_2, question.option_3];
            options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = 'option-btn';
                btn.textContent = opt;
                btn.dataset.option = opt;
                btn.addEventListener('click', function () {
                    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                    this.classList.add('selected');
                });
                optionsContainer.appendChild(btn);
            });
        } else {
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'text-answer';
            input.placeholder = 'Javobingizni kiriting...';
            optionsContainer.appendChild(input);
        }

        const submitBtn = document.createElement('button');
        submitBtn.id = 'submit-answer';
        submitBtn.textContent = 'Javob berish';
        submitBtn.addEventListener('click', submitAnswer);
        optionsContainer.appendChild(submitBtn);

        const passBtn = document.createElement('button');
        passBtn.id = 'pass-question';
        passBtn.textContent = 'Pas';
        passBtn.addEventListener('click', passQuestion);
        optionsContainer.appendChild(passBtn);

        const nextBtn = document.createElement('button');
        nextBtn.id = 'next-question';
        nextBtn.textContent = 'Keyingi savol';
        nextBtn.style.display = 'none';
        nextBtn.addEventListener('click', loadNextQuestion);
        optionsContainer.appendChild(nextBtn);

        questionDisplay.style.display = 'block';
    }

    function submitAnswer() {
        let answer;
        if (currentQuestion.question_type === 'MC') {
            const selected = document.querySelector('.option-btn.selected');
            if (!selected) {
                alert('Variant tanlang!');
                return;
            }
            answer = selected.dataset.option;
        } else {
            answer = document.getElementById('text-answer').value;
            if (!answer.trim()) {
                alert('Javobni kiriting!');
                return;
            }
        }

        fetch('/api/submit-answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                question_id: currentQuestion.id,
                selected_answer: answer
            })
        })
            .then(res => res.json())
            .then(data => {
                score += data.score_change;
                updateScoreDisplay();
                answeredQuestions.push(currentQuestion.id);
                showResult(data);
                document.getElementById('next-question').style.display = 'inline-block';
                document.getElementById('submit-answer').style.display = 'none';
                document.getElementById('pass-question').style.display = 'none';
            });
    }

    function passQuestion() {
        fetch('/api/submit-answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                question_id: currentQuestion.id,
                selected_answer: ''
            })
        })
            .then(res => res.json())
            .then(data => {
                answeredQuestions.push(currentQuestion.id);
                showResult(data);
                document.getElementById('next-question').style.display = 'inline-block';
                document.getElementById('submit-answer').style.display = 'none';
                document.getElementById('pass-question').style.display = 'none';
            });
    }

    function loadNextQuestion() {
        currentQuestionIndex++;
        if (currentQuestionIndex < currentTopicQuestions.length) {
            showQuestion(currentTopicQuestions[currentQuestionIndex]);
        } else {
            questionDisplay.style.display = 'none';
            checkRoundCompletion();
        }
    }

    function showResult(data) {
        const title = document.getElementById('result-title');
        const message = document.getElementById('result-message');

        if (data.result === 'correct') {
            title.textContent = "To'g'ri!";
            message.textContent = `+${data.score_change} ball.`;
        } else if (data.result === 'incorrect') {
            title.textContent = "Noto‘g‘ri!";
            message.textContent = `-${Math.abs(data.score_change)} ball. To‘g‘ri javob: ${currentQuestion.correct_answer}`;
        } else {
            title.textContent = "Pas";
            message.textContent = `To‘g‘ri javob: ${currentQuestion.correct_answer}`;
        }

        resultModal.style.display = 'block';
    }

    function checkRoundCompletion() {
        fetch(`/api/rounds/${currentRound}/questions-count/`)
            .then(res => res.json())
            .then(data => {
                if (answeredQuestions.length >= data.total_questions) {
                    if (currentRound < 3) {
                        document.getElementById('next-round-btn').style.display = 'block';
                        document.getElementById('close-result').style.display = 'none';
                    } else {
                        showFinalResults();
                    }
                } else {
                    resultModal.style.display = 'none';
                }
            });
    }

    function showFinalResults() {
        fetch('/api/save-score/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ score: score })
        }).then(() => {
            document.getElementById('result-title').textContent = "O'yin tugadi!";
            document.getElementById('result-message').textContent = `Yakuniy ball: ${score}`;
            document.getElementById('next-round-btn').style.display = 'none';
            const closeBtn = document.getElementById('close-result');
            closeBtn.style.display = 'block';
            closeBtn.textContent = 'Yakunlash';
            resultModal.style.display = 'block';
        });
    }

    function updateScoreDisplay() {
        totalScore.textContent = score;
        if (score < 0) {
            totalScore.classList.add('negative-score');
        } else {
            totalScore.classList.remove('negative-score');
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.getElementById('close-result').addEventListener('click', () => {
        resultModal.style.display = 'none';
    });

    document.getElementById('next-round-btn').addEventListener('click', () => {
        currentRound++;
        answeredQuestions = [];
        resultModal.style.display = 'none';
        loadRound(currentRound);
    });

    initGame();
});

document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('profile-btn');
    const dropdown = document.getElementById('profile-dropdown');

    btn.addEventListener('click', function(e) {
        e.preventDefault();
        dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
    });

    document.addEventListener('mousedown', function(e) {
        if (!dropdown.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
});