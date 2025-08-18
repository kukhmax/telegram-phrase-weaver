// Главный файл, который управляет всем приложением
import { api, setAuthToken } from '/static/js/api.js';
import { DOMElements, showWindow, renderDecks, showLoading, showError } from '/static/js/ui.js';

// Глобальные переменные для хранения данных
let currentGeneratedData = null;
let selectedPhrases = new Set();
let currentDeckId = null;

// Функция для извлечения кода языка из строки
function extractLanguageCode(langText) {
    // Извлекаем код языка из строки типа "🇵🇹 PT" -> "pt"
    const match = langText.match(/([A-Z]{2})/);
    return match ? match[1].toLowerCase() : 'en';
}

// Функция для получения флага по коду языка
function getFlagByCode(langCode) {
    const flags = {
        'en': '🇺🇸',
        'ru': '🇷🇺', 
        'es': '🇪🇸',
        'pt': '🇵🇹',
        'pl': '🇵🇱'
    };
    return flags[langCode] || '🌐';
}

// Функция для отображения сгенерированных фраз
function displayGeneratedPhrases(data, langFrom, langTo) {
    currentGeneratedData = data;
    selectedPhrases.clear();
    
    const container = document.getElementById('phrases-container');
    container.innerHTML = '';
    
    // Создаем карточки фраз
    const allPhrases = [];
    
    // Добавляем оригинальную фразу
    if (data.original_phrase) {
        allPhrases.push({
            original: data.original_phrase.original,
            translation: data.original_phrase.translation,
            isOriginal: true
        });
    }
    
    // Добавляем дополнительные примеры
    if (data.additional_examples) {
        data.additional_examples.forEach(example => {
            allPhrases.push({
                original: example.original,
                translation: example.translation,
                isOriginal: false
            });
        });
    }
    
    // Создаем HTML для каждой фразы
    allPhrases.forEach((phrase, index) => {
        const phraseCard = createPhraseCard(phrase, index, langFrom, langTo);
        container.appendChild(phraseCard);
    });
    
    // Обновляем счетчики
    updatePhrasesCounter(allPhrases.length, 0);
    
    // Обновляем изображение ключевого слова
    updatePhraseImage(data.image_path);
}

// Функция для создания карточки фразы
function createPhraseCard(phrase, index, langFrom, langTo) {
    const card = document.createElement('div');
    card.className = 'phrase-card';
    card.dataset.index = index;
    
    card.innerHTML = `
        <div class="phrase-content">
            <div class="phrase-line">
                <span class="flag-emoji">${langFrom.split(' ')[0]}</span>
                <span class="phrase-text">${phrase.original}</span>
                <button class="audio-btn" onclick="playAudio('${phrase.original.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${extractLanguageCode(langFrom)}')" title="Прослушать">
                    🔊
                </button>
            </div>
            <div class="phrase-line">
                <span class="flag-emoji">${langTo.split(' ')[0]}</span>
                <span class="phrase-text">${phrase.translation}</span>
                <button class="audio-btn" onclick="playAudio('${phrase.translation.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${extractLanguageCode(langTo)}')" title="Прослушать">
                    🔊
                </button>
            </div>
        </div>
        <div class="phrase-actions">
            <button class="phrase-btn select-btn" onclick="togglePhraseSelection(${index})">
                Выбрать
            </button>
            <button class="phrase-btn delete-phrase-btn" onclick="deletePhraseCard(${index})">
                Удалить
            </button>
        </div>
    `;
    
    return card;
}

// Функция для переключения выбора фразы
window.togglePhraseSelection = function(index) {
    const card = document.querySelector(`[data-index="${index}"]`);
    const button = card.querySelector('.select-btn');
    
    if (selectedPhrases.has(index)) {
        selectedPhrases.delete(index);
        card.classList.remove('selected');
        button.textContent = 'Выбрать';
        button.classList.remove('selected');
    } else {
        selectedPhrases.add(index);
        card.classList.add('selected');
        button.textContent = 'Выбрано';
        button.classList.add('selected');
    }
    
    updatePhrasesCounter();
};

// Функция для удаления карточки фразы
window.deletePhraseCard = function(index) {
    const card = document.querySelector(`[data-index="${index}"]`);
    if (card) {
        // Удаляем из выбранных, если была выбрана
        selectedPhrases.delete(index);
        card.remove();
        updatePhrasesCounter();
    }
};

// Функция для обновления счетчиков
function updatePhrasesCounter(totalCount = null, selectedCount = null) {
    if (totalCount === null) {
        totalCount = document.querySelectorAll('.phrase-card').length;
    }
    if (selectedCount === null) {
        selectedCount = selectedPhrases.size;
    }
    
    document.getElementById('total-phrases-count').textContent = totalCount;
    document.getElementById('selected-phrases-count').textContent = selectedCount;
    document.getElementById('save-count').textContent = selectedCount;
    
    // Управляем состоянием кнопки сохранения
    const saveBtn = document.getElementById('save-selected-btn');
    saveBtn.disabled = selectedCount === 0;
}

// Функция для отображения карточек колоды
async function displayDeckCards(deckId) {
    try {
        showLoading('Загружаем карточки...');
        
        const response = await api.getDeckCards(deckId);
        
        if (response && response.deck && response.cards) {
            // Обновляем информацию о колоде
            document.getElementById('cards-deck-name').textContent = response.deck.name;
            document.getElementById('cards-lang-from-display').textContent = response.deck.lang_from;
            document.getElementById('cards-lang-to-display').textContent = response.deck.lang_to;
            
            const container = document.getElementById('cards-container');
            const noCardsMessage = document.getElementById('no-cards-message');
            
            container.innerHTML = '';
            
            if (response.cards.length === 0) {
                noCardsMessage.style.display = 'block';
                container.style.display = 'none';
            } else {
                noCardsMessage.style.display = 'none';
                container.style.display = 'flex';
                
                // Создаем карточки
                response.cards.forEach(card => {
                    const cardElement = createSavedCard(card, response.deck);
                    container.appendChild(cardElement);
                });
            }
        }
    } catch (error) {
        console.error('Error loading deck cards:', error);
        showError(`Ошибка загрузки карточек: ${error.message}`);
    }
}

// Функция для создания карточки в окне просмотра
function createSavedCard(card, deck) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'saved-card';
    cardDiv.dataset.cardId = card.id;
    
    // Получаем флаги языков
    const langFromFlag = deck.lang_from.split(' ')[0];
    const langToFlag = deck.lang_to.split(' ')[0];
    
    cardDiv.innerHTML = `
        <div class="card-content">
            <div class="card-side front">
                <span class="card-flag">${langFromFlag}</span>
                <span class="card-text">${card.front_text}</span>
                <button class="audio-btn" onclick="playAudio('${card.front_text.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${extractLanguageCode(deck.lang_from)}')" title="Прослушать">
                    🔊
                </button>
            </div>
            <div class="card-side back">
                <span class="card-flag">${langToFlag}</span>
                <span class="card-text">${card.back_text}</span>
                <button class="audio-btn" onclick="playAudio('${card.back_text.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${extractLanguageCode(deck.lang_to)}')" title="Прослушать">
                    🔊
                </button>
            </div>
        </div>
        <div class="card-actions">
            <button class="card-btn practice-btn" onclick="practiceCard(${card.id})">
                Тренировать
            </button>
            <button class="card-btn delete-card-btn" onclick="deleteCard(${card.id})">
                Удалить
            </button>
        </div>
    `;
    
    return cardDiv;
}

// Функция для тренировки карточки (заглушка)
window.practiceCard = function(cardId) {
    alert(`Тренировка карточки ${cardId} будет реализована позже`);
};

// Функция для удаления карточки (заглушка)
window.deleteCard = function(cardId) {
    if (confirm('Вы уверены, что хотите удалить эту карточку?')) {
        alert(`Удаление карточки ${cardId} будет реализовано позже`);
    }
};

// Функция для воспроизведения аудио
window.playAudio = async function(text, langCode) {
    try {
        // Очищаем текст от HTML тегов
        const cleanText = text.replace(/<[^>]*>/g, '');
        
        // Сначала пробуем Web Speech API (для десктопа)
        if ('speechSynthesis' in window && !window.Telegram?.WebApp) {
            // Останавливаем предыдущее воспроизведение
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(cleanText);
            
            // Настройка языка
            const langMap = {
                'en': 'en-US',
                'ru': 'ru-RU',
                'es': 'es-ES', 
                'pt': 'pt-PT',
                'pl': 'pl-PL'
            };
            
            utterance.lang = langMap[langCode] || 'en-US';
            utterance.rate = 0.8;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            window.speechSynthesis.speak(utterance);
        } else {
            // Для Telegram WebApp используем серверную генерацию аудио
            try {
                const response = await api.generateAudio({
                    text: cleanText,
                    lang_code: langCode
                });
                
                if (response && response.audio_url) {
                     const audio = new Audio(response.audio_url);
                     
                     // Добавляем обработчик ошибки загрузки
                     audio.addEventListener('error', async (e) => {
                         console.log('Audio file not found, waiting for generation...');
                         // Ждем немного и пробуем еще раз
                         setTimeout(() => {
                             const retryAudio = new Audio(response.audio_url);
                             retryAudio.play().catch(retryError => {
                                 console.error('Retry audio play failed:', retryError);
                                 alert('Ошибка воспроизведения аудио');
                             });
                         }, 1000);
                     });
                     
                     audio.play().catch(error => {
                         console.error('Error playing audio file:', error);
                         // Не показываем alert при первой ошибке, так как файл может еще генерироваться
                     });
                 } else {
                     throw new Error('No audio URL received');
                 }
            } catch (error) {
                console.error('Error generating audio:', error);
                alert('Ошибка генерации аудио');
            }
        }
    } catch (error) {
        console.error('Error playing audio:', error);
        alert('Ошибка воспроизведения аудио');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram?.WebApp || {};
    if (tg.ready) {
        tg.ready();
    }

    // ============================================
    //               ЛОГИКА ПРИЛОЖЕНИЯ
    // ============================================

    // Функция для обновления и перерисовки списка колод
    async function refreshDecks() {
        try {
            showLoading('Загружаем ваши колоды...');
            const decks = await api.getDecks();
            renderDecks(decks);
        } catch (error) {
            console.error("Failed to refresh decks:", error);
            showError(error.message || 'Не удалось загрузить колоды');
        }
    }

    // Главная функция инициализации
    async function main() {
    try {
        let authData;

        // ПРОВЕРКА НА ОТЛАДОЧНЫЙ РЕЖИМ
        const isDebugMode = (window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' || 
                           window.location.hostname.includes('fly.dev') ||
                           window.location.protocol === 'file:');

        if (tg.initDataUnsafe && Object.keys(tg.initDataUnsafe).length > 0 && !isDebugMode) {
            // Режим продакшена (внутри Telegram)
            console.log("Running in Production Mode (inside Telegram)");
            authData = await api.authenticate(tg.initData);
        } else if (isDebugMode) {
            // Режим отладки (локально в браузере)
            console.log("Running in Debug Mode (localhost)");
            authData = await api.authenticateDebug(); // Вызываем новый метод API
        } else {
            // Запуск в браузере, но не локально
            throw new Error("Telegram.WebApp.initData is empty. Please run the app inside Telegram.");
        }
        
        // 1. Аутентификация
        setAuthToken(authData.access_token);
        console.log("Authentication successful, token set.");
        
        // 2. Первоначальная загрузка и отрисовка колод
        await refreshDecks();

        // 3. Показываем главный экран
        showWindow('main-window');
    } catch (error) {
        console.error("Initialization failed:", error);
        DOMElements.decksContainer.innerHTML = `<p style='color: red;'>${error.message}</p>`;
    }
}
    // ============================================
    //             ОБРАБОТЧИКИ СОБЫТИЙ
    // ============================================

    // Нажатие на "+" на главном экране
    document.getElementById('add-deck-btn').addEventListener('click', () => {
        showWindow('create-deck-window');
    });

    // Нажатие на "Назад" в окне создания
    document.getElementById('back-to-main-btn').addEventListener('click', async () => {
        await refreshDecks(); // Обновляем список колод
        showWindow('main-window');
    });

    // Обработчик кнопки "Назад" из окна карточек
    document.getElementById('back-from-cards-btn').addEventListener('click', async () => {
        await refreshDecks(); // Обновляем список колод
        showWindow('main-window');
    });

    // Отправка формы создания новой колоды
    DOMElements.createDeckForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        const formData = new FormData(event.target);
        const deckData = Object.fromEntries(formData.entries());
        
        // Валидация формы
        if (!deckData.name || deckData.name.trim().length < 2) {
            alert('Название колоды должно содержать минимум 2 символа');
            return;
        }
        
        if (!deckData.lang_from || !deckData.lang_to) {
            alert('Пожалуйста, выберите оба языка');
            return;
        }
        
        if (deckData.lang_from === deckData.lang_to) {
            alert('Изучаемый язык и язык перевода должны отличаться');
            return;
        }
        
        const submitBtn = DOMElements.createDeckForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true; // Блокируем кнопку на время запроса
        submitBtn.textContent = '⏳ Создание...';

        try {
            await api.createDeck(deckData);
            event.target.reset(); // Очищаем форму
            showWindow('main-window'); // Возвращаемся на главный экран
            await refreshDecks(); // Обновляем список колод, чтобы увидеть новую
        } catch (error) {
            console.error("Failed to create deck:", error);
            alert(`Ошибка создания колоды: ${error.message}`); // Показываем ошибку
        } finally {
            submitBtn.disabled = false; // Разблокируем кнопку
            submitBtn.textContent = '➕ Создать колоду';
        }
    });

    // Обработчик клика по header для возврата на главное окно
    document.addEventListener('click', (event) => {
        if (event.target.closest('.clickable-header')) {
            // Возвращаемся на главное окно только если мы не на нем
            const mainWindow = document.getElementById('main-window');
            if (mainWindow.classList.contains('hidden')) {
                showWindow('main-window');
            }
        }
    });

    // Обработчик клика по колоде для перехода к генерации карточек
    document.addEventListener('click', (event) => {
        const deckCard = event.target.closest('.deck-card');
        if (deckCard && !event.target.closest('.deck-actions')) {
            // Клик по колоде, но не по кнопкам действий
            
            // Сохраняем ID колоды для последующего сохранения карточек
            currentDeckId = parseInt(deckCard.dataset.deckId);
            
            // Извлекаем данные о языках из колоды
            const langFromElement = deckCard.querySelector('.lang-from');
            const langToElement = deckCard.querySelector('.lang-to');
            
            if (langFromElement && langToElement) {
                const langFrom = langFromElement.textContent;
                const langTo = langToElement.textContent;
                
                // Отображаем языки в окне генерации карточек
                document.getElementById('lang-from-display').textContent = langFrom;
                document.getElementById('lang-to-display').textContent = langTo;
            }
            
            showWindow('generate-cards-window');
        }
    });

    // Обработчик кнопки "Удалить"
    document.addEventListener('click', async (event) => {
        if (event.target.classList.contains('delete-btn')) {
            event.preventDefault();
            
            const deckCard = event.target.closest('.deck-card');
            const deckName = deckCard.querySelector('.deck-name').textContent;
            
            if (confirm(`Вы уверены, что хотите удалить колоду "${deckName}"?`)) {
                try {
                    // Получаем ID колоды из data-атрибута
                    const deckId = deckCard.dataset.deckId;
                    
                    // Удаляем колоду через API
                    await api.deleteDeck(deckId);
                    
                    // Обновляем список колод
                    await refreshDecks();
                } catch (error) {
                    console.error('Failed to delete deck:', error);
                    alert(`Ошибка удаления колоды: ${error.message}`);
                }
            }
        }
    });

    // Обработчик кнопки "Карточки"
    document.addEventListener('click', async (event) => {
        if (event.target.classList.contains('cards-btn')) {
            event.preventDefault();
            
            const deckCard = event.target.closest('.deck-card');
            const deckId = parseInt(deckCard.dataset.deckId);
            
            // Загружаем и отображаем карточки колоды
            await displayDeckCards(deckId);
            
            showWindow('cards-window');
        }
    });

    // Обработчик формы генерации фраз
    document.getElementById('generate-cards-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const phrase = document.getElementById('phrase-input').value.trim();
        const keyword = document.getElementById('keyword-input').value.trim();
        
        if (!phrase || !keyword) {
            alert('Пожалуйста, заполните все поля');
            return;
        }
        
        // Получаем языки из текущей колоды
        const langFrom = document.getElementById('lang-from-display').textContent;
        const langTo = document.getElementById('lang-to-display').textContent;
        
        // Извлекаем коды языков из текста (например, "🇵🇹 PT" -> "pt")
        const langFromCode = extractLanguageCode(langFrom);
        const langToCode = extractLanguageCode(langTo);
        
        try {
            // Показываем спиннер в кнопке
            showButtonLoading(true);
            showLoading('Генерируем фразы...');
            
            const response = await api.enrichPhrase({
                phrase: phrase,
                keyword: keyword,
                lang_code: langFromCode,
                target_lang: langToCode
            });
            
            if (response) {
                displayGeneratedPhrases(response, langFrom, langTo);
                showWindow('generated-phrases-window');
            } else {
                showError('Не удалось сгенерировать фразы');
            }
        } catch (error) {
            console.error('Error generating phrases:', error);
            showError(`Ошибка генерации: ${error.message}`);
        } finally {
            // Скрываем спиннер в любом случае
            showButtonLoading(false);
        }
     });

    // Обработчики для окна сгенерированных фраз
    document.getElementById('save-selected-btn').addEventListener('click', async () => {
        if (selectedPhrases.size === 0) return;
        
        try {
            showLoading('Сохраняем карточки...');
            
            // Получаем выбранные фразы
            const phrasesToSave = [];
            const allCards = document.querySelectorAll('.phrase-card');
            
            // Проверяем, что currentDeckId установлен
            if (!currentDeckId) {
                showError('Ошибка: не выбрана колода для сохранения карточек');
                return;
            }
            
            console.log('Saving cards to deck ID:', currentDeckId);
            
            selectedPhrases.forEach(index => {
                const card = allCards[index];
                if (card) {
                    const originalText = card.querySelector('.phrase-line:first-child .phrase-text').textContent;
                    const translationText = card.querySelector('.phrase-line:last-child .phrase-text').textContent;
                    
                    const cardData = {
                        deck_id: currentDeckId,
                        front_text: originalText,
                        back_text: translationText,
                        difficulty: 1,
                        next_review: new Date().toISOString(),
                        image_path: currentGeneratedData?.image_path || null
                    };
                    
                    console.log('Card data to save:', cardData);
                    phrasesToSave.push(cardData);
                }
            });
            
            // Сохраняем каждую карточку
            for (const cardData of phrasesToSave) {
                await api.saveCard(cardData);
            }
            
            alert(`Сохранено ${phrasesToSave.length} карточек!`);
            await refreshDecks(); // Обновляем список колод
            showWindow('main-window');
            
        } catch (error) {
            console.error('Error saving cards:', error);
            showError(`Ошибка сохранения: ${error.message}`);
        }
    });
    
    document.getElementById('regenerate-btn').addEventListener('click', () => {
        showWindow('generate-cards-window');
    });
    
    document.getElementById('back-to-main-btn').addEventListener('click', () => {
        showWindow('main-window');
    });

    // Обработчик кнопки "Выделить все"
    const selectAllBtn = document.getElementById('select-all-btn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
        const allCards = document.querySelectorAll('.phrase-card');
        const selectAllBtn = document.getElementById('select-all-btn');
        
        if (selectedPhrases.size === allCards.length) {
            // Если все выделены, снимаем выделение
            selectedPhrases.clear();
            allCards.forEach((card, index) => {
                card.classList.remove('selected');
                const selectBtn = card.querySelector('.select-btn');
                selectBtn.textContent = 'Выбрать';
                selectBtn.classList.remove('selected');
            });
            selectAllBtn.textContent = 'Выделить все';
        } else {
            // Выделяем все
            selectedPhrases.clear();
            allCards.forEach((card, index) => {
                selectedPhrases.add(index);
                card.classList.add('selected');
                const selectBtn = card.querySelector('.select-btn');
                selectBtn.textContent = 'Выбрано';
                selectBtn.classList.add('selected');
            });
            selectAllBtn.textContent = 'Снять выделение';
        }
        
        updatePhrasesCounter();
         });
     }

    // Запускаем приложение
    main();
});

// Функция для управления спиннером в кнопке
function showButtonLoading(show) {
    const spinner = document.querySelector('#enrich-btn .loading-spinner');
    const btnText = document.querySelector('#enrich-btn .btn-text');
    const button = document.getElementById('enrich-btn');
    
    if (show) {
        spinner.classList.remove('hidden');
        btnText.textContent = 'Обогащаем...';
        button.disabled = true;
    } else {
        spinner.classList.add('hidden');
        btnText.textContent = 'Обогатить';
        button.disabled = false;
    }
}

// Функция для обновления изображения в окне фраз
function updatePhraseImage(imagePath) {
    const imageElement = document.getElementById('phrase-image');
    if (imagePath && imagePath.trim() !== '') {
        // Показываем изображение ключевого слова
        imageElement.src = imagePath;
        imageElement.alt = 'Keyword Image';
    } else {
        // Показываем mascot по умолчанию
        imageElement.src = '/static/assets/icons/mascot.png';
        imageElement.alt = 'Mascot';
    }
}