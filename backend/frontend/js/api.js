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
        // Проверяем режим отладки
        const isDebugMode = (window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' || 
                           window.location.protocol === 'file:') &&
                           !window.location.hostname.includes('pw-new.club');

        if (isDebugMode) {
            // Режим отладки - используем debug endpoint
            console.log('Running in debug mode, using debug authentication...');
            const response = await request('/auth/telegram/debug', 'POST');
            
            // Сохраняем токен и данные пользователя
            setAuthToken(response.access_token);
            setUserData(response.user);
            
            console.log('Debug authentication successful:', response.user);
            return response;
        }

        // Проверяем, запущено ли в Telegram
        if (!window.Telegram?.WebApp) {
            throw new Error('Приложение должно запускаться в Telegram');
        }

        // Получаем initData от Telegram
        const initData = window.Telegram.WebApp.initData;
        if (!initData) {
            throw new Error('Нет данных авторизации от Telegram');
        }

        console.log('Authenticating with Telegram...');
        
        // Отправляем запрос на авторизацию
        const response = await fetch(`${API_BASE_URL}/auth/telegram`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ init_data: initData })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка авторизации');
        }

        const authData = await response.json();
        
        // Сохраняем токен и данные пользователя
        setAuthToken(authData.access_token);
        setUserData(authData.user);
        
        console.log('Authentication successful:', authData.user);
        return authData;
        
    } catch (error) {
        console.error('Authentication error:', error);
        throw error;
    }
}

// Функции для каждого эндпоинта
export const api = {
    // Авторизация
    authenticateUser,
    getCurrentUser: () => request('/auth/me'),
    
    // Методы для работы с колодами
    getDecks: () => request('/decks/'),
    createDeck: (deckData) => request('/decks/', 'POST', deckData),
    deleteDeck: (deckId) => request(`/decks/${deckId}`, 'DELETE'),
    
    // Методы для работы с карточками
    getDeckCards: (deckId) => request(`/cards/deck/${deckId}`, 'GET'),
    saveCard: (cardData) => request('/cards/save', 'POST', cardData),
    enrichPhrase: (enrichData) => request('/cards/enrich', 'POST', enrichData),
    generateAudio: (audioData) => request('/cards/generate-audio', 'POST', audioData),
    updateCardStatus: (statusData) => request('/cards/update-status', 'POST', statusData),
    deleteCard: (cardId) => request(`/cards/delete/${cardId}`, 'DELETE'),
    
    // Отладочные методы
    authenticateDebug: () => request('/auth/telegram/debug', 'POST')
};