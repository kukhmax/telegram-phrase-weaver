/**
 * Компонент для управления колодами карточек
 * Обеспечивает создание, просмотр, редактирование и удаление колод
 */

class DeckManager {
    constructor(apiClient, authService) {
        this.apiClient = apiClient;
        this.authService = authService;
        this.currentUser = null;
        this.decks = [];
        
        // DOM элементы
        this.elements = {
            // Основной контейнер
            container: null,
            
            // Список колод
            decksList: null,
            emptyState: null,
            
            // Форма создания колоды
            createForm: null,
            createButton: null,
            
            // Поля формы
            nameInput: null,
            descriptionInput: null,
            sourceLanguageSelect: null,
            targetLanguageSelect: null,
            
            // Кнопки действий
            submitButton: null,
            cancelButton: null
        };
        
        // Состояние компонента
        this.isFormVisible = false;
        this.isLoading = false;
        
        // Список поддерживаемых языков
        this.languages = [
            { code: 'en', name: 'English' },
            { code: 'ru', name: 'Русский' },
            { code: 'es', name: 'Español' },
            { code: 'fr', name: 'Français' },
            { code: 'de', name: 'Deutsch' },
            { code: 'it', name: 'Italiano' },
            { code: 'pt', name: 'Português' },
            { code: 'zh', name: '中文' },
            { code: 'ja', name: '日本語' },
            { code: 'ko', name: '한국어' }
        ];
    }
    
    /**
     * Инициализация компонента
     */
    async init() {
        console.log('[DeckManager] Initializing deck manager...');
        
        try {
            // Получаем текущего пользователя
            this.currentUser = await this.authService.getCurrentUser();
            
            if (!this.currentUser) {
                throw new Error('Пользователь не аутентифицирован');
            }
            
            // Создаем DOM структуру
            this.createDOM();
            
            // Привязываем обработчики событий
            this.bindEvents();
            
            // Загружаем колоды пользователя
            await this.loadDecks();
            
            console.log('[DeckManager] Deck manager initialized successfully');
            
        } catch (error) {
            console.error('[DeckManager] Failed to initialize:', error);
            this.showError('Ошибка инициализации менеджера колод: ' + error.message);
        }
    }
    
    /**
     * Создание DOM структуры компонента
     */
    createDOM() {
        // Находим контейнер для компонента
        this.elements.container = document.getElementById('deck-manager');
        
        if (!this.elements.container) {
            // Создаем контейнер если его нет
            this.elements.container = document.createElement('div');
            this.elements.container.id = 'deck-manager';
            this.elements.container.className = 'deck-manager';
            
            // Добавляем в основное приложение
            const app = document.getElementById('app');
            if (app) {
                app.appendChild(this.elements.container);
            }
        }
        
        // Создаем HTML структуру
        this.elements.container.innerHTML = `
            <div class="deck-manager-header">
                <h2>📚 Мои колоды</h2>
                <button id="create-deck-btn" class="btn btn-primary">
                    <span class="btn-icon">➕</span>
                    Создать колоду
                </button>
            </div>
            
            <!-- Форма создания колоды (скрыта по умолчанию) -->
            <div id="create-deck-form" class="create-deck-form" style="display: none;">
                <div class="form-header">
                    <h3>Создание новой колоды</h3>
                </div>
                
                <form id="deck-form">
                    <div class="form-group">
                        <label for="deck-name">Название колоды *</label>
                        <input 
                            type="text" 
                            id="deck-name" 
                            name="name" 
                            placeholder="Например: Базовые фразы для путешествий"
                            required
                            maxlength="255"
                        >
                    </div>
                    
                    <div class="form-group">
                        <label for="deck-description">Описание (опционально)</label>
                        <textarea 
                            id="deck-description" 
                            name="description" 
                            placeholder="Краткое описание содержимого колоды"
                            maxlength="1000"
                            rows="3"
                        ></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="source-language">Изучаемый язык *</label>
                            <select id="source-language" name="sourceLanguage" required>
                                <option value="">Выберите язык</option>
                                ${this.languages.map(lang => 
                                    `<option value="${lang.code}">${lang.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="target-language">Язык перевода *</label>
                            <select id="target-language" name="targetLanguage" required>
                                <option value="">Выберите язык</option>
                                ${this.languages.map(lang => 
                                    `<option value="${lang.code}">${lang.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" id="cancel-btn" class="btn btn-secondary">
                            Отмена
                        </button>
                        <button type="submit" id="submit-btn" class="btn btn-primary">
                            <span class="btn-icon">💾</span>
                            Создать колоду
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Список колод -->
            <div id="decks-list" class="decks-list">
                <!-- Колоды будут загружены динамически -->
            </div>
            
            <!-- Состояние "нет колод" -->
            <div id="empty-state" class="empty-state" style="display: none;">
                <div class="empty-icon">📚</div>
                <h3>У вас пока нет колод</h3>
                <p>Создайте свою первую колоду карточек для изучения языка</p>
                <button class="btn btn-primary" onclick="document.getElementById('create-deck-btn').click()">
                    <span class="btn-icon">➕</span>
                    Создать первую колоду
                </button>
            </div>
            
            <!-- Индикатор загрузки -->
            <div id="loading-indicator" class="loading-indicator" style="display: none;">
                <div class="spinner"></div>
                <p>Загрузка колод...</p>
            </div>
        `;
        
        // Получаем ссылки на элементы
        this.elements.createButton = document.getElementById('create-deck-btn');
        this.elements.createForm = document.getElementById('create-deck-form');
        this.elements.decksList = document.getElementById('decks-list');
        this.elements.emptyState = document.getElementById('empty-state');
        
        // Элементы формы
        this.elements.nameInput = document.getElementById('deck-name');
        this.elements.descriptionInput = document.getElementById('deck-description');
        this.elements.sourceLanguageSelect = document.getElementById('source-language');
        this.elements.targetLanguageSelect = document.getElementById('target-language');
        
        // Кнопки
        this.elements.submitButton = document.getElementById('submit-btn');
        this.elements.cancelButton = document.getElementById('cancel-btn');
    }
    
    /**
     * Привязка обработчиков событий
     */
    bindEvents() {
        // Кнопка создания колоды
        this.elements.createButton.addEventListener('click', () => {
            this.showCreateForm();
        });
        
        // Кнопка отмены
        this.elements.cancelButton.addEventListener('click', () => {
            this.hideCreateForm();
        });
        
        // Отправка формы
        const form = document.getElementById('deck-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateDeck();
        });
        
        // Валидация полей в реальном времени
        this.elements.nameInput.addEventListener('input', () => {
            this.validateForm();
        });
        
        this.elements.sourceLanguageSelect.addEventListener('change', () => {
            this.validateForm();
        });
        
        this.elements.targetLanguageSelect.addEventListener('change', () => {
            this.validateForm();
        });
    }
    
    /**
     * Показать форму создания колоды
     */
    showCreateForm() {
        this.elements.createForm.style.display = 'block';
        this.elements.nameInput.focus();
        this.isFormVisible = true;
        
        // Прокручиваем к форме
        this.elements.createForm.scrollIntoView({ behavior: 'smooth' });
    }
    
    /**
     * Скрыть форму создания колоды
     */
    hideCreateForm() {
        this.elements.createForm.style.display = 'none';
        this.isFormVisible = false;
        
        // Очищаем форму
        document.getElementById('deck-form').reset();
        this.validateForm();
    }
    
    /**
     * Валидация формы
     */
    validateForm() {
        const name = this.elements.nameInput.value.trim();
        const sourceLanguage = this.elements.sourceLanguageSelect.value;
        const targetLanguage = this.elements.targetLanguageSelect.value;
        
        // Проверяем обязательные поля
        const isValid = name.length > 0 && sourceLanguage && targetLanguage && sourceLanguage !== targetLanguage;
        
        // Включаем/отключаем кнопку отправки
        this.elements.submitButton.disabled = !isValid;
        
        // Показываем предупреждение если языки одинаковые
        if (sourceLanguage && targetLanguage && sourceLanguage === targetLanguage) {
            this.showFormError('Изучаемый язык и язык перевода должны быть разными');
        } else {
            this.hideFormError();
        }
        
        return isValid;
    }
    
    /**
     * Показать ошибку в форме
     */
    showFormError(message) {
        let errorElement = document.querySelector('.form-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            this.elements.createForm.appendChild(errorElement);
        }
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    /**
     * Скрыть ошибку в форме
     */
    hideFormError() {
        const errorElement = document.querySelector('.form-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    /**
     * Обработка создания новой колоды
     */
    async handleCreateDeck() {
        if (!this.validateForm()) {
            return;
        }
        
        // Показываем индикатор загрузки
        this.setLoading(true);
        
        try {
            // Собираем данные формы
            const formData = {
                name: this.elements.nameInput.value.trim(),
                description: this.elements.descriptionInput.value.trim() || null,
                source_language: this.elements.sourceLanguageSelect.value,
                target_language: this.elements.targetLanguageSelect.value
            };
            
            console.log('[DeckManager] Creating deck:', formData);
            
            // Отправляем запрос на создание колоды
            const response = await this.apiClient.client.post(
                `/decks?user_id=${this.currentUser.id}`,
                formData
            );
            
            console.log('[DeckManager] Deck created successfully:', response);
            
            // Скрываем форму
            this.hideCreateForm();
            
            // Перезагружаем список колод
            await this.loadDecks();
            
            // Показываем уведомление об успехе
            this.showSuccess('Колода успешно создана!');
            
        } catch (error) {
            console.error('[DeckManager] Failed to create deck:', error);
            this.showError('Ошибка при создании колоды: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Загрузка списка колод пользователя
     */
    async loadDecks() {
        console.log('[DeckManager] Loading user decks...');
        
        try {
            // Показываем индикатор загрузки
            document.getElementById('loading-indicator').style.display = 'block';
            this.elements.decksList.style.display = 'none';
            this.elements.emptyState.style.display = 'none';
            
            // Запрашиваем колоды с сервера
            const response = await this.apiClient.client.get(
                `/decks?user_id=${this.currentUser.id}`
            );
            
            this.decks = response.decks || [];
            
            console.log('[DeckManager] Loaded decks:', this.decks);
            
            // Отображаем колоды
            this.renderDecks();
            
        } catch (error) {
            console.error('[DeckManager] Failed to load decks:', error);
            this.showError('Ошибка при загрузке колод: ' + error.message);
        } finally {
            // Скрываем индикатор загрузки
            document.getElementById('loading-indicator').style.display = 'none';
        }
    }
    
    /**
     * Отображение списка колод
     */
    renderDecks() {
        if (this.decks.length === 0) {
            // Показываем состояние "нет колод"
            this.elements.decksList.style.display = 'none';
            this.elements.emptyState.style.display = 'block';
            return;
        }
        
        // Показываем список колод
        this.elements.emptyState.style.display = 'none';
        this.elements.decksList.style.display = 'block';
        
        // Генерируем HTML для каждой колоды
        const decksHTML = this.decks.map(deck => this.renderDeckCard(deck)).join('');
        
        this.elements.decksList.innerHTML = decksHTML;
        
        // Привязываем обработчики для карточек колод
        this.bindDeckCardEvents();
    }
    
    /**
     * Отображение карточки колоды
     */
    renderDeckCard(deck) {
        const sourceLanguageName = this.getLanguageName(deck.source_language);
        const targetLanguageName = this.getLanguageName(deck.target_language);
        const createdDate = new Date(deck.created_at).toLocaleDateString('ru-RU');
        
        return `
            <div class="deck-card" data-deck-id="${deck.id}">
                <div class="deck-card-header">
                    <h3 class="deck-name">${this.escapeHtml(deck.name)}</h3>
                    <div class="deck-actions">
                        <button class="btn-icon edit-deck" title="Редактировать">
                            ✏️
                        </button>
                        <button class="btn-icon delete-deck" title="Удалить">
                            🗑️
                        </button>
                    </div>
                </div>
                
                ${deck.description ? `
                    <p class="deck-description">${this.escapeHtml(deck.description)}</p>
                ` : ''}
                
                <div class="deck-info">
                    <div class="deck-languages">
                        <span class="language-badge source">${sourceLanguageName}</span>
                        <span class="arrow">→</span>
                        <span class="language-badge target">${targetLanguageName}</span>
                    </div>
                    
                    <div class="deck-stats">
                        <div class="stat">
                            <span class="stat-value">${deck.card_count}</span>
                            <span class="stat-label">карточек</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${deck.cards_to_review}</span>
                            <span class="stat-label">к повторению</span>
                        </div>
                    </div>
                </div>
                
                <div class="deck-footer">
                    <span class="deck-date">Создана: ${createdDate}</span>
                    <div class="deck-actions">
                        <button class="btn btn-primary open-deck">
                            <span class="btn-icon">📖</span>
                            Открыть
                        </button>
                        <button class="btn btn-success add-cards" data-deck-id="${deck.id}">
                            <span class="btn-icon">➕</span>
                            Добавить карточки
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Привязка обработчиков для карточек колод
     */
    bindDeckCardEvents() {
        // Кнопки открытия колоды
        document.querySelectorAll('.open-deck').forEach(button => {
            button.addEventListener('click', (e) => {
                const deckCard = e.target.closest('.deck-card');
                const deckId = parseInt(deckCard.dataset.deckId);
                this.openDeck(deckId);
            });
        });
        
        // Кнопки добавления карточек
        document.querySelectorAll('.add-cards').forEach(button => {
            button.addEventListener('click', (e) => {
                const deckId = parseInt(e.target.dataset.deckId);
                this.addCardsToDeck(deckId);
            });
        });
        
        // Кнопки редактирования
        document.querySelectorAll('.edit-deck').forEach(button => {
            button.addEventListener('click', (e) => {
                const deckCard = e.target.closest('.deck-card');
                const deckId = parseInt(deckCard.dataset.deckId);
                this.editDeck(deckId);
            });
        });
        
        // Кнопки удаления
        document.querySelectorAll('.delete-deck').forEach(button => {
            button.addEventListener('click', (e) => {
                const deckCard = e.target.closest('.deck-card');
                const deckId = parseInt(deckCard.dataset.deckId);
                this.deleteDeck(deckId);
            });
        });
    }
    
    /**
     * Открытие колоды для просмотра карточек
     */
    async openDeck(deckId) {
        console.log('[DeckManager] Opening deck:', deckId);
        
        try {
            // Находим данные колоды
            const deck = this.decks.find(d => d.id === parseInt(deckId));
            if (!deck) {
                this.showError('Колода не найдена');
                return;
            }
            
            // Вызываем метод главного приложения для показа карточек
            if (window.app && typeof window.app.showCardsView === 'function') {
                await window.app.showCardsView(deck);
            } else {
                console.error('[DeckManager] App instance or showCardsView method not found');
                this.showError('Ошибка навигации к карточкам');
            }
        } catch (error) {
            console.error('[DeckManager] Error opening deck:', error);
            this.showError('Ошибка при открытии колоды: ' + error.message);
        }
    }
    
    /**
     * Добавление карточек в колоду
     */
    async addCardsToDeck(deckId) {
        console.log('[DeckManager] Adding cards to deck:', deckId);
        
        try {
            // Находим данные колоды
            const deck = this.decks.find(d => d.id === parseInt(deckId));
            if (!deck) {
                this.showError('Колода не найдена');
                return;
            }
            
            // Открываем модальное окно обогащения карточек
            if (window.cardEnricher && typeof window.cardEnricher.open === 'function') {
                window.cardEnricher.open(deck.id);
            } else {
                console.error('[DeckManager] CardEnricher instance not found');
                this.showError('Ошибка открытия окна обогащения карточек');
            }
        } catch (error) {
            console.error('[DeckManager] Error adding cards to deck:', error);
            this.showError('Ошибка при добавлении карточек: ' + error.message);
        }
    }
    
    /**
     * Редактирование колоды
     */
    editDeck(deckId) {
        console.log('[DeckManager] Editing deck:', deckId);
        // TODO: Реализовать редактирование колоды
        this.showInfo(`Редактирование колоды ${deckId} будет реализовано в следующих версиях`);
    }
    
    /**
     * Удаление колоды
     */
    async deleteDeck(deckId) {
        const deck = this.decks.find(d => d.id === deckId);
        if (!deck) return;
        
        // Подтверждение удаления
        const confirmed = confirm(
            `Вы уверены, что хотите удалить колоду "${deck.name}"?\n\n` +
            `Это действие нельзя отменить. Все карточки в колоде также будут удалены.`
        );
        
        if (!confirmed) return;
        
        try {
            console.log('[DeckManager] Deleting deck:', deckId);
            
            // Отправляем запрос на удаление
            await this.apiClient.client.delete(
                `/decks/${deckId}?user_id=${this.currentUser.id}`
            );
            
            console.log('[DeckManager] Deck deleted successfully');
            
            // Перезагружаем список колод
            await this.loadDecks();
            
            this.showSuccess('Колода успешно удалена');
            
        } catch (error) {
            console.error('[DeckManager] Failed to delete deck:', error);
            this.showError('Ошибка при удалении колоды: ' + error.message);
        }
    }
    
    /**
     * Получение названия языка по коду
     */
    getLanguageName(code) {
        const language = this.languages.find(lang => lang.code === code);
        return language ? language.name : code.toUpperCase();
    }
    
    /**
     * Экранирование HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Установка состояния загрузки
     */
    setLoading(loading) {
        this.isLoading = loading;
        
        if (this.elements.submitButton) {
            this.elements.submitButton.disabled = loading;
            this.elements.submitButton.textContent = loading ? 'Создание...' : 'Создать колоду';
        }
    }
    
    /**
     * Показать сообщение об успехе
     */
    showSuccess(message) {
        // TODO: Реализовать систему уведомлений
        console.log('[DeckManager] Success:', message);
        alert('✅ ' + message);
    }
    
    /**
     * Показать сообщение об ошибке
     */
    showError(message) {
        // TODO: Реализовать систему уведомлений
        console.error('[DeckManager] Error:', message);
        alert('❌ ' + message);
    }
    
    /**
     * Показать информационное сообщение
     */
    showInfo(message) {
        // TODO: Реализовать систему уведомлений
        console.info('[DeckManager] Info:', message);
        alert('ℹ️ ' + message);
    }
}

// Экспорт для использования в других модулях
window.DeckManager = DeckManager;

console.log('[DeckManager] Deck manager component loaded');