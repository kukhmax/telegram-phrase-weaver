/**
 * Компонент для управления карточками в колоде
 * Обеспечивает создание, просмотр, редактирование и удаление карточек
 * Поддерживает аудио и изображения для карточек
 */

class CardManager {
    constructor(apiClient, authService) {
        this.apiClient = apiClient;
        this.authService = authService;
        this.currentUser = null;
        this.currentDeck = null;
        this.cards = [];
        
        // DOM элементы
        this.elements = {
            // Основной контейнер
            container: null,
            
            // Заголовок с информацией о колоде
            deckHeader: null,
            backButton: null,
            
            // Список карточек
            cardsList: null,
            emptyState: null,
            
            // Форма создания/редактирования карточки
            cardForm: null,
            createButton: null,
            
            // Поля формы
            frontTextInput: null,
            backTextInput: null,
            audioUrlInput: null,
            imageUrlInput: null,
            difficultySelect: null,
            
            // Кнопки действий
            submitButton: null,
            cancelButton: null,
            
            // Предварительный просмотр медиа
            audioPreview: null,
            imagePreview: null
        };
        
        // Состояние компонента
        this.isFormVisible = false;
        this.isLoading = false;
        this.editingCardId = null;
        
        // Уровни сложности
        this.difficultyLevels = [
            { value: 1, name: 'Очень легко', color: '#4CAF50' },
            { value: 2, name: 'Легко', color: '#8BC34A' },
            { value: 3, name: 'Средне', color: '#FFC107' },
            { value: 4, name: 'Сложно', color: '#FF9800' },
            { value: 5, name: 'Очень сложно', color: '#F44336' }
        ];
    }
    
    /**
     * Инициализация компонента управления карточками
     * @param {Object} deck - Объект колоды
     */
    async init(deck) {
        try {
            this.currentDeck = deck;
            this.currentUser = await this.authService.getCurrentUser();
            
            if (!this.currentUser) {
                throw new Error('Пользователь не авторизован');
            }
            
            this.createDOM();
            this.bindEvents();
            await this.loadCards();
            
        } catch (error) {
            console.error('[CardManager] Ошибка инициализации:', error);
            this.showError('Ошибка загрузки карточек: ' + error.message);
        }
    }
    
    /**
     * Создание DOM структуры компонента
     */
    createDOM() {
        const container = document.getElementById('app');
        if (!container) {
            throw new Error('Контейнер приложения не найден');
        }
        
        container.innerHTML = `
            <div class="card-manager">
                <!-- Заголовок с информацией о колоде -->
                <div class="deck-header">
                    <button class="back-button" id="backButton">
                        <i class="icon-arrow-left"></i>
                        Назад к колодам
                    </button>
                    <div class="deck-info">
                        <h1>${this.escapeHtml(this.currentDeck.name)}</h1>
                        <p class="deck-description">${this.escapeHtml(this.currentDeck.description || 'Без описания')}</p>
                        <div class="deck-languages">
                            <span class="language-badge source">${this.currentDeck.source_language.toUpperCase()}</span>
                            <i class="icon-arrow-right"></i>
                            <span class="language-badge target">${this.currentDeck.target_language.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Кнопка создания карточки -->
                <div class="cards-header">
                    <h2>Карточки</h2>
                    <button class="btn btn-primary" id="createCardButton">
                        <i class="icon-plus"></i>
                        Добавить карточку
                    </button>
                </div>
                
                <!-- Форма создания/редактирования карточки -->
                <div class="card-form-container" id="cardFormContainer" style="display: none;">
                    <div class="card-form">
                        <h3 id="formTitle">Новая карточка</h3>
                        
                        <div class="form-group">
                            <label for="frontText">Текст на ${this.currentDeck.source_language.toUpperCase()} *</label>
                            <textarea id="frontText" placeholder="Введите текст на исходном языке" required></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="backText">Перевод на ${this.currentDeck.target_language.toUpperCase()} *</label>
                            <textarea id="backText" placeholder="Введите перевод" required></textarea>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="audioUrl">URL аудио (произношение)</label>
                                <input type="url" id="audioUrl" placeholder="https://example.com/audio.mp3">
                                <div class="audio-preview" id="audioPreview" style="display: none;">
                                    <audio controls></audio>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="imageUrl">URL изображения</label>
                                <input type="url" id="imageUrl" placeholder="https://example.com/image.jpg">
                                <div class="image-preview" id="imagePreview" style="display: none;">
                                    <img alt="Предварительный просмотр">
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="difficulty">Уровень сложности</label>
                            <select id="difficulty">
                                ${this.difficultyLevels.map(level => 
                                    `<option value="${level.value}">${level.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="form-error" id="formError" style="display: none;"></div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" id="cancelButton">Отмена</button>
                            <button type="submit" class="btn btn-primary" id="submitButton">
                                <span class="button-text">Создать карточку</span>
                                <span class="loading-spinner" style="display: none;"></span>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Список карточек -->
                <div class="cards-list" id="cardsList">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        <p>Загрузка карточек...</p>
                    </div>
                </div>
                
                <!-- Пустое состояние -->
                <div class="empty-state" id="emptyState" style="display: none;">
                    <div class="empty-icon">📚</div>
                    <h3>Карточек пока нет</h3>
                    <p>Создайте первую карточку для изучения</p>
                    <button class="btn btn-primary" id="createFirstCardButton">
                        <i class="icon-plus"></i>
                        Создать карточку
                    </button>
                </div>
            </div>
        `;
        
        // Сохраняем ссылки на элементы
        this.elements.container = container.querySelector('.card-manager');
        this.elements.backButton = container.querySelector('#backButton');
        this.elements.cardsList = container.querySelector('#cardsList');
        this.elements.emptyState = container.querySelector('#emptyState');
        this.elements.cardForm = container.querySelector('#cardFormContainer');
        this.elements.createButton = container.querySelector('#createCardButton');
        this.elements.frontTextInput = container.querySelector('#frontText');
        this.elements.backTextInput = container.querySelector('#backText');
        this.elements.audioUrlInput = container.querySelector('#audioUrl');
        this.elements.imageUrlInput = container.querySelector('#imageUrl');
        this.elements.difficultySelect = container.querySelector('#difficulty');
        this.elements.submitButton = container.querySelector('#submitButton');
        this.elements.cancelButton = container.querySelector('#cancelButton');
        this.elements.audioPreview = container.querySelector('#audioPreview');
        this.elements.imagePreview = container.querySelector('#imagePreview');
    }
    
    /**
     * Привязка обработчиков событий
     */
    bindEvents() {
        // Кнопка возврата к колодам
        this.elements.backButton.addEventListener('click', () => {
            window.app.showDeckManager();
        });
    }
    
    /**
     * Показать форму создания карточки
     */
    showCreateForm() {
        this.editingCardId = null;
        this.resetForm();
        document.querySelector('#formTitle').textContent = 'Новая карточка';
        document.querySelector('.button-text').textContent = 'Создать карточку';
        this.elements.cardForm.style.display = 'block';
        this.elements.frontTextInput.focus();
        this.isFormVisible = true;
    }
    
    /**
     * Показать форму редактирования карточки
     */
    showEditForm(card) {
        this.editingCardId = card.id;
        this.resetForm();
        
        // Заполняем форму данными карточки
        this.elements.frontTextInput.value = card.front_text;
        this.elements.backTextInput.value = card.back_text;
        this.elements.audioUrlInput.value = card.audio_url || '';
        this.elements.imageUrlInput.value = card.image_url || '';
        this.elements.difficultySelect.value = card.difficulty;
        
        // Обновляем предварительный просмотр
        this.updateAudioPreview();
        this.updateImagePreview();
        
        document.querySelector('#formTitle').textContent = 'Редактировать карточку';
        document.querySelector('.button-text').textContent = 'Сохранить изменения';
        this.elements.cardForm.style.display = 'block';
        this.elements.frontTextInput.focus();
        this.isFormVisible = true;
    }
    
    /**
     * Скрыть форму создания/редактирования карточки
     */
    hideCreateForm() {
        this.elements.cardForm.style.display = 'none';
        this.resetForm();
        this.isFormVisible = false;
        this.editingCardId = null;
    }
    
    /**
     * Сброс формы к начальному состоянию
     */
    resetForm() {
        this.elements.frontTextInput.value = '';
        this.elements.backTextInput.value = '';
        this.elements.audioUrlInput.value = '';
        this.elements.imageUrlInput.value = '';
        this.elements.difficultySelect.value = '1';
        this.hideFormError();
        this.hideMediaPreviews();
        this.validateForm();
    }
    
    /**
     * Валидация формы
     */
    validateForm() {
        const frontText = this.elements.frontTextInput.value.trim();
        const backText = this.elements.backTextInput.value.trim();
        
        const isValid = frontText.length > 0 && backText.length > 0;
        this.elements.submitButton.disabled = !isValid;
        
        return isValid;
    }
    
    /**
     * Показать ошибку формы
     */
    showFormError(message) {
        const errorElement = document.querySelector('#formError');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }
    
    /**
     * Скрыть ошибку формы
     */
    hideFormError() {
        const errorElement = document.querySelector('#formError');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    /**
     * Обновить предварительный просмотр аудио
     */
    updateAudioPreview() {
        const url = this.elements.audioUrlInput.value.trim();
        const preview = this.elements.audioPreview;
        const audio = preview.querySelector('audio');
        
        if (url && this.isValidUrl(url)) {
            audio.src = url;
            preview.style.display = 'block';
        } else {
            preview.style.display = 'none';
        }
    }
    
    /**
     * Обновить предварительный просмотр изображения
     */
    updateImagePreview() {
        const url = this.elements.imageUrlInput.value.trim();
        const preview = this.elements.imagePreview;
        const img = preview.querySelector('img');
        
        if (url && this.isValidUrl(url)) {
            img.src = url;
            img.onload = () => preview.style.display = 'block';
            img.onerror = () => preview.style.display = 'none';
        } else {
            preview.style.display = 'none';
        }
    }
    
    /**
     * Скрыть все предварительные просмотры медиа
     */
    hideMediaPreviews() {
        this.elements.audioPreview.style.display = 'none';
        this.elements.imagePreview.style.display = 'none';
    }
    
    /**
     * Проверка валидности URL
     */
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    /**
     * Обработка отправки формы создания/редактирования карточки
     */
    async handleSubmitCard() {
        if (!this.validateForm()) {
            this.showFormError('Пожалуйста, заполните все обязательные поля');
            return;
        }
        
        this.setLoading(true);
        this.hideFormError();
        
        try {
            const cardData = {
                front_text: this.elements.frontTextInput.value.trim(),
                back_text: this.elements.backTextInput.value.trim(),
                audio_url: this.elements.audioUrlInput.value.trim() || null,
                image_url: this.elements.imageUrlInput.value.trim() || null,
                difficulty: parseInt(this.elements.difficultySelect.value),
                deck_id: this.currentDeck.id
            };
            
            let response;
            if (this.editingCardId) {
                // Редактирование существующей карточки
                response = await this.apiClient.client.put(
                    `/api/cards/${this.editingCardId}?user_id=${this.currentUser.id}`,
                    cardData
                );
            } else {
                // Создание новой карточки
                response = await this.apiClient.client.post(
                    `/api/cards?user_id=${this.currentUser.id}`,
                    cardData
                );
            }
            
            if (response.ok) {
                const action = this.editingCardId ? 'обновлена' : 'создана';
                this.showSuccess(`Карточка успешно ${action}!`);
                this.hideCreateForm();
                await this.loadCards();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка при сохранении карточки');
            }
            
        } catch (error) {
            console.error('[CardManager] Ошибка при сохранении карточки:', error);
            this.showFormError('Ошибка при сохранении карточки: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Загрузка карточек колоды
     */
    async loadCards() {
        try {
            this.setLoading(true);
            
            const response = await this.apiClient.client.get(
                `/api/cards/deck/${this.currentDeck.id}?user_id=${this.currentUser.id}`
            );
            
            if (response.ok) {
                const data = await response.json();
                this.cards = data.cards || [];
                this.renderCards();
                this.updateCardsCount();
            } else {
                throw new Error('Ошибка загрузки карточек');
            }
            
        } catch (error) {
            console.error('[CardManager] Ошибка загрузки карточек:', error);
            this.showError('Ошибка загрузки карточек: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Обновление счетчика карточек
     */
    updateCardsCount() {
        const totalCardsElement = document.getElementById('totalCards');
        if (totalCardsElement) {
            totalCardsElement.textContent = this.cards.length;
        }
    }
    
    /**
     * Отрисовка списка карточек
     */
    renderCards() {
        if (this.cards.length === 0) {
            this.elements.cardsList.style.display = 'none';
            this.elements.emptyState.style.display = 'block';
        } else {
            this.elements.emptyState.style.display = 'none';
            this.elements.cardsList.style.display = 'block';
            this.elements.cardsList.innerHTML = this.cards.map(card => this.renderCardItem(card)).join('');
            this.bindCardEvents();
        }
    }
    
    /**
     * Отрисовка отдельной карточки
     */
    renderCardItem(card) {
        return `
            <div class="card-item" data-card-id="${card.id}">
                <div class="card-content">
                    <div class="card-phrase">
                        <span class="phrase-text">${this.escapeHtml(card.front_text)}</span>
                        <span class="phrase-separator"> - </span>
                        <span class="translation-text">${this.escapeHtml(card.back_text)}</span>
                    </div>
                    
                    ${card.audio_url ? `
                        <div class="card-audio">
                            <audio controls>
                                <source src="${card.audio_url}" type="audio/mpeg">
                                Ваш браузер не поддерживает аудио.
                            </audio>
                        </div>
                    ` : ''}
                    
                    ${card.image_url ? `
                        <div class="card-image">
                            <img src="${card.image_url}" alt="Изображение карточки" loading="lazy">
                        </div>
                    ` : ''}
                </div>
                
                <div class="card-actions">
                    <button class="btn btn-danger delete-card" data-card-id="${card.id}" title="Удалить карточку">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Привязка событий для карточек
     */
    bindCardEvents() {
        // Кнопки удаления
        document.querySelectorAll('.delete-card').forEach(button => {
            button.addEventListener('click', (e) => {
                const cardId = parseInt(e.target.closest('.delete-card').dataset.cardId);
                if (confirm('Вы уверены, что хотите удалить эту карточку?')) {
                    this.deleteCard(cardId);
                }
            });
        });
    }
    
    /**
     * Удаление карточки
     */
    async deleteCard(cardId) {
        const card = this.cards.find(c => c.id === cardId);
        if (!card) return;
        
        const confirmed = confirm(
            `Вы уверены, что хотите удалить карточку "${card.front_text}"?\n\nЭто действие нельзя отменить.`
        );
        
        if (!confirmed) return;
        
        try {
            const response = await this.apiClient.client.delete(
                `/api/cards/${cardId}?user_id=${this.currentUser.id}`
            );
            
            if (response.ok) {
                this.showSuccess('Карточка успешно удалена!');
                await this.loadCards();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка при удалении карточки');
            }
            
        } catch (error) {
            console.error('[CardManager] Ошибка удаления карточки:', error);
            this.showError('Ошибка при удалении карточки: ' + error.message);
        }
    }
    
    /**
     * Экранирование HTML
     */
    escapeHtml(text) {
        if (!text) return '';
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
            this.elements.submitButton.disabled = loading || !this.validateForm();
            const spinner = this.elements.submitButton.querySelector('.loading-spinner');
            const text = this.elements.submitButton.querySelector('.button-text');
            
            if (loading) {
                spinner.style.display = 'inline-block';
                text.style.display = 'none';
            } else {
                spinner.style.display = 'none';
                text.style.display = 'inline';
            }
        }
    }
    
    /**
     * Показать сообщение об успехе
     */
    showSuccess(message) {
        // Используем систему уведомлений приложения
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }
    
    /**
     * Показать сообщение об ошибке
     */
    showError(message) {
        // Используем систему уведомлений приложения
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'error');
        } else {
            alert('Ошибка: ' + message);
        }
    }
    
    /**
     * Показать информационное сообщение
     */
    showInfo(message) {
        // Используем систему уведомлений приложения
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, 'info');
        } else {
            alert(message);
        }
    }
}

// Экспорт в глобальную область видимости
window.CardManager = CardManager;

console.log('[CardManager] Card manager component loaded');