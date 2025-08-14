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

    // TODO: Auth, fetch decks
});