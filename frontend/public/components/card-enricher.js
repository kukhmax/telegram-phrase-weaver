/**
 * CardEnricher - модальное окно для AI-генерации карточек
 * Позволяет пользователю ввести фразу и ключевое слово,
 * получить AI-сгенерированные варианты и добавить их в колоду
 */
class CardEnricher {
    constructor() {
        this.currentDeckId = null;
        this.generatedPhrases = [];
        this.imageQuery = null;
        this.isLoading = false;
        this.isOpen = false;
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        const modalHTML = `
            <div id="card-enricher-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Обогащение карточек</h2>
                        <button class="close-btn" id="close-enricher">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="enricher-form">
                            <div class="form-group">
                                <label for="phrase-input">Фраза:</label>
                                <input type="text" id="phrase-input" placeholder="Введите фразу для изучения" required>
                            </div>
                            <div class="form-group">
                                <label for="keyword-input">Ключевое слово:</label>
                                <input type="text" id="keyword-input" placeholder="Введите ключевое слово" required>
                            </div>
                            <div class="form-actions">
                                <button type="submit" class="btn-primary" id="enrich-btn">
                                    <span class="btn-text">Обогатить</span>
                                    <span class="loading-spinner" style="display: none;">⏳</span>
                                </button>
                            </div>
                        </form>
                        
                        <div id="enricher-results" style="display: none;">
                            <div class="results-header">
                                <h3>Сгенерированные фразы</h3>
                                <div id="image-query-info" style="display: none;">
                                    <small>Запрос для поиска изображения: <span id="image-query-text"></span></small>
                                </div>
                            </div>
                            <div id="phrases-list"></div>
                            <div class="results-actions">
                                <button class="btn-secondary" id="select-all-btn">Выбрать все</button>
                                <button class="btn-secondary" id="deselect-all-btn">Снять выделение</button>
                                <button class="btn-primary" id="create-cards-btn">Создать карточки</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    bindEvents() {
        // Закрытие модального окна
        document.getElementById('close-enricher').addEventListener('click', () => {
            this.close();
        });

        // Закрытие по клику вне модального окна
        document.getElementById('card-enricher-modal').addEventListener('click', (e) => {
            if (e.target.id === 'card-enricher-modal') {
                this.close();
            }
        });

        // Обработка формы обогащения
        document.getElementById('enricher-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generatePhrases();
        });

        // Кнопки управления выбором
        document.getElementById('select-all-btn').addEventListener('click', () => {
            this.selectAllPhrases(true);
        });

        document.getElementById('deselect-all-btn').addEventListener('click', () => {
            this.selectAllPhrases(false);
        });

        // Создание карточек
        document.getElementById('create-cards-btn').addEventListener('click', () => {
            this.addSelectedCards();
        });
    }

    open(deckId) {
        this.currentDeckId = deckId;
        this.isOpen = true;
        document.getElementById('card-enricher-modal').style.display = 'flex';
        document.getElementById('phrase-input').focus();
        this.clearForm();
    }

    close() {
        this.isOpen = false;
        document.getElementById('card-enricher-modal').style.display = 'none';
        this.clearForm();
    }

    clearForm() {
        document.getElementById('enricher-form').reset();
        document.getElementById('enricher-results').style.display = 'none';
        document.getElementById('image-query-info').style.display = 'none';
        this.generatedPhrases = [];
        this.imageQuery = null;
        this.setLoading(false);
    }

    setLoading(loading) {
        const btn = document.getElementById('enrich-btn');
        const btnText = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.loading-spinner');
        
        if (loading) {
            btn.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'inline';
        } else {
            btn.disabled = false;
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    }

    async generatePhrases() {
        const phrase = document.getElementById('phrase-input').value.trim();
        const keyword = document.getElementById('keyword-input').value.trim();

        if (!phrase || !keyword) {
            alert('Пожалуйста, заполните все поля');
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch('/api/cards/enrich', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    original_phrase: phrase,
                    keyword: keyword,
                    deck_id: this.currentDeckId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayResults(data);
        } catch (error) {
            console.error('Ошибка при обогащении фраз:', error);
            alert('Произошла ошибка при генерации фраз. Попробуйте еще раз.');
        } finally {
            this.setLoading(false);
        }
    }

    displayResults(data) {
        this.generatedPhrases = data.phrases || [];
        this.imageQuery = data.image_query;

        // Показываем запрос для поиска изображения
        if (this.imageQuery) {
            document.getElementById('image-query-text').textContent = this.imageQuery;
            document.getElementById('image-query-info').style.display = 'block';
        }

        // Отображаем список фраз
        const phrasesList = document.getElementById('phrases-list');
        phrasesList.innerHTML = '';

        this.generatedPhrases.forEach((phrase, index) => {
            const phraseItem = document.createElement('div');
            phraseItem.className = 'phrase-item';
            phraseItem.innerHTML = `
                <label class="phrase-checkbox">
                    <input type="checkbox" ${phrase.selected ? 'checked' : ''} data-index="${index}">
                    <div class="phrase-content">
                        <div class="phrase-original">${phrase.original}</div>
                        <div class="phrase-translation">${phrase.translation}</div>
                    </div>
                </label>
            `;
            phrasesList.appendChild(phraseItem);
        });

        // Добавляем обработчики для чекбоксов
        phrasesList.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                const index = parseInt(e.target.dataset.index);
                this.generatedPhrases[index].selected = e.target.checked;
            }
        });

        document.getElementById('enricher-results').style.display = 'block';
    }

    selectAllPhrases(selected) {
        this.generatedPhrases.forEach((phrase, index) => {
            phrase.selected = selected;
            const checkbox = document.querySelector(`input[data-index="${index}"]`);
            if (checkbox) {
                checkbox.checked = selected;
            }
        });
    }

    async addSelectedCards() {
        const selectedPhrases = this.generatedPhrases.filter(phrase => phrase.selected);
        
        if (selectedPhrases.length === 0) {
            alert('Выберите хотя бы одну фразу для создания карточек');
            return;
        }

        try {
            const response = await fetch('/api/cards/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phrases: selectedPhrases,
                    deck_id: this.currentDeckId,
                    difficulty: 1
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            alert(`Успешно создано ${result.total_created} карточек`);
            
            // Закрываем модальное окно и обновляем список карточек
            this.close();
            
            // Уведомляем другие компоненты об обновлении
            window.dispatchEvent(new CustomEvent('cardsUpdated', {
                detail: { deckId: this.currentDeckId }
            }));
            
        } catch (error) {
            console.error('Ошибка при создании карточек:', error);
            alert('Произошла ошибка при создании карточек. Попробуйте еще раз.');
        }
    }
}

// Создаем глобальный экземпляр
window.cardEnricher = new CardEnricher();

// Экспорт для модульной системы
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CardEnricher;
}