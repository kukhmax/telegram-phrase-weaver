// Главный файл, который управляет всем приложением
import { api, setAuthToken } from '/static/js/api.js';
import { DOMElements, showWindow, renderDecks, showLoading, showError } from '/static/js/ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.ready();

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
    document.getElementById('back-to-main-btn').addEventListener('click', () => {
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

    // Запускаем приложение
    main();
});