// Этот файл будет отвечать за все запросы к нашему бэкенду.

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000' // URL для локальной разработки
        : 'https://phraseweaver.fly.dev'; // Наш деплой на fly.io

// Глобальная переменная для токена. В более крупных приложениях это лучше хранить в классе или State Manager.
let authToken = null;

export function setAuthToken(token) {
    authToken = token;
}

async function request(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    console.log(`Sending request to ${endpoint}. Current token is:`, authToken);
    
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
        // Для ошибок тоже проверяем наличие контента
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API request failed');
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    }
    
    // Для успешных ответов проверяем наличие контента
    // Статус 204 No Content не имеет тела
    if (response.status === 204) {
        return null;
    }
    
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        return response.json();
    } 
    return null;
}

// Функции для каждого эндпоинта
export const api = {
    authenticate: (initData) => request('/auth/telegram', 'POST', { init_data: initData }),
    authenticateDebug: () => request('/auth/telegram/debug', 'POST'), 
    getDecks: () => request('/decks/'),
    createDeck: (deckData) => request('/decks/', 'POST', deckData),
    deleteDeck: (deckId) => request(`/decks/${deckId}`, 'DELETE'),
    enrichPhrase: (enrichData) => request('/cards/enrich', 'POST', enrichData),
    generateAudio: (audioData) => request('/cards/generate-audio', 'POST', audioData),
    saveCard: (cardData) => request('/cards/save', 'POST', cardData),
    // ... здесь будут другие методы API: getCards, etc.
};