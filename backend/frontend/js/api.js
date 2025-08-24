// Этот файл будет отвечать за все запросы к нашему бэкенду.

// Определяем базовый URL в зависимости от окружения
const API_BASE_URL = (window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1') 
                     ? 'http://localhost:8000' 
                     : 'https://pw-new.club';

// Функции для работы с токенами
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

function setAuthToken(token) {
    if (token) {
        localStorage.setItem('auth_token', token);
    } else {
        localStorage.removeItem('auth_token');
    }
}

function getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
}

function setUserData(userData) {
    if (userData) {
        localStorage.setItem('user_data', JSON.stringify(userData));
    } else {
        localStorage.removeItem('user_data');
    }
}

export { setAuthToken, getUserData };

async function request(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    const token = getAuthToken();
    console.log(`Sending request to ${endpoint}. Current token is:`, token ? 'present' : 'missing');
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers,
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    console.log(`Received response from ${endpoint}. Status:`, response.status);

    // Если токен истек, пробуем обновить авторизацию
    if (response.status === 401) {
        console.log('Token expired, trying to re-authenticate...');
        try {
            await authenticateUser();
            // Повторяем запрос с новым токеном
            const newToken = getAuthToken();
            if (newToken) {
                headers['Authorization'] = `Bearer ${newToken}`;
                const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
                if (retryResponse.ok) {
                    return retryResponse;
                }
            }
        } catch (authError) {
            console.error('Re-authentication failed:', authError);
            throw new Error('Ошибка авторизации. Перезапустите приложение.');
        }
    }

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

// Функция авторизации через Telegram WebApp
async function authenticateUser() {
    try {
        // Проверяем, запущено ли в Telegram WebApp
        const isTelegramWebApp = window.Telegram?.WebApp?.initData;
        
        console.log('Authentication context:', {
            hostname: window.location.hostname,
            isTelegramWebApp: !!isTelegramWebApp,
            telegramWebApp: !!window.Telegram?.WebApp
        });
        
        if (isTelegramWebApp) {
            // Telegram WebApp авторизация
            console.log('Authenticating with Telegram WebApp...');
            
            const initData = window.Telegram.WebApp.initData;
            const response = await request('/api/auth/telegram', 'POST', { init_data: initData });
            
            // Сохраняем токен и данные пользователя
            setAuthToken(response.access_token);
            setUserData(response.user);
            
            console.log('Telegram authentication successful:', response.user);
            return response;
        } else {
            // Debug режим для браузера и разработки
            console.log('Using debug authentication...');
            
            const response = await request('/api/auth/telegram/debug', 'POST');
            
            // Сохраняем токен и данные пользователя
            setAuthToken(response.access_token);
            setUserData(response.user);
            
            console.log('Debug authentication successful:', response.user);
            return response;
        }
        
    } catch (error) {
        console.error('Authentication error:', error);
        throw error;
    }
}

// Функции для каждого эндпоинта
export const api = {
    // Авторизация
    authenticateUser,
    getCurrentUser: () => request('/api/auth/me'),
    
    // Методы для работы с колодами
    getDecks: () => request('/api/decks/'),
    createDeck: (deckData) => request('/api/decks/', 'POST', deckData),
    deleteDeck: (deckId) => request(`/api/decks/${deckId}`, 'DELETE'),
    
    // Методы для работы с карточками
    getDeckCards: (deckId) => request(`/api/cards/deck/${deckId}`, 'GET'),
    saveCard: (cardData) => request('/api/cards/save', 'POST', cardData),
    enrichPhrase: (enrichData) => request('/api/cards/enrich', 'POST', enrichData),
    generateAudio: (audioData) => request('/api/cards/generate-audio', 'POST', audioData),
    updateCardStatus: (statusData) => request('/api/cards/update-status', 'POST', statusData),
    deleteCard: (cardId) => request(`/api/cards/delete/${cardId}`, 'DELETE'),
    
    // Отладочные методы
    authenticateDebug: () => request('/api/auth/telegram/debug', 'POST'),
    
    // Методы для работы со статистикой тренировок
    getDailyTrainingStats: (days = 7) => request(`/api/training-stats/daily?days=${days}`, 'GET'),
    recordTrainingSession: (cardsStudied, sessionDuration = 0) => 
        request('/api/training-stats/record', 'POST', { 
            cards_studied: cardsStudied, 
            session_duration: sessionDuration 
        })
};