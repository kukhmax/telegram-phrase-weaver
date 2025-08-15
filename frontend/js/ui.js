// Этот файл отвечает за манипуляции с DOM

// Находим элементы один раз и экспортируем их
export const DOMElements = {
    mainWindow: document.getElementById('main-window'),
    createDeckWindow: document.getElementById('create-deck-window'),
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