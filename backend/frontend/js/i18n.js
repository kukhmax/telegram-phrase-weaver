// Система интернационализации (i18n)

// Объект с переводами
const translations = {
    ru: {
        // Общие элементы
        settings: 'Настройки',
        save: 'Сохранить',
        cancel: 'Отмена',
        back: 'Назад',
        delete: 'Удалить',
        edit: 'Редактировать',
        create: 'Создать',
        
        // Языки
        interface_language: 'Язык интерфейса',
        russian: '🇷🇺 Русский',
        english: '🇺🇸 English',
        
        // Главная страница
        my_decks: 'Мои колоды:',
        no_decks_message: 'У вас пока нет колод. Создайте первую колоду для изучения языков!',
        create_deck: 'Создать колоду',
        
        // Создание колоды
        deck_creation: 'Создание колоды',
        deck_name: 'Название колоды',
        deck_name_placeholder: 'Введите название колоды',
        deck_description: 'Описание:',
        deck_description_placeholder: 'Введите описание колоды',
        learning_language: 'Изучаемый язык',
        translation_language: 'Язык перевода',
        select_language: 'Выберите язык',
        create_deck_btn: '➕ Создать колоду',
        back_to_main: '← Назад на главную',
        
        // Генерация фраз
        phrase_generation: 'Генерация карточек',
        phrase_label: 'Фраза:',
        phrase_placeholder: 'Введите фразу для изучения',
        keyword_label: 'Ключевое слово:',
        keyword_placeholder: 'Введите ключевое слово',
        enrich_button: 'Обогатить',
        add_phrase_button: 'Добавить фразу',
        enriching: 'Обогащаем...',
        adding_phrase: 'Добавляем...',
        phrases_for_training: 'Фразы для тренировки',
        phrases_count: 'фраз',
        selected: 'выбрано',
        select_all: 'Выделить все',
        deselect_all: 'Снять выделение',
        save_selected: 'Сохранить выбранные',
        regenerate: 'Обогатить заново',
        
        // Карточки
        cards: 'Карточки',
        training: 'Тренировка',
        
        // Тренировка
        enter_translation: 'Введите перевод...',
        enter_phrase: 'Введите фразу...',
        enter_missing_word: 'Введите пропущенное слово...',
        hint: '💡 Подсказка',
        check: 'Проверить',
        correct_answer: 'Правильный ответ:',
        again: 'Снова',
        good: 'Хорошо',
        easy: 'Легко',
        back_to_main_from_training: '← Назад на главную',
        training_complete: 'Тренировка завершена!',
        
        // Кнопки действий
        add_cards: 'Добавить карточки',
        cards: 'Карточки',
        training: 'Тренировка',
        delete: 'Удалить',
        select: 'Выбрать',
        back_to_main: '← Назад на главную',
        
        // Статистика колод
        total: 'Всего',
        repeat: 'Повтор',
        
        // Статистика
        stats_button: 'Статистика',
        statistics: 'Статистика',
        general_stats: 'Общая статистика',
        total_decks: 'Всего колод',
        total_cards: 'Всего карточек',
        learned_cards: 'Изученные карточки',
        cards_for_repeat: 'Карточки для повтора',
        repeat_stats: 'Статистика повторений',
        again_cards: 'Снова',
        good_cards: 'Хорошо',
        easy_cards: 'Легко',
        deck_distribution: 'Распределение по колодам',
        daily_training: 'Ежедневная тренировка',
        close: 'Закрыть',
        
        // Сообщения
        error: 'Ошибка',
        try_again: 'Попробовать снова',
        card_deleted: 'Карточка успешно удалена!',
        delete_confirmation: 'Вы уверены, что хотите удалить эту карточку?',
        training_interruption: 'Вы уверены, что хотите прервать тренировку?',
        enter_answer: 'Пожалуйста, введите ответ',
        
        // Ошибки и уведомления
        card_delete_error: 'Ошибка при удалении карточки. Попробуйте еще раз.',
        audio_playback_error: 'Ошибка воспроизведения аудио',
        audio_generation_error: 'Ошибка генерации аудио',
        deck_name_min_length: 'Название колоды должно содержать минимум 2 символа',
        select_both_languages: 'Пожалуйста, выберите оба языка',
        languages_must_differ: 'Изучаемый язык и язык перевода должны отличаться',
        deck_creation_error: 'Ошибка создания колоды:',
        deck_deletion_confirm: 'Вы уверены, что хотите удалить колоду',
        deck_deletion_error: 'Ошибка удаления колоды:',
        fill_all_fields: 'Пожалуйста, заполните все поля',
        cards_saved: 'Сохранено {count} карточек!',
        training_completed: 'Тренировка завершена! Вы изучили {count} карточек.',
        loading_cards: 'Загружаем карточки...',
        loading_decks: 'Загружаем ваши колоды...',
        saving_cards: 'Сохраняем карточки...',
        loading_training_cards: 'Загружаем карточки для тренировки...',
        loading_stats: 'Загружаем статистику...',
        stats_load_error: 'Ошибка загрузки статистики',
        no_data: 'Нет данных',
        
        // Подсказки валидации
        fill_this_field: 'Заполните это поле.',
        select_item_from_list: 'Выберите один из пунктов списка.',
        enter_valid_value: 'Введите допустимое значение.',
         
          // Футер
        app_version: 'PhraseWeaver v0.1.0'
    },
    
    en: {
        // General elements
        settings: 'Settings',
        save: 'Save',
        cancel: 'Cancel',
        back: 'Back',
        delete: 'Delete',
        edit: 'Edit',
        create: 'Create',
        
        // Languages
        interface_language: 'Interface Language',
        russian: '🇷🇺 Русский',
        english: '🇺🇸 English',
        
        // Main page
        my_decks: 'My Decks:',
        no_decks_message: 'You don\'t have any decks yet. Create your first deck to start learning languages!',
        create_deck: 'Create Deck',
        
        // Deck creation
        deck_creation: 'Deck Creation',
        deck_name: 'Deck Name',
        deck_name_placeholder: 'Enter deck name',
        deck_description: 'Description:',
        deck_description_placeholder: 'Enter deck description',
        learning_language: 'Learning Language',
        translation_language: 'Translation Language',
        select_language: 'Select Language',
        create_deck_btn: '➕ Create Deck',
        back_to_main: '← Back to Main',
        
        // Phrase generation
        phrase_generation: 'Card Generation',
        phrase_label: 'Phrase:',
        phrase_placeholder: 'Enter phrase for learning',
        keyword_label: 'Keyword:',
        keyword_placeholder: 'Enter keyword',
        enrich_button: 'Enrich',
        add_phrase_button: 'Add phrase',
        enriching: 'Enriching...',
        adding_phrase: 'Adding...',
        phrases_for_training: 'Phrases for Training',
        phrases_count: 'phrases',
        selected: 'selected',
        select_all: 'Select All',
        deselect_all: 'Deselect All',
        save_selected: 'Save Selected',
        regenerate: 'Regenerate',
        
        // Cards
        cards: 'Cards',
        training: 'Training',
        
        // Тренировка
        enter_translation: 'Enter translation...',
        enter_phrase: 'Enter phrase...',
        enter_missing_word: 'Enter missing word...',
        hint: '💡 Hint',
        check: 'Check',
        correct_answer: 'Correct answer:',
        again: 'Again',
        good: 'Good',
        easy: 'Easy',
        back_to_main_from_training: '← Back to Main',
        training_complete: 'Training Complete!',
        
        // Action buttons
        add_cards: 'Add Cards',
        cards: 'Cards',
        training: 'Training',
        delete: 'Delete',
        select: 'Select',
        back_to_main: '← Back to Main',
        
        // Deck statistics
        total: 'Total',
        repeat: 'Repeat',
        
        // Statistics
        stats_button: 'Statistics',
        statistics: 'Statistics',
        general_stats: 'General Statistics',
        total_decks: 'Total Decks',
        total_cards: 'Total Cards',
        learned_cards: 'Learned Cards',
        cards_for_repeat: 'Cards for Repeat',
        repeat_stats: 'Repeat Statistics',
        again_cards: 'Again',
        good_cards: 'Good',
        easy_cards: 'Easy',
        deck_distribution: 'Deck Distribution',
        daily_training: 'Daily Training',
        close: 'Close',
        
        // Messages
        error: 'Error',
        try_again: 'Try Again',
        card_deleted: 'Card deleted successfully!',
        delete_confirmation: 'Are you sure you want to delete this card?',
        training_interruption: 'Are you sure you want to interrupt the training?',
        enter_answer: 'Please enter an answer',
        
        // Errors and notifications
        card_delete_error: 'Error deleting card. Please try again.',
        audio_playback_error: 'Audio playback error',
        audio_generation_error: 'Audio generation error',
        deck_name_min_length: 'Deck name must contain at least 2 characters',
        select_both_languages: 'Please select both languages',
        languages_must_differ: 'Learning language and translation language must be different',
        deck_creation_error: 'Deck creation error:',
        deck_deletion_confirm: 'Are you sure you want to delete deck',
        deck_deletion_error: 'Deck deletion error:',
        fill_all_fields: 'Please fill in all fields',
        cards_saved: 'Saved {count} cards!',
        training_completed: 'Training completed! You studied {count} cards.',
        loading_cards: 'Loading cards...',
        loading_decks: 'Loading your decks...',
        saving_cards: 'Saving cards...',
        loading_training_cards: 'Loading cards for training...',
        loading_stats: 'Loading statistics...',
        stats_load_error: 'Error loading statistics',
        no_data: 'No data available',
        
        // Validation hints
        fill_this_field: 'Please fill out this field.',
        select_item_from_list: 'Please select an item in the list.',
        enter_valid_value: 'Please enter a valid value.',
         
          // Footer
        app_version: 'PhraseWeaver v0.1.0'
    }
};

// Текущий язык интерфейса (по умолчанию английский)
let currentLanguage = 'en';

// Проверяем сохраненный язык только если он есть в localStorage
const savedLanguage = localStorage.getItem('interface_language');
if (savedLanguage && translations[savedLanguage]) {
    currentLanguage = savedLanguage;
}

// Функция для получения перевода
function t(key, params = {}) {
    let translation = translations[currentLanguage][key] || translations['ru'][key] || key;
    
    // Заменяем параметры в строке
    Object.keys(params).forEach(param => {
        translation = translation.replace(`{${param}}`, params[param]);
    });
    
    return translation;
}

// Функция для смены языка
function setLanguage(language) {
    if (translations[language]) {
        currentLanguage = language;
        localStorage.setItem('interface_language', language);
        updateInterface();
    }
}

// Функция для получения текущего языка
function getCurrentLanguage() {
    return currentLanguage;
}

// Функция для обновления интерфейса
function updateInterface() {
    // Обновляем все элементы с атрибутом data-translate
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const translation = t(key);
        
        // Проверяем, нужно ли обновлять placeholder, title или textContent
        if ((element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email' || element.type === 'password')) || 
            element.tagName === 'TEXTAREA') {
            // Для полей ввода обновляем placeholder
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        } else if (element.hasAttribute('title')) {
            // Для элементов с title обновляем title
            element.title = translation;
        } else {
            // Для остальных элементов обновляем textContent
            element.textContent = translation;
        }
    });
    
    // Обновляем специальные элементы
    updateSpecialElements();
    
    // Обновляем сообщения валидации
    updateValidationMessages();
}

// Функция для обновления специальных элементов
function updateSpecialElements() {
    // Обновляем tooltip FAB кнопки
    const fabTooltip = document.querySelector('.fab .tooltip');
    if (fabTooltip) {
        fabTooltip.textContent = t('create_deck');
    }
    
    // Обновляем title FAB кнопки
    const fabButton = document.getElementById('add-deck-btn');
    if (fabButton) {
        fabButton.title = t('create_deck');
    }
    
    // Обновляем placeholder полей ввода
    const deckNameInput = document.getElementById('deck-name');
    if (deckNameInput) {
        deckNameInput.placeholder = t('deck_name_placeholder');
    }
    
    // Обновляем placeholder поля ответа в тренировке
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        const isReverse = answerInput.getAttribute('data-reverse') === 'true';
        answerInput.placeholder = isReverse ? t('enter_phrase') : t('enter_translation');
    }
    
    // Обновляем текст "Правильный ответ"
    const correctAnswerElements = document.querySelectorAll('.correct-answer');
    correctAnswerElements.forEach(element => {
        if (element.textContent.includes(':')) {
            const answerText = element.textContent.split(':')[1];
            element.textContent = t('correct_answer') + answerText;
        }
    });
    
    // Обновляем счетчики фраз
    updatePhrasesCounter();
}

// Функция для обновления счетчиков фраз
function updatePhrasesCounter() {
    const totalElement = document.getElementById('total-phrases-count');
    const selectedElement = document.getElementById('selected-phrases-count');
    const saveCountElement = document.getElementById('save-count');
    
    if (totalElement && selectedElement) {
        const totalCount = totalElement.textContent;
        const selectedCount = selectedElement.textContent;
        
        // Обновляем текст счетчика
        const counterContainer = document.querySelector('.phrases-counter');
        if (counterContainer) {
            counterContainer.innerHTML = `
                <span id="total-phrases-count">${totalCount}</span> ${t('phrases_count')} | 
                <span id="selected-phrases-count">${selectedCount}</span> ${t('selected')}
            `;
        }
    }
    
    if (saveCountElement) {
        const count = saveCountElement.textContent;
        const saveButton = document.getElementById('save-selected-btn');
        if (saveButton) {
            saveButton.innerHTML = `${t('save_selected')} (<span id="save-count">${count}</span>)`;
        }
    }
}

// Функция для обновления сообщений валидации
function updateValidationMessages() {
    // Обновляем сообщения для обязательных полей
    const requiredInputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    requiredInputs.forEach(input => {
        input.setCustomValidity('');
        input.addEventListener('invalid', function() {
            if (this.validity.valueMissing) {
                if (this.tagName === 'SELECT') {
                    this.setCustomValidity(t('select_item_from_list'));
                } else {
                    this.setCustomValidity(t('fill_this_field'));
                }
            } else {
                this.setCustomValidity(t('enter_valid_value'));
            }
        });
        
        input.addEventListener('input', function() {
            this.setCustomValidity('');
        });
    });
}

// Инициализация i18n при загрузке страницы
function initializeI18n() {
    // Обновляем интерфейс (currentLanguage уже установлен)
    updateInterface();
    
    // Устанавливаем правильный radio button в настройках
    const languageRadio = document.querySelector(`input[name="language"][value="${currentLanguage}"]`);
    if (languageRadio) {
        languageRadio.checked = true;
    }
}

// Экспортируем функции
export { t, setLanguage, getCurrentLanguage, updateInterface, initializeI18n };