/**
 * Простая версия DeckManager для работы без внешних зависимостей
 */
class SimpleDeckManager {
    constructor() {
        this.languages = [
            { code: 'en', name: 'English' },
            { code: 'ru', name: 'Русский' },
            { code: 'es', name: 'Español' },
            { code: 'fr', name: 'Français' },
            { code: 'de', name: 'Deutsch' },
            { code: 'it', name: 'Italiano' },
            { code: 'pt', name: 'Português' },
            { code: 'pl', name: 'Polski' },

        ];
        
        this.elements = {};
        this.isFormVisible = false;
        this.decks = this.loadDecksFromStorage();
        this.init();
    }
    
    init() {
        this.createDOM();
        this.bindEvents();
        console.log('[SimpleDeckManager] Initialized');
    }
    
    createDOM() {
        // Находим контейнер
        this.elements.container = document.getElementById('deck-manager');
        
        if (!this.elements.container) {
            console.error('[SimpleDeckManager] Container not found');
            return;
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
                            <label>Изучаемый язык *</label>
                            <div class="checkbox-group" id="source-language-group">
                                ${this.languages.map(lang => 
                                    `<label class="checkbox-item">
                                        <input type="checkbox" name="source_language" value="${lang.code}">
                                        <span class="checkmark"></span>
                                        ${lang.name}
                                    </label>`
                                ).join('')}
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Язык перевода *</label>
                            <div class="checkbox-group" id="target-language-group">
                                ${this.languages.map(lang => 
                                    `<label class="checkbox-item">
                                        <input type="checkbox" name="target_language" value="${lang.code}">
                                        <span class="checkmark"></span>
                                        ${lang.name}
                                    </label>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" id="cancel-deck-btn" class="btn btn-secondary">
                            Отмена
                        </button>
                        <button type="submit" id="submit-deck-btn" class="btn btn-primary" disabled>
                            Создать колоду
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Список колод -->
            <div id="decks-list" class="decks-list">
                <!-- Список будет заполнен динамически -->
            </div>
        `;
        
        // Сохраняем ссылки на элементы
        this.elements.createButton = document.getElementById('create-deck-btn');
        this.elements.createForm = document.getElementById('create-deck-form');
        this.elements.cancelButton = document.getElementById('cancel-deck-btn');
        this.elements.nameInput = document.getElementById('deck-name');
        this.elements.descriptionInput = document.getElementById('deck-description');
        this.elements.sourceLanguageGroup = document.getElementById('source-language-group');
        this.elements.targetLanguageGroup = document.getElementById('target-language-group');
        this.elements.submitButton = document.getElementById('submit-deck-btn');
        this.elements.decksList = document.getElementById('decks-list');
        
        // Отображаем существующие колоды
        this.renderDecks();
    }
    
    bindEvents() {
        if (!this.elements.createButton) return;
        
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
        
        // Обработчики для checkbox'ов языков
        this.elements.sourceLanguageGroup.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.handleLanguageCheckbox(e.target, 'source_language');
                this.validateForm();
            }
        });
        
        this.elements.targetLanguageGroup.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.handleLanguageCheckbox(e.target, 'target_language');
                this.validateForm();
            }
        });
    }
    
    showCreateForm() {
        this.elements.createForm.style.display = 'block';
        this.elements.nameInput.focus();
        this.isFormVisible = true;
        
        // Прокручиваем к форме
        this.elements.createForm.scrollIntoView({ behavior: 'smooth' });
    }
    
    hideCreateForm() {
        this.elements.createForm.style.display = 'none';
        this.isFormVisible = false;
        
        // Очищаем форму
        document.getElementById('deck-form').reset();
        this.validateForm();
    }
    
    handleLanguageCheckbox(checkbox, groupName) {
        // Снимаем выделение с других checkbox'ов в той же группе
        const groupElement = groupName === 'source_language' ? 
            this.elements.sourceLanguageGroup : this.elements.targetLanguageGroup;
        
        const checkboxes = groupElement.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            if (cb !== checkbox) {
                cb.checked = false;
            }
        });
    }
    
    validateForm() {
        const name = this.elements.nameInput.value.trim();
        const sourceLanguage = this.getSelectedLanguage('source_language');
        const targetLanguage = this.getSelectedLanguage('target_language');
        
        const isValid = name && sourceLanguage && targetLanguage && sourceLanguage !== targetLanguage;
        
        this.elements.submitButton.disabled = !isValid;
        
        // Показываем ошибку если языки одинаковые
        if (sourceLanguage && targetLanguage && sourceLanguage === targetLanguage) {
            this.showFormError('Изучаемый язык и язык перевода должны быть разными');
        } else {
            this.hideFormError();
        }
        
        return isValid;
    }
    
    getSelectedLanguage(groupName) {
        const groupElement = groupName === 'source_language' ? 
            this.elements.sourceLanguageGroup : this.elements.targetLanguageGroup;
        
        const checkedCheckbox = groupElement.querySelector('input[type="checkbox"]:checked');
        return checkedCheckbox ? checkedCheckbox.value : null;
    }
    
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
    
    hideFormError() {
        const errorElement = document.querySelector('.form-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    handleCreateDeck() {
        if (!this.validateForm()) {
            return;
        }
        
        // Собираем данные формы
        const formData = {
            id: Date.now(), // Простой ID на основе времени
            name: this.elements.nameInput.value.trim(),
            description: this.elements.descriptionInput.value.trim() || null,
            source_language: this.getSelectedLanguage('source_language'),
            target_language: this.getSelectedLanguage('target_language'),
            created_at: new Date().toISOString(),
            card_count: 0
        };
        
        console.log('[SimpleDeckManager] Creating deck:', formData);
        
        // Добавляем колоду в список
        this.decks.push(formData);
        
        // Сохраняем в localStorage
        this.saveDecksToStorage();
        
        // Обновляем отображение списка
        this.renderDecks();
        
        // Показываем сообщение об успехе
        this.showSuccessMessage(`Колода "${formData.name}" создана!`);
        
        // Скрываем форму
        this.hideCreateForm();
        
        // Обновляем главный экран с новыми колодами
        this.updateMainScreenDecks();
        
        // Возвращаемся на главный экран
        setTimeout(() => {
            if (typeof goHome === 'function') {
                goHome();
            }
        }, 1500); // Даем время показать сообщение об успехе
    }
    
    getLanguageName(code) {
        const language = this.languages.find(lang => lang.code === code);
        return language ? language.name : code;
    }
    
    getLanguageFlag(code) {
        const flags = {
            'en': '🇺🇸',
            'ru': '🇷🇺',
            'fr': '🇫🇷',
            'de': '🇩🇪',
            'es': '🇪🇸',
            'it': '🇮🇹',
            'pt': '🇵🇹',
            'pl': '🇵🇱',
        };
        return flags[code] || '🌐';
    }
    
    // Методы для работы с localStorage
    loadDecksFromStorage() {
        try {
            const stored = localStorage.getItem('phraseweaver_decks');
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('[SimpleDeckManager] Error loading decks from storage:', error);
            return [];
        }
    }
    
    saveDecksToStorage() {
        try {
            localStorage.setItem('phraseweaver_decks', JSON.stringify(this.decks));
        } catch (error) {
            console.error('[SimpleDeckManager] Error saving decks to storage:', error);
        }
    }
    
    // Рендеринг списка колод
    renderDecks() {
        if (!this.elements.decksList) return;
        
        if (this.decks.length === 0) {
            this.elements.decksList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📚</div>
                    <h3>У вас пока нет колод</h3>
                    <p>Создайте свою первую колоду для изучения языков</p>
                </div>
            `;
            return;
        }
        
        const decksHTML = this.decks.map(deck => this.renderDeckCard(deck)).join('');
        this.elements.decksList.innerHTML = decksHTML;
    }
    
    // Рендеринг карточки колоды
    renderDeckCard(deck) {
        const sourceLanguage = this.getLanguageName(deck.source_language);
        const targetLanguage = this.getLanguageName(deck.target_language);
        const sourceFlag = this.getLanguageFlag(deck.source_language);
        const targetFlag = this.getLanguageFlag(deck.target_language);
        const createdDate = new Date(deck.created_at).toLocaleDateString('ru-RU');
        
        return `
            <div class="deck-card" data-deck-id="${deck.id}">
                <div class="deck-header">
                    <h3 class="deck-title">${deck.name}</h3>
                    <div class="deck-actions">
                        <button class="btn-icon" onclick="simpleDeckManager.editDeck(${deck.id})" title="Редактировать">
                            ✏️
                        </button>
                        <button class="btn-icon" onclick="simpleDeckManager.deleteDeck(${deck.id})" title="Удалить">
                            🗑️
                        </button>
                    </div>
                </div>
                
                ${deck.description ? `<p class="deck-description">${deck.description}</p>` : ''}
                
                <div class="deck-info">
                    <div class="deck-languages">
                        <span class="language-badge source">${sourceFlag} ${sourceLanguage}</span>
                        <span class="arrow">→</span>
                        <span class="language-badge target">${targetFlag} ${targetLanguage}</span>
                    </div>
                    
                    <div class="deck-stats">
                        <span class="card-count">${deck.card_count} карточек</span>
                        <span class="created-date">Создана: ${createdDate}</span>
                    </div>
                </div>
                
                <div class="deck-actions-bottom">
                    <button class="btn btn-secondary" onclick="simpleDeckManager.viewDeck(${deck.id})">
                        📖 Просмотр
                    </button>
                    <button class="btn btn-primary" onclick="simpleDeckManager.startTraining(${deck.id})">
                        🎯 Тренировка
                    </button>
                </div>
            </div>
        `;
    }
    
    // Показать сообщение об успехе
    showSuccessMessage(message) {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">✅</span>
                <span class="notification-text">${message}</span>
            </div>
        `;
        
        // Добавляем стили если их нет
        if (!document.querySelector('#success-notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'success-notification-styles';
            styles.textContent = `
                .success-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #4CAF50;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 10000;
                    animation: slideIn 0.3s ease-out;
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Заглушки для действий с колодами
    editDeck(deckId) {
        console.log('[SimpleDeckManager] Edit deck:', deckId);
        alert('Редактирование колод будет реализовано в следующих версиях');
    }
    
    deleteDeck(deckId) {
        if (confirm('Вы уверены, что хотите удалить эту колоду?')) {
            this.decks = this.decks.filter(deck => deck.id !== deckId);
            this.saveDecksToStorage();
            this.renderDecks();
            this.showSuccessMessage('Колода удалена');
        }
    }
    
    viewDeck(deckId) {
        console.log('[SimpleDeckManager] View deck:', deckId);
        alert('Просмотр карточек будет реализован в следующих версиях');
    }
    
    startTraining(deckId) {
        console.log('[SimpleDeckManager] Start training:', deckId);
        alert('Тренировка будет реализована в следующих версиях');
    }
    
    // Обновление списка колод на главном экране
    updateMainScreenDecks() {
        const mainDecksContainer = document.getElementById('decks-container');
        if (!mainDecksContainer) return;
        
        // Удаляем только динамически созданные колоды (с классом 'dynamic-deck')
        const dynamicDecks = mainDecksContainer.querySelectorAll('.deck-item.dynamic-deck');
        dynamicDecks.forEach(deck => deck.remove());
        
        // Управляем отображением заглушки
        const emptyMessage = document.getElementById('empty-decks-message');
        if (emptyMessage) {
            if (this.decks.length > 0) {
                emptyMessage.style.display = 'none';
            } else {
                emptyMessage.style.display = 'block';
            }
        }
        
        // Находим кнопку API для вставки новых колод перед ней
        const apiButton = mainDecksContainer.querySelector('.api-button');
        
        // Добавляем новые колоды
        this.decks.forEach(deck => {
            const sourceLanguage = this.getLanguageName(deck.source_language);
            const targetLanguage = this.getLanguageName(deck.target_language);
            const sourceFlag = this.getLanguageFlag(deck.source_language);
            const targetFlag = this.getLanguageFlag(deck.target_language);
            
            const deckElement = document.createElement('div');
            deckElement.className = 'deck-item dynamic-deck';
            deckElement.onclick = () => generateCards(deck.id);
            
            deckElement.innerHTML = `
                <div class="deck-content">
                    <h3 class="deck-title">${deck.name}<br><small>(${sourceFlag} ${sourceLanguage} → ${targetFlag} ${targetLanguage})</small></h3>
                    <div class="deck-stats">
                        <span>Total: ${deck.card_count}</span>
                        <span>To repeat: 0</span>
                    </div>
                </div>
                <div class="deck-actions">
                    <button class="deck-btn cards" onclick="event.stopPropagation(); viewDeckCards(${deck.id})">карточки</button>
                    <button class="deck-btn training" onclick="event.stopPropagation(); startTraining(${deck.id})">тренировка</button>
                </div>
            `;
            
            // Вставляем перед кнопкой API
            if (apiButton) {
                mainDecksContainer.insertBefore(deckElement, apiButton);
            } else {
                mainDecksContainer.appendChild(deckElement);
            }
        });
    }
}

// Глобальная переменная для доступа к менеджеру
window.simpleDeckManager = null;

console.log('[SimpleDeckManager] Module loaded');