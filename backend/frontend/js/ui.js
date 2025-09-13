// Этот файл отвечает за манипуляции с DOM
import { updateInterface, t } from '/static/js/i18n.js';

// Находим элементы один раз и экспортируем их
export const DOMElements = {
    mainWindow: document.getElementById('main-window'),
    createDeckWindow: document.getElementById('create-deck-window'),
    generateCardsWindow: document.getElementById('generate-cards-window'),
    cardsWindow: document.getElementById('cards-window'),
    generatedPhrasesWindow: document.getElementById('generated-phrases-window'),
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

    // Применяем фиксированные стили при переключении окон
    if (window.Telegram && window.Telegram.WebApp) {
    document.body.classList.add('web-style-override');  // Добавьте этот класс в main.css для переопределений
    }
    updateInterface();  // Уже есть, но убедитесь, что оно обновляет стили
    
    // Обновляем переводы при переключении окон
    if (typeof updateInterface === 'function') {
        updateInterface();
    }
    
    // Управляем классом main-active для контейнера
    const appContainer = document.querySelector('.app-container');
    const fabButton = document.getElementById('add-deck-btn');
    
    if (windowId === 'main-window') {
        appContainer.classList.add('main-active');
        // Прямое управление видимостью FAB кнопки
        if (fabButton) {
            fabButton.style.display = 'flex';
        }
        console.log('Main window shown, FAB visible');
    } else {
        appContainer.classList.remove('main-active');
        // Прямое скрытие FAB кнопки
        if (fabButton) {
            fabButton.style.display = 'none';
        }
        console.log('Other window shown, FAB hidden');
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
            
            // Применяем локализацию к только что добавленным элементам
            const addedCard = DOMElements.decksContainer.lastElementChild;
            addedCard.style.backgroundColor = '#ffffff';  // Пример, если нужно override
            const translatableElements = addedCard.querySelectorAll('[data-translate]');
            translatableElements.forEach(element => {
                const key = element.getAttribute('data-translate');
                const translation = t(key);
                if (translation) {
                    element.textContent = translation;
                }
            });
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
            <p>${t('error')}: ${message}</p>
            <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #f4c300; border: none; border-radius: 10px; cursor: pointer;">${t('try_again')}</button>
        </div>
    `;
}