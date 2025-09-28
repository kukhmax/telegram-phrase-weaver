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
        // Проверяем, запущено ли в Telegram (по User Agent)
        const isTelegramClient = navigator.userAgent.includes('Telegram');
        const telegramWebApp = window.Telegram?.WebApp;
        const initData = telegramWebApp?.initData || '';
        
        console.log('Authentication context:', {
            hostname: window.location.hostname,
            isTelegramClient: isTelegramClient,
            telegramWebApp: !!telegramWebApp,
            initDataLength: initData.length,
            initDataPreview: initData ? initData.substring(0, 50) + '...' : 'null',
            userAgent: navigator.userAgent
        });
        
        if (isTelegramClient) {
            // Telegram клиент обнаружен - пробуем аутентификацию
            console.log('Telegram client detected, attempting authentication...');
            console.log('InitData length:', initData.length);
            
            // Пробуем настоящую Telegram аутентификацию если есть initData
            if (initData && initData.length > 50) {
                console.log('Attempting real Telegram authentication with initData...');
                try {
                    const response = await request('/api/auth/telegram', 'POST', { init_data: initData });
                    setAuthToken(response.access_token);
                    setUserData(response.user);
                    console.log('Real Telegram authentication successful:', response.user);
                    return response;
                } catch (authError) {
                    console.error('Real Telegram auth failed:', authError);
                    console.log('Falling back to debug authentication...');
                }
            }
            
            // Fallback к debug режиму
            console.log('Using debug authentication for Telegram client...');
            const response = await request('/api/auth/telegram/debug', 'POST');
            setAuthToken(response.access_token);
            setUserData(response.user);
            console.log('Telegram debug authentication successful:', response.user);
            return response;
        } else {
            // Debug режим для браузера и разработки
            console.log('Using debug authentication for browser...');
            console.log('Reason: Not a Telegram client');
            
            const response = await request('/api/auth/telegram/debug', 'POST');
            
            // Сохраняем токен и данные пользователя
            setAuthToken(response.access_token);
            setUserData(response.user);
            
            console.log('Debug authentication successful:', response.user);
            return response;
        }
        
    } catch (error) {
        console.error('Authentication error:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        throw new Error(`Ошибка инициализации: ${error.message}`);
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
    getDeckCards: (deckId, page = 1, limit = 10) => request(`/api/cards/deck/${deckId}?page=${page}&limit=${limit}`, 'GET'),
    saveCard: (cardData) => request('/api/cards/save', 'POST', cardData),
    enrichPhrase: (enrichData) => request('/api/cards/enrich', 'POST', enrichData),
    addPhrase: (phraseData) => request('/api/cards/add-phrase', 'POST', phraseData),
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