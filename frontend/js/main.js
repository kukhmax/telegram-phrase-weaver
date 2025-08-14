document.addEventListener('DOMContentLoaded', () => {
    const WebApp = window.Telegram.WebApp;
    WebApp.ready(); // Init Telegram
    WebApp.expand(); // Full screen

    // Dynamic API URL
    const API_URL = window.location.hostname.includes('onrender') ? 'https://your-app.onrender.com' : 'http://localhost:8000';

    // Screens toggle func
    function showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => screen.classList.remove('active'));
        document.getElementById(screenId).classList.add('active');
    }

    // Header events
    document.getElementById('stats-btn').addEventListener('click', () => showScreen('stats-screen'));
    document.getElementById('settings-btn').addEventListener('click', () => showScreen('settings-screen'));

    // + button
    document.getElementById('create-deck-btn').addEventListener('click', () => showScreen('create-deck-screen')); // TODO: Add div


    let token = localStorage.getItem('access_token');

    async function authenticate() {
        if (!token) {
            const initData = WebApp.initData; // Safe string
            const response = await fetch(`${API_URL}/auth/telegram`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ init_data: initData })
            });
            if (response.ok) {
                const data = await response.json();
                token = data.access_token;
                localStorage.setItem('access_token', token);
            } else {
                alert('Auth failed');
            }
        }
    }

    async function fetchDecks() {
        await authenticate(); // Ensure token
        const response = await fetch(`${API_URL}/decks`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const decks = await response.json();
            renderDecks(decks);
        } else {
            alert('Fetch decks failed');
        }
    }

    function renderDecks(decks) {
        const list = document.getElementById('decks-list');
        list.innerHTML = '';
        if (decks.length === 0) {
            list.innerHTML = '<p class="no-decks">Здесь появятся ваши колоды</p>';
            return;
        }
        decks.forEach(deck => {
            const card = document.createElement('div');
            card.className = 'deck-card';
            card.innerHTML = `
                <div class="deck-info">
                    <h3>${deck.name}</h3>
                    <p>${deck.description || ''}</p>
                    <p>${getFlag(deck.lang_from)} ${deck.lang_from} → ${getFlag(deck.lang_to)} ${deck.lang_to}</p>
                    <p>Total: ${deck.cards_count} | Repeat: ${deck.due_count}</p>
                </div>
                <div class="deck-buttons">
                    <button class="deck-btn btn-cards">Карточки</button>
                    <button class="deck-btn btn-train">Тренировки</button>
                    <button class="deck-btn btn-delete">Удалить</button>
                </div>
            `;
            // Events
            card.addEventListener('click', () => showGenerateScreen(deck.id)); // TODO: Impl screen
            card.querySelector('.btn-cards').addEventListener('click', (e) => { e.stopPropagation(); showCardsPopup(deck.id); });
            card.querySelector('.btn-train').addEventListener('click', (e) => { e.stopPropagation(); showTrainScreen(deck.id); });
            card.querySelector('.btn-delete').addEventListener('click', (e) => { e.stopPropagation(); deleteDeck(deck.id); });
            list.appendChild(card);
        });
    }

    function getFlag(lang) {
        const flags = { pt: '🇵🇹', fr: '🇫🇷', en: '🇺🇸', pl: '🇵🇱', ru: '🇷🇺' /* add more */ };
        return flags[lang] || '';
    }

    async function deleteDeck(id) {
        if (confirm('Удалить колоду?')) {
            const response = await fetch(`${API_URL}/decks/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) fetchDecks();
        }
    }

    // TODO: Functions for showCardsPopup (modal), showGenerateScreen, showTrainScreen

    // On load
    fetchDecks();
});