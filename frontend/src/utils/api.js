/**
 * API клиент для взаимодействия с backend сервером PhraseWeaver
 * Обеспечивает централизованное управление HTTP запросами
 */

/**
 * Определяет базовый URL API в зависимости от окружения.
 * @returns {string} Базовый URL API.
 */
const getApiBaseUrl = () => {
    // Для локальной разработки, когда frontend запущен на localhost или 127.0.0.1
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Используем порт 8000, как указано в скрипте restart_servers.sh
        return 'http://localhost:8000/api';
    }
    // Для production или тестирования через ngrok.
    // В идеале, этот URL должен внедряться в процессе сборки (build).
    return 'https://316fbdc32e47.ngrok-free.app/api'; // ЗАМЕНИТЬ НА ВАШ PROD/NGROK URL
};

// Конфигурация API
const API_CONFIG = {
    BASE_URL: getApiBaseUrl(),
    
    // Таймауты для запросов
    TIMEOUT: 10000, // 10 секунд
    
    // Заголовки по умолчанию
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

/**
 * Основной класс для работы с API
 */
class ApiClient {
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.defaultHeaders = { ...API_CONFIG.DEFAULT_HEADERS };
    }

    /**
     * Выполняет HTTP запрос с обработкой ошибок
     * @param {string} endpoint - Конечная точка API
     * @param {Object} options - Опции запроса (method, body, headers)
     * @returns {Promise<Object>} Ответ от сервера
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Настройка опций запроса
        const requestOptions = {
            method: options.method || 'GET',
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            },
            // Добавляем тело запроса только для методов, которые его поддерживают
            ...(options.body && { body: JSON.stringify(options.body) })
        };

        try {
            console.log(`[API] ${requestOptions.method} ${url}`, options.body || '');
            
            // Создаем контроллер для отмены запроса по таймауту
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            requestOptions.signal = controller.signal;
            
            // Выполняем запрос
            const response = await fetch(url, requestOptions);
            
            // Очищаем таймаут
            clearTimeout(timeoutId);
            
            // Проверяем статус ответа
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Парсим JSON ответ
            const data = await response.json();
            console.log(`[API] Response:`, data);
            
            return data;
            
        } catch (error) {
            console.error(`[API] Error in ${requestOptions.method} ${url}:`, error);
            
            // Обработка различных типов ошибок
            if (error.name === 'AbortError') {
                throw new Error('Превышено время ожидания запроса');
            }
            
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Ошибка подключения к серверу');
            }
            
            throw error;
        }
    }

    /**
     * GET запрос
     * @param {string} endpoint - Конечная точка API
     * @param {Object} headers - Дополнительные заголовки
     * @returns {Promise<Object>} Ответ от сервера
     */
    async get(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'GET', headers });
    }

    /**
     * POST запрос
     * @param {string} endpoint - Конечная точка API
     * @param {Object} body - Тело запроса
     * @param {Object} headers - Дополнительные заголовки
     * @returns {Promise<Object>} Ответ от сервера
     */
    async post(endpoint, body = {}, headers = {}) {
        return this.request(endpoint, { method: 'POST', body, headers });
    }

    /**
     * PUT запрос
     * @param {string} endpoint - Конечная точка API
     * @param {Object} body - Тело запроса
     * @param {Object} headers - Дополнительные заголовки
     * @returns {Promise<Object>} Ответ от сервера
     */
    async put(endpoint, body = {}, headers = {}) {
        return this.request(endpoint, { method: 'PUT', body, headers });
    }

    /**
     * DELETE запрос
     * @param {string} endpoint - Конечная точка API
     * @param {Object} headers - Дополнительные заголовки
     * @returns {Promise<Object>} Ответ от сервера
     */
    async delete(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'DELETE', headers });
    }

    /**
     * Проверка доступности сервера
     * @returns {Promise<boolean>} true если сервер доступен
     */
    async checkHealth() {
        try {
            await this.get('/health');
            return true;
        } catch (error) {
            console.warn('[API] Health check failed:', error.message);
            return false;
        }
    }

    /**
     * Устанавливает токен авторизации для всех последующих запросов
     * @param {string} token - JWT токен
     */
    setAuthToken(token) {
        if (token) {
            this.defaultHeaders['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.defaultHeaders['Authorization'];
        }
    }

    /**
     * Очищает токен авторизации
     */
    clearAuthToken() {
        delete this.defaultHeaders['Authorization'];
    }
}

/**
 * Специализированные методы для работы с аутентификацией
 */
class AuthApi {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Аутентификация через Telegram WebApp
     * @param {Object} telegramData - Данные от Telegram WebApp
     * @returns {Promise<Object>} Информация о пользователе
     */
    async authenticateWithTelegram(telegramData) {
        return this.api.post('/auth/telegram', telegramData);
    }

    /**
     * Получение информации о текущем пользователе
     * @param {number} telegramId - ID пользователя в Telegram
     * @returns {Promise<Object>} Информация о пользователе
     */
    async getCurrentUser(telegramId) {
        return this.api.get(`/auth/me?telegram_id=${telegramId}`);
    }
}

/**
 * Специализированные методы для работы с колодами (будут добавлены позже)
 */
class DecksApi {
    constructor(apiClient) {
        this.api = apiClient;
    }

    // Методы для работы с колодами будут добавлены в следующих этапах
    // async getDecks() { ... }
    // async createDeck(deckData) { ... }
    // async deleteDeck(deckId) { ... }
}

// Создаем глобальный экземпляр API клиента
const apiClient = new ApiClient();

// Создаем специализированные API для разных модулей
const authApi = new AuthApi(apiClient);
const decksApi = new DecksApi(apiClient);

// Экспортируем API для использования в других модулях
window.PhraseWeaverAPI = {
    client: apiClient,
    auth: authApi,
    decks: decksApi
};

// Логируем инициализацию API
console.log('[API] PhraseWeaver API client initialized');
console.log('[API] Base URL:', API_CONFIG.BASE_URL);