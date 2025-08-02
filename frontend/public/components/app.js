/**
 * Основной модуль приложения PhraseWeaver
 * Координирует работу всех компонентов и управляет состоянием приложения
 */

/**
 * Главный класс приложения
 */
class PhraseWeaverApp {
    constructor() {
        this.isInitialized = false;
        this.authService = null;
        this.apiClient = null;
        
        // DOM элементы
        this.elements = {
            // Статус подключения
            connectionStatus: null,
            statusIndicator: null,
            statusText: null,
            
            // Секции приложения
            welcomeSection: null,
            navigation: null,
            userInfo: null,
            
            // Информация о пользователе в заголовке
            userGreeting: null,
            userAvatar: null,
            
            // Детали пользователя
            telegramId: null,
            username: null,
            languageCode: null,
            
            // Навигационные кнопки
            createDeckBtn: null,
            myDecksBtn: null,
            practiceBtn: null
        };
    }

    /**
     * Инициализация приложения
     */
    async init() {
        try {
            console.log('[App] Initializing PhraseWeaver application...');
            
            // Инициализируем DOM элементы
            this.initializeElements();
            
            // Получаем ссылки на сервисы
            this.authService = window.PhraseWeaverAuth;
            this.apiClient = window.PhraseWeaverAPI;
            
            if (!this.authService || !this.apiClient) {
                throw new Error('Сервисы аутентификации или API не инициализированы');
            }
            
            // Настраиваем колбэки для аутентификации
            this.setupAuthCallbacks();
            
            // Настраиваем обработчики событий
            this.setupEventListeners();
            
            // Проверяем подключение к серверу
            await this.checkServerConnection();
            
            // Инициализируем Telegram WebApp
            const telegramInitialized = await this.authService.initialize();
            
            if (telegramInitialized) {
                // Аутентифицируем пользователя
                await this.authService.authenticate();
            }
            
            this.isInitialized = true;
            console.log('[App] Application initialized successfully');
            
        } catch (error) {
            console.error('[App] Initialization failed:', error);
            this.showError(`Ошибка инициализации: ${error.message}`);
        }
    }

    /**
     * Инициализация DOM элементов
     */
    initializeElements() {
        // Статус подключения
        this.elements.connectionStatus = document.getElementById('connectionStatus');
        this.elements.statusIndicator = this.elements.connectionStatus?.querySelector('.status-indicator');
        this.elements.statusText = this.elements.connectionStatus?.querySelector('span:last-child');
        
        // Секции приложения
        this.elements.welcomeSection = document.getElementById('welcomeSection');
        this.elements.navigation = document.getElementById('navigation');
        this.elements.userInfo = document.getElementById('userDetails');
        
        // Информация о пользователе в заголовке
        this.elements.userGreeting = document.getElementById('userGreeting');
        this.elements.userAvatar = document.getElementById('userAvatar');
        
        // Детали пользователя
        this.elements.telegramId = document.getElementById('telegramId');
        this.elements.username = document.getElementById('username');
        this.elements.languageCode = document.getElementById('languageCode');
        
        // Навигационные кнопки
        this.elements.createDeckBtn = document.getElementById('createDeckBtn');
        this.elements.myDecksBtn = document.getElementById('myDecksBtn');
        this.elements.practiceBtn = document.getElementById('practiceBtn');
        
        console.log('[App] DOM elements initialized');
    }

    /**
     * Настройка колбэков для аутентификации
     */
    setupAuthCallbacks() {
        this.authService.setCallbacks({
            onAuthSuccess: (user) => this.handleAuthSuccess(user),
            onAuthError: (error) => this.handleAuthError(error),
            onStatusChange: (message, type) => this.updateConnectionStatus(message, type)
        });
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Навигационные кнопки
        if (this.elements.createDeckBtn) {
            this.elements.createDeckBtn.addEventListener('click', () => this.handleCreateDeck());
        }
        
        if (this.elements.myDecksBtn) {
            this.elements.myDecksBtn.addEventListener('click', () => this.handleMyDecks());
        }
        
        if (this.elements.practiceBtn) {
            this.elements.practiceBtn.addEventListener('click', () => this.handlePractice());
        }
        
        console.log('[App] Event listeners set up');
    }

    /**
     * Проверка подключения к серверу
     */
    async checkServerConnection() {
        try {
            this.updateConnectionStatus('Проверка подключения к серверу...');
            
            const isHealthy = await this.apiClient.client.checkHealth();
            
            if (isHealthy) {
                this.updateConnectionStatus('Подключение к серверу установлено', 'success');
            } else {
                throw new Error('Сервер недоступен');
            }
            
        } catch (error) {
            console.error('[App] Server connection failed:', error);
            this.updateConnectionStatus('Ошибка подключения к серверу', 'error');
        }
    }

    /**
     * Обработка успешной аутентификации
     * @param {Object} user - Данные пользователя
     */
    handleAuthSuccess(user) {
        console.log('[App] Authentication successful:', user);
        
        // Обновляем информацию о пользователе в интерфейсе
        this.updateUserInterface(user);
        
        // Показываем навигацию
        this.showNavigation();
        
        // Скрываем секцию приветствия
        this.hideWelcomeSection();
        
        // Показываем информацию о пользователе
        this.showUserInfo(user);
    }

    /**
     * Обработка ошибки аутентификации
     * @param {Error} error - Ошибка аутентификации
     */
    handleAuthError(error) {
        console.error('[App] Authentication error:', error);
        this.showError(`Ошибка аутентификации: ${error.message}`);
    }

    /**
     * Обновление интерфейса пользователя
     * @param {Object} user - Данные пользователя
     */
    updateUserInterface(user) {
        // Обновляем приветствие в заголовке
        if (this.elements.userGreeting) {
            const name = user.first_name || user.username || 'Пользователь';
            this.elements.userGreeting.textContent = `Привет, ${name}!`;
        }
        
        // Обновляем аватар
        if (this.elements.userAvatar) {
            const initial = (user.first_name || user.username || 'U')[0].toUpperCase();
            this.elements.userAvatar.textContent = initial;
        }
    }

    /**
     * Показ навигации
     */
    showNavigation() {
        if (this.elements.navigation) {
            this.elements.navigation.style.display = 'flex';
            this.elements.navigation.classList.add('fade-in');
        }
    }

    /**
     * Скрытие секции приветствия
     */
    hideWelcomeSection() {
        if (this.elements.welcomeSection) {
            // Плавно скрываем секцию приветствия
            setTimeout(() => {
                this.elements.welcomeSection.style.display = 'none';
            }, 1000);
        }
    }

    /**
     * Показ информации о пользователе
     * @param {Object} user - Данные пользователя
     */
    showUserInfo(user) {
        // Заполняем детали пользователя
        if (this.elements.telegramId) {
            this.elements.telegramId.textContent = user.telegram_id || '-';
        }
        
        if (this.elements.username) {
            const displayName = user.first_name 
                ? `${user.first_name} ${user.last_name || ''}`.trim()
                : user.username || '-';
            this.elements.username.textContent = displayName;
        }
        
        if (this.elements.languageCode) {
            this.elements.languageCode.textContent = user.language_code || '-';
        }
        
        // Показываем секцию с информацией о пользователе
        if (this.elements.userInfo) {
            this.elements.userInfo.style.display = 'block';
            this.elements.userInfo.classList.add('fade-in');
        }
    }

    /**
     * Обновление статуса подключения
     * @param {string} message - Сообщение о статусе
     * @param {string} type - Тип статуса (info, success, error)
     */
    updateConnectionStatus(message, type = 'info') {
        if (!this.elements.connectionStatus) return;
        
        // Обновляем текст статуса
        if (this.elements.statusText) {
            this.elements.statusText.textContent = message;
        }
        
        // Обновляем индикатор и стили
        if (this.elements.statusIndicator && this.elements.connectionStatus) {
            // Удаляем предыдущие классы статуса
            this.elements.connectionStatus.classList.remove('connected', 'error');
            
            switch (type) {
                case 'success':
                    this.elements.statusIndicator.textContent = '✅';
                    this.elements.connectionStatus.classList.add('connected');
                    break;
                case 'error':
                    this.elements.statusIndicator.textContent = '❌';
                    this.elements.connectionStatus.classList.add('error');
                    break;
                default:
                    this.elements.statusIndicator.textContent = '🔄';
                    break;
            }
        }
    }

    /**
     * Показ ошибки пользователю
     * @param {string} message - Сообщение об ошибке
     */
    showError(message) {
        console.error('[App] Error:', message);
        
        // Используем Telegram API для показа ошибки, если доступен
        if (this.authService && this.authService.telegramWebApp) {
            this.authService.showAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Обработчики навигационных кнопок
     */
    handleCreateDeck() {
        console.log('[App] Create deck clicked');
        this.authService?.showAlert('Функция создания колоды будет добавлена в следующих этапах');
    }

    handleMyDecks() {
        console.log('[App] My decks clicked');
        this.authService?.showAlert('Функция просмотра колод будет добавлена в следующих этапах');
    }

    handlePractice() {
        console.log('[App] Practice clicked');
        this.authService?.showAlert('Функция тренировки будет добавлена в следующих этапах');
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[App] DOM loaded, initializing application...');
    
    // Создаем экземпляр приложения
    const app = new PhraseWeaverApp();
    
    // Делаем приложение доступным глобально для отладки
    window.PhraseWeaverApp = app;
    
    // Инициализируем приложение
    await app.init();
});

// Логируем загрузку модуля
console.log('[App] Application module loaded');