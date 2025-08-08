/**
 * Модуль аутентификации для Telegram Mini App
 * Обрабатывает инициализацию Telegram WebApp и аутентификацию пользователя
 */

/**
 * Класс для управления аутентификацией
 */
class AuthService {
    constructor() {
        this.isInitialized = false;
        this.user = null;
        this.telegramWebApp = null;
        
        // Колбэки для событий аутентификации
        this.onAuthSuccess = null;
        this.onAuthError = null;
        this.onStatusChange = null;
    }

    /**
     * Инициализация Telegram WebApp
     * @returns {Promise<boolean>} true если инициализация успешна
     */
    async initialize() {
        try {
            console.log('[Auth] Initializing Telegram WebApp...');
            
            // Проверяем доступность Telegram WebApp API
            if (typeof window.Telegram === 'undefined' || !window.Telegram.WebApp) {
                throw new Error('Telegram WebApp API недоступен');
            }
            
            this.telegramWebApp = window.Telegram.WebApp;
            
            // Инициализируем WebApp
            this.telegramWebApp.ready();
            
            // Настраиваем внешний вид
            this.telegramWebApp.expand();
            this.telegramWebApp.enableClosingConfirmation();
            
            // Получаем данные пользователя
            const initData = this.telegramWebApp.initData;
            const initDataUnsafe = this.telegramWebApp.initDataUnsafe;
            
            console.log('[Auth] Telegram WebApp initialized');
            console.log('[Auth] Init data:', initData);
            console.log('[Auth] Init data unsafe:', initDataUnsafe);
            
            // Проверяем наличие пользователя
            if (!initDataUnsafe.user) {
                throw new Error('Данные пользователя недоступны');
            }
            
            this.isInitialized = true;
            this.updateStatus('Telegram WebApp инициализирован');
            
            return true;
            
        } catch (error) {
            console.error('[Auth] Initialization failed:', error);
            this.updateStatus(`Ошибка инициализации: ${error.message}`, 'error');
            return false;
        }
    }

    /**
     * Аутентификация пользователя через backend
     * @returns {Promise<Object|null>} Данные пользователя или null при ошибке
     */
    async authenticate() {
        if (!this.isInitialized) {
            console.error('[Auth] WebApp not initialized');
            return null;
        }

        try {
            this.updateStatus('Аутентификация пользователя...');
            
            // Получаем данные пользователя из Telegram
            const telegramUser = this.telegramWebApp.initDataUnsafe.user;
            
            // Подготавливаем данные для отправки на backend
            const authData = {
                telegram_id: telegramUser.id,
                username: telegramUser.username || '',
                first_name: telegramUser.first_name || '',
                last_name: telegramUser.last_name || '',
                language_code: telegramUser.language_code || 'en'
            };
            
            console.log('[Auth] Authenticating user:', authData);
            
            // Отправляем данные на backend
            const response = await window.PhraseWeaverAPI.auth.authenticateWithTelegram(authData);
            
            // Сохраняем данные пользователя
            this.user = response;
            
            console.log('[Auth] Authentication successful:', this.user);
            this.updateStatus('Аутентификация успешна', 'success');
            
            // Вызываем колбэк успешной аутентификации
            if (this.onAuthSuccess) {
                this.onAuthSuccess(this.user);
            }
            
            return this.user;
            
        } catch (error) {
            console.error('[Auth] Authentication failed:', error);
            this.updateStatus(`Ошибка аутентификации: ${error.message}`, 'error');
            
            // Вызываем колбэк ошибки аутентификации
            if (this.onAuthError) {
                this.onAuthError(error);
            }
            
            return null;
        }
    }

    /**
     * Получение текущего пользователя
     * @returns {Object|null} Данные пользователя
     */
    getCurrentUser() {
        return this.user;
    }

    /**
     * Проверка аутентификации
     * @returns {boolean} true если пользователь аутентифицирован
     */
    isAuthenticated() {
        return this.user !== null;
    }

    /**
     * Получение Telegram данных пользователя
     * @returns {Object|null} Telegram данные пользователя
     */
    getTelegramUser() {
        if (!this.isInitialized || !this.telegramWebApp) {
            return null;
        }
        return this.telegramWebApp.initDataUnsafe.user || null;
    }

    /**
     * Получение информации о Telegram WebApp
     * @returns {Object} Информация о WebApp
     */
    getWebAppInfo() {
        if (!this.isInitialized || !this.telegramWebApp) {
            return null;
        }
        
        return {
            version: this.telegramWebApp.version,
            platform: this.telegramWebApp.platform,
            colorScheme: this.telegramWebApp.colorScheme,
            themeParams: this.telegramWebApp.themeParams,
            isExpanded: this.telegramWebApp.isExpanded,
            viewportHeight: this.telegramWebApp.viewportHeight,
            viewportStableHeight: this.telegramWebApp.viewportStableHeight
        };
    }

    /**
     * Обновление статуса аутентификации
     * @param {string} message - Сообщение о статусе
     * @param {string} type - Тип статуса (info, success, error)
     */
    updateStatus(message, type = 'info') {
        console.log(`[Auth] Status (${type}):`, message);
        
        if (this.onStatusChange) {
            this.onStatusChange(message, type);
        }
    }

    /**
     * Установка колбэков для событий аутентификации
     * @param {Object} callbacks - Объект с колбэками
     */
    setCallbacks(callbacks) {
        this.onAuthSuccess = callbacks.onAuthSuccess || null;
        this.onAuthError = callbacks.onAuthError || null;
        this.onStatusChange = callbacks.onStatusChange || null;
    }

    /**
     * Выход из системы
     */
    logout() {
        this.user = null;
        console.log('[Auth] User logged out');
        this.updateStatus('Пользователь вышел из системы');
    }

    /**
     * Показать главную кнопку Telegram
     * @param {string} text - Текст кнопки
     * @param {Function} onClick - Обработчик нажатия
     */
    showMainButton(text, onClick) {
        if (!this.telegramWebApp) return;
        
        this.telegramWebApp.MainButton.text = text;
        this.telegramWebApp.MainButton.show();
        this.telegramWebApp.MainButton.onClick(onClick);
    }

    /**
     * Скрыть главную кнопку Telegram
     */
    hideMainButton() {
        if (!this.telegramWebApp) return;
        
        this.telegramWebApp.MainButton.hide();
    }

    /**
     * Показать всплывающее уведомление
     * @param {string} message - Текст уведомления
     */
    showAlert(message) {
        if (!this.telegramWebApp) {
            alert(message);
            return;
        }
        
        this.telegramWebApp.showAlert(message);
    }

    /**
     * Показать подтверждение
     * @param {string} message - Текст подтверждения
     * @param {Function} callback - Колбэк с результатом (true/false)
     */
    showConfirm(message, callback) {
        if (!this.telegramWebApp) {
            callback(confirm(message));
            return;
        }
        
        this.telegramWebApp.showConfirm(message, callback);
    }

    /**
     * Закрыть Mini App
     */
    close() {
        if (!this.telegramWebApp) return;
        
        this.telegramWebApp.close();
    }
}

// Создаем глобальный экземпляр сервиса аутентификации
const authService = new AuthService();

// Экспортируем сервис для использования в других модулях
window.PhraseWeaverAuth = authService;

// Логируем инициализацию
console.log('[Auth] Authentication service initialized');