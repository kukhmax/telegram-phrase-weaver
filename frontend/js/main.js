document.addEventListener('DOMContentLoaded', () => {
    // =================================================================
    // 1. ИНИЦИАЛИЗАЦИЯ И ПОЛУЧЕНИЕ ЭЛЕМЕНТОВ DOM
    // =================================================================

    // Получаем объект Telegram Web App для взаимодействия с клиентом Telegram
    const tg = window.Telegram.WebApp;
    // Говорим Telegram, что наше приложение готово к отображению
    tg.ready(); 

    // Находим ключевые элементы на странице, с которыми будем работать
    const decksContainer = document.getElementById('decks-container');
    const noDecksMessage = document.getElementById('no-decks-message');
    const deckCardTemplate = document.getElementById('deck-card-template');
    
    // Состояние приложения. Здесь мы будем хранить данные, полученные с сервера.
    const state = {
        token: null, // Наш JWT токен для авторизации
        user: null,  // Информация о пользователе
        decks: []    // Список колод
    };


    // =================================================================
    // 2. ЛОГИКА АУТЕНТИФИКАЦИИ И ВЗАИМОДЕЙСТВИЯ С API
    // =================================================================

    /**
     * Отправляет initData на бэкенд для верификации и получения JWT токена.
     * Это первый и самый важный запрос к нашему API.
     */
    async function authenticateUser() {
        // Проверяем, есть ли вообще initData. Если запускать в обычном браузере, его не будет.
        if (!tg.initData) {
            console.error("Telegram.WebApp.initData is empty. Are you running in Telegram?");
            // В режиме отладки можно показать сообщение прямо на экране
            decksContainer.innerHTML = "<p style='color: red;'>Ошибка: Запустите приложение через Telegram.</p>";
            return;
        }

        try {
            const response = await fetch(`${config.API_BASE_URL}/auth/telegram`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ init_data: tg.initData })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Authentication failed: ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log("Authentication successful:", data);
            
            // Сохраняем токен и информацию о пользователе в нашем состоянии
            state.token = data.access_token;
            state.user = data.user;

        } catch (error) {
            console.error(error);
            decksContainer.innerHTML = `<p style='color: red;'>Не удалось подключиться к серверу. Попробуйте позже.</p>`;
        }
    }
    
    /**
     * Запрашивает список всех колод для текущего пользователя.
     * Использует JWT токен, полученный при аутентификации.
     */
    async function fetchDecks() {
        if (!state.token) {
            console.error("Cannot fetch decks without an auth token.");
            return;
        }
        
        try {
            const response = await fetch(`${config.API_BASE_URL}/decks/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${state.token}`
                }
            });

            if (!response.ok) {
                 throw new Error(`Failed to fetch decks: ${response.statusText}`);
            }

            const decks = await response.json();
            console.log("Decks fetched:", decks);
            state.decks = decks; // Обновляем состояние

        } catch (error) {
            console.error(error);
        }
    }


    // =================================================================
    // 3. ЛОГИКА ОТОБРАЖЕНИЯ (РЕНДЕРИНГ)
    // =================================================================

    /**
     * Отображает колоды на экране на основе данных из state.decks.
     */
    function renderDecks() {
        // Очищаем контейнер перед отрисовкой
        decksContainer.innerHTML = ''; 

        if (state.decks.length === 0) {
            // Если колод нет, показываем сообщение-заглушку
            noDecksMessage.classList.remove('hidden');
        } else {
            // Если колоды есть, скрываем заглушку и рендерим их
            noDecksMessage.classList.add('hidden');

            state.decks.forEach(deck => {
                // Клонируем содержимое нашего шаблона <template>
                const cardNode = deckCardTemplate.content.cloneNode(true);
                
                // Находим элементы внутри клонированного узла и заполняем их данными
                cardNode.querySelector('.deck-name').textContent = deck.name;
                cardNode.querySelector('.deck-description').textContent = deck.description || '';
                cardNode.querySelector('.lang-from').textContent = getFlagEmoji(deck.lang_from) + ` ${deck.lang_from.toUpperCase()}`;
                cardNode.querySelector('.lang-to').textContent = getFlagEmoji(deck.lang_to) + ` ${deck.lang_to.toUpperCase()}`;
                cardNode.querySelector('.cards-total').textContent = deck.cards_count;
                cardNode.querySelector('.cards-repeat').textContent = deck.due_count;
                
                // Добавляем готовую карточку в контейнер
                decksContainer.appendChild(cardNode);
            });
        }
    }
    
    /**
     * Вспомогательная функция для получения эмодзи флага по коду языка.
     * @param {string} langCode - Двухбуквенный код языка (напр., 'en', 'ru').
     * @returns {string} - Эмодзи флага.
     */
    function getFlagEmoji(langCode) {
        const flagMap = {
            en: '🇺🇸', ru: '🇷🇺', fr: '🇫🇷', de: '🇩🇪',
            es: '🇪🇸', pl: '🇵🇱', pt: '🇵🇹', it: '🇮🇹'
        };
        return flagMap[langCode] || '🏳️';
    }


    // =================================================================
    // 4. ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ПРИЛОЖЕНИЯ
    // =================================================================

    /**
     * Основная асинхронная функция, которая запускает всю логику:
     * 1. Аутентификация
     * 2. Загрузка данных
     * 3. Отображение данных
     */
    async function main() {
        await authenticateUser();
        // Если аутентификация прошла успешно и мы получили токен
        if (state.token) {
            await fetchDecks();
            renderDecks();
        }
    }

    // Запускаем!
    main();
});