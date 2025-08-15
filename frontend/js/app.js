// Главный файл, который управляет всем приложением
import { api, setAuthToken } from './api.js';
import { DOMElements, showWindow, renderDecks } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.ready();

    // ============================================
    //               ЛОГИКА ПРИЛОЖЕНИЯ
    // ============================================

    // Функция для обновления и перерисовки списка колод
    async function refreshDecks() {
        try {
            const decks = await api.getDecks();
            renderDecks(decks);
        } catch (error) {
            console.error("Failed to refresh decks:", error);
            // Можно показать ошибку пользователю
        }
    }

    // Главная функция инициализации
    async function main() {
        try {
            if (!tg.initData) {
                 throw new Error("Telegram.WebApp.initData is empty. Run in Telegram.");
            }
            // 1. Аутентификация
            const authData = await api.authenticate(tg.initData);
            setAuthToken(authData.access_token);
            
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
        
        const submitBtn = DOMElements.createDeckForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true; // Блокируем кнопку на время запроса
        submitBtn.textContent = 'Создание...';

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