// === Quiz Game Frontend Logic ===

// --- Elements ---
const quizModal = document.getElementById('quizModal');
const reytingModal = document.getElementById('reyting-modal');
const playAgainModal = document.getElementById('play-again-modal');
const startQuizBtn = document.getElementById('startQuizBtn');
const modalBody = document.getElementById('modal-body');


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// --- Open Quiz Modal ---
startQuizBtn.addEventListener('click', () => {
    quizModal.style.display = 'block';
    loadRounds();
});

// --- Close Quiz Modal ---
document.querySelectorAll('.close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        quizModal.style.display = 'none';
        // Agar boshqa modal bo'lsa, ularni ham yopamiz
        const topicModal = document.getElementById('topicModal');
        if (topicModal) topicModal.style.display = 'none';
    });
});

// --- Load Rounds List ---
function loadRounds() {
    fetch('/api/rounds/')
        .then(response => response.json())
        .then(rounds => {
            let html = '<ul class="round-list">';
            rounds.forEach(round => {
                html += `
                    <li>
                        <button class="round-btn" onclick="tryStartRound(${round.id})">
                            ${round.order} - ${round.title}
                        </button>
                    </li>
                `;
            });
            html += '</ul>';
            modalBody.innerHTML = html;
        })
        .catch(error => {
            modalBody.innerHTML = `<div class="error">Error loading rounds</div>`;
            console.error('Error:', error);
        });
}

// --- Try Start Round: check if played, then show modal or start ---
window.tryStartRound = function(roundId) {
    fetch(`/api/check-user-round/?round=${roundId}`)
        .then(res => res.json())
        .then(data => {
            if (data.already_played) {
                showPlayAgainModal(() => {
                    startUserRound(roundId);
                });
            } else {
                startUserRound(roundId);
            }
        })
        .catch(() => {
            alert("Error: could not check round status.");
        });
};

// --- Actually Start Round: open session and redirect ---
function startUserRound(roundId) {
    fetch(`/api/start-user-round/?round=${roundId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    })
    .then(data => {
        window.location.href = `/game/?round=${roundId}`;
    })
    .catch(() => {
        alert("Error: could not start round");
    });
}

// --- Play Again Modal Logic ---
function showPlayAgainModal(onPlayAgain) {
    playAgainModal.style.display = 'flex';

    document.getElementById('play-again-confirm').onclick = () => {
        playAgainModal.style.display = 'none';
        if (typeof onPlayAgain === "function") onPlayAgain();
    };
    document.getElementById('play-again-cancel').onclick = () => {
        playAgainModal.style.display = 'none';
    };
    document.getElementById('close-play-again-modal').onclick = () => {
        playAgainModal.style.display = 'none';
    };
    playAgainModal.onclick = function (e) {
        if (e.target === this) playAgainModal.style.display = 'none';
    }
}

// --- Reyting Modal Logic ---
document.getElementById('open-reyting-modal').onclick = function (e) {
    e.preventDefault();
    reytingModal.style.display = 'flex';
    fetchReyting();
};
document.getElementById('close-reyting-modal').onclick = function () {
    reytingModal.style.display = 'none';
};
reytingModal.onclick = function (e) {
    if (e.target === this) reytingModal.style.display = 'none';
};

// --- Load Reyting via AJAX ---
function fetchReyting() {
    const content = document.getElementById('reyting-content');
    content.innerHTML = '<div class="loading">Loading...</div>';
    fetch('/api/top-reyting/')
        .then(res => res.json())
        .then(data => {
            if (!data.length) {
                content.innerHTML = "<div style='text-align:center;color:#ccc'>No rankings yet</div>";
                return;
            }
            content.innerHTML = `<ul class="reyting-list">` +
                data.map((item, idx) => `
                    <li class="reyting-item">
                        <span class="reyting-rank">${idx + 1}</span>
                        <span class="reyting-username">${item.full_name || item.username}</span>
                        <span class="reyting-score">${item.score}</span>
                    </li>
                `).join('') +
                `</ul>`;
        })
        .catch(() => {
            content.innerHTML = "<div class='loading'>Error: failed to load ranking</div>";
        });
}

// --- Global ESC key closes all modals ---
window.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        [quizModal, reytingModal, playAgainModal].forEach(modal => {
            if (modal && modal.style.display !== 'none') modal.style.display = 'none';
        });
    }
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