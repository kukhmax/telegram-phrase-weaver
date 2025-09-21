/**
 * Telegram Mini App - Cache Management Script
 * Управление кешем и обновление при перезагрузке
 */

class TelegramCacheManager {
    constructor() {
        this.tg = window.Telegram.WebApp;
        this.cacheVersion = '1.0.0';
        this.cacheKey = 'tg_miniapp_cache_v1';
        this.lastUpdateKey = 'tg_miniapp_last_update';
        this.isReloading = false;
        
        this.init();
    }

    /**
     * Инициализация приложения
     */
    init() {
        // Проверяем поддержку Telegram WebApp
        if (!this.tg) {
            this.showError('Telegram WebApp не поддерживается');
            return;
        }

        // Развертываем приложение на весь экран
        this.tg.expand();
        
        // Устанавливаем тему
        this.setupTheme();
        
        // Проверяем обновления кеша
        this.checkCacheUpdate();
        
        // Отображаем информацию о пользователе
        this.displayUserInfo();
        
        // Устанавливаем обработчики событий
        this.setupEventHandlers();
        
        // Обновляем статус
        this.updateStatus('Приложение инициализировано');
    }

    /**
     * Настройка темы в соответствии с настройками Telegram
     */
    setupTheme() {
        const theme = this.tg.themeParams;
        
        if (theme.bg_color) {
            document.documentElement.style.setProperty('--bg-color', theme.bg_color);
        }
        if (theme.text_color) {
            document.documentElement.style.setProperty('--text-color', theme.text_color);
        }
        
        // Сохраняем тему в локальное хранилище
        localStorage.setItem('tg_theme', JSON.stringify(theme));
    }

    /**
     * Проверка и обновление кеша
     */
    checkCacheUpdate() {
        const cachedVersion = localStorage.getItem('app_version');
        const lastUpdate = localStorage.getItem(this.lastUpdateKey);
        
        // Проверяем версию приложения
        if (cachedVersion !== this.cacheVersion) {
            this.showUpdateWarning();
            setTimeout(() => {
                this.forceUpdate();
            }, 2000);
            return;
        }
        
        // Обновляем информацию о кеше
        this.updateCacheInfo();
        
        // Проверяем последнее обновление
        if (lastUpdate) {
            const updateTime = new Date(parseInt(lastUpdate));
            document.getElementById('last-update').textContent = updateTime.toLocaleString('ru-RU');
        }
    }

    /**
     * Отображение информации о пользователе
     */
    displayUserInfo() {
        const user = this.tg.initDataUnsafe?.user;
        if (user) {
            document.getElementById('user-id').textContent = user.id || 'Неизвестно';
            document.getElementById('app-title').textContent = `Привет, ${user.first_name || 'пользователь'}!`;
        } else {
            document.getElementById('user-id').textContent = 'Демо-режим';
        }
    }

    /**
     * Установка обработчиков событий
     */
    setupEventHandlers() {
        // Обработчик события viewportChanged
        this.tg.onEvent('viewportChanged', () => {
            this.updateStatus('Размер экрана изменен');
        });

        // Обработчик события themeChanged
        this.tg.onEvent('themeChanged', () => {
            this.setupTheme();
            this.updateStatus('Тема изменена');
        });

        // Обработчик перед закрытием
        window.addEventListener('beforeunload', () => {
            this.saveCacheData();
        });

        // Обработчик видимости страницы
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isReloading) {
                this.checkCacheUpdate();
            }
        });
    }

    /**
     * Сохранение данных кеша
     */
    saveCacheData() {
        const cacheData = {
            version: this.cacheVersion,
            timestamp: Date.now(),
            theme: localStorage.getItem('tg_theme'),
            userId: this.tg.initDataUnsafe?.user?.id
        };
        
        localStorage.setItem(this.cacheKey, JSON.stringify(cacheData));
        localStorage.setItem(this.lastUpdateKey, Date.now().toString());
        localStorage.setItem('app_version', this.cacheVersion);
    }

    /**
     * Обновление информации о кеше
     */
    updateCacheInfo() {
        const cacheData = localStorage.getItem(this.cacheKey);
        if (cacheData) {
            try {
                const data = JSON.parse(cacheData);
                const updateTime = new Date(data.timestamp);
                document.getElementById('last-update').textContent = updateTime.toLocaleString('ru-RU');
            } catch (e) {
                console.error('Ошибка разбора кеша:', e);
            }
        }
    }

    /**
     * Показать предупреждение об обновлении
     */
    showUpdateWarning() {
        document.getElementById('update-warning').classList.remove('hidden');
        this.updateStatus('Обнаружено обновление...');
    }

    /**
     * Обновление статуса
     */
    updateStatus(message) {
        const statusElement = document.getElementById('status-text');
        const timestampElement = document.getElementById('status-timestamp');
        
        statusElement.textContent = message;
        timestampElement.textContent = new Date().toLocaleString('ru-RU');
        
        console.log(`[TelegramCacheManager] ${message}`);
    }

    /**
     * Показать ошибку
     */
    showError(message) {
        this.updateStatus(`Ошибка: ${message}`);
        alert(`Ошибка: ${message}`);
    }
}

/**
 * Глобальные функции для кнопок
 */

/**
 * Перезагрузка приложения с обновлением кеша
 */
function reloadApp() {
    if (window.cacheManager) {
        window.cacheManager.isReloading = true;
        window.cacheManager.saveCacheData();
        window.cacheManager.updateStatus('Перезагрузка приложения...');
    }
    
    // Очищаем кеш браузера для текущей страницы
    if ('caches' in window) {
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        }).then(() => {
            console.log('Браузерный кеш очищен');
        });
    }
    
    // Перезагружаем страницу с принудительным обновлением
    setTimeout(() => {
        window.location.reload(true);
    }, 1000);
}

/**
 * Очистка локального кеша
 */
function clearCache() {
    try {
        // Очищаем localStorage
        const keysToKeep = ['tg_theme'];
        const allKeys = Object.keys(localStorage);
        
        allKeys.forEach(key => {
            if (!keysToKeep.includes(key)) {
                localStorage.removeItem(key);
            }
        });
        
        // Очищаем sessionStorage
        sessionStorage.clear();
        
        // Очищаем куки
        document.cookie.split(";").forEach(function(c) {
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        
        if (window.cacheManager) {
            window.cacheManager.updateStatus('Кеш очищен');
        }
        
        alert('Кеш успешно очищен!');
        
    } catch (error) {
        console.error('Ошибка при очистке кеша:', error);
        alert('Ошибка при очистке кеша');
    }
}

/**
 * Принудительное обновление приложения
 */
function forceUpdate() {
    if (window.cacheManager) {
        window.cacheManager.isReloading = true;
        
        // Увеличиваем версию кеша
        const newVersion = '1.0.' + Date.now();
        window.cacheManager.cacheVersion = newVersion;
        
        // Показываем сообщение об успехе
        document.getElementById('update-success').classList.remove('hidden');
        document.getElementById('update-warning').classList.add('hidden');
        
        window.cacheManager.updateStatus('Принудительное обновление...');
        
        // Сохраняем данные и перезагружаем
        setTimeout(() => {
            window.cacheManager.saveCacheData();
            window.location.reload(true);
        }, 1500);
    }
}

/**
 * Инициализация при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    // Создаем экземпляр менеджера кеша
    window.cacheManager = new TelegramCacheManager();
    
    // Проверяем, является ли это перезагрузкой после обновления
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('updated') === 'true') {
        document.getElementById('update-success').classList.remove('hidden');
        setTimeout(() => {
            document.getElementById('update-success').classList.add('hidden');
        }, 3000);
    }
});

/**
 * Дополнительные утилиты для работы с кешем
 */

/**
 * Проверка поддержки Service Worker и кеша
 */
function checkCacheSupport() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(function(registration) {
            console.log('Service Worker готов');
            return registration.update();
        }).catch(function(error) {
            console.log('Service Worker не поддерживается:', error);
        });
    }
}

/**
 * Установка мета-тегов для предотвращения кеширования
 */
function setupNoCacheHeaders() {
    // Добавляем мета-теги для предотвращения кеширования
    const metaTags = [
        { name: 'cache-control', content: 'no-cache, no-store, must-revalidate' },
        { name: 'pragma', content: 'no-cache' },
        { name: 'expires', content: '0' }
    ];
    
    metaTags.forEach(tag => {
        const meta = document.createElement('meta');
        meta.httpEquiv = tag.name;
        meta.content = tag.content;
        document.head.appendChild(meta);
    });
}

// Вызываем при загрузке
setupNoCacheHeaders();