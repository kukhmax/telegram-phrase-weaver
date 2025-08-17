// Этот файл отвечает за манипуляции с DOM

// Находим элементы один раз и экспортируем их
export const DOMElements = {
    mainWindow: document.getElementById('main-window'),
    createDeckWindow: document.getElementById('create-deck-window'),
    generateCardsWindow: document.getElementById('generate-cards-window'),
    cardsWindow: document.getElementById('cards-window'),
    decksContainer: document.getElementById('decks-container'),
    noDecksMessage: document.getElementById('no-decks-message'),
    deckCardTemplate: document.getElementById('deck-card-template'),
    createDeckForm: document.getElementById('create-deck-form'),
};

/**
 * Показывает одно окно приложения, скрывая все остальные.
 * @param {string} windowId - ID окна, которое нужно показать (напр., 'main-window').
 */
export function showWindow(windowId) {
    document.querySelectorAll('.app-window').forEach(win => {
        win.classList.add('hidden');
    });
    document.getElementById(windowId).classList.remove('hidden');
    
    // Управляем классом main-active для контейнера
    const appContainer = document.querySelector('.app-container');
    if (windowId === 'main-window') {
        appContainer.classList.add('main-active');
    } else {
        appContainer.classList.remove('main-active');
    }
}

/**
 * Отрисовывает карточки колод
 * @param {Array} decks - Массив объектов колод
 */
export function renderDecks(decks) {
    DOMElements.decksContainer.innerHTML = ''; 

    if (decks.length === 0) {
        DOMElements.noDecksMessage.classList.remove('hidden');
    } else {
        DOMElements.noDecksMessage.classList.add('hidden');
        decks.forEach(deck => {
            const cardNode = DOMElements.deckCardTemplate.content.cloneNode(true);
            const deckCard = cardNode.querySelector('.deck-card');
            
            // Добавляем ID колоды как data-атрибут
            deckCard.dataset.deckId = deck.id;
            
            cardNode.querySelector('.deck-name').textContent = deck.name;
            cardNode.querySelector('.deck-description').textContent = deck.description || '';
            cardNode.querySelector('.lang-from').textContent = getFlagEmoji(deck.lang_from) + ` ${deck.lang_from.toUpperCase()}`;
            cardNode.querySelector('.lang-to').textContent = getFlagEmoji(deck.lang_to) + ` ${deck.lang_to.toUpperCase()}`;
            cardNode.querySelector('.cards-total').textContent = deck.cards_count;
            cardNode.querySelector('.cards-repeat').textContent = deck.due_count;
            DOMElements.decksContainer.appendChild(cardNode);
        });
    }
}

function getFlagEmoji(langCode) {
    const flagMap = {
        en: '🇺🇸', ru: '🇷🇺', fr: '🇫🇷', de: '🇩🇪',
        es: '🇪🇸', pl: '🇵🇱', pt: '🇵🇹', it: '🇮🇹'
    };
    return flagMap[langCode] || '🏳️';
}

/**
 * Показывает loading состояние
 */
export function showLoading(message = 'Загрузка...') {
    DOMElements.decksContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #666;">
            <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Показывает ошибку
 */
export function showError(message) {
    DOMElements.decksContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #ff4757;">
            <div style="font-size: 24px; margin-bottom: 10px;">❌</div>
            <p>Ошибка: ${message}</p>
            <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #f4c300; border: none; border-radius: 10px; cursor: pointer;">Попробовать снова</button>
        </div>
    `;
}