// Простой скрипт для очистки кеша в Telegram WebApp
(function() {
    'use strict';
    
    // Генерируем уникальный timestamp для версии
    const version = Date.now();
    
    // Добавляем версию к CSS файлам
    const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
    cssLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.includes('?v=')) {
            link.setAttribute('href', `${href}?v=${version}`);
        }
    });
    
    // Добавляем версию к JS файлам
    const scriptTags = document.querySelectorAll('script[src]');
    scriptTags.forEach(script => {
        const src = script.getAttribute('src');
        if (src && !src.includes('?v=') && src.includes('/static/')) {
            script.setAttribute('src', `${src}?v=${version}`);
        }
    });
    
    // Очищаем localStorage если версия изменилась
    const lastVersion = localStorage.getItem('app_version');
    if (lastVersion !== version.toString()) {
        console.log('Clearing cache due to version change');
        // Сохраняем важные данные
        const authToken = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('user_data');
        
        // Очищаем кеш
        localStorage.clear();
        
        // Восстанавливаем важные данные
        if (authToken) localStorage.setItem('auth_token', authToken);
        if (userData) localStorage.setItem('user_data', userData);
        
        // Сохраняем новую версию
        localStorage.setItem('app_version', version.toString());
    }
    
    console.log(`App version: ${version}`);
})();