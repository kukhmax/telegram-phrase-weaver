// Этот файл будет отвечать за все запросы к нашему бэкенду.

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000' // URL для локальной разработки
        : 'https://phrase-weaver-jpcj.onrender.com'; // ЗАМЕНИТЕ НА ВАШ URL

// Глобальная переменная для токена. В более крупных приложениях это лучше хранить в классе или State Manager.
let authToken = null;

export function setAuthToken(token) {
    authToken = token;
}

async function request(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
    };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const options = {
        method,
        headers,
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'API request failed');
    }
    // Если у ответа нет тела (например, для статуса 204), json() вызовет ошибку
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        return response.json();
    } 
    return null; // или response.text() если нужно
}

// Функции для каждого эндпоинта
export const api = {
    authenticate: (initData) => request('/auth/telegram', 'POST', { init_data: initData }),
    getDecks: () => request('/decks/'),
    createDeck: (deckData) => request('/decks/', 'POST', deckData),
    // ... здесь будут другие методы API: deleteDeck, getCards, etc.
};