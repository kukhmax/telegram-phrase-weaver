// Агрессивный скрипт для очистки кеша в Telegram WebApp
(function() {
    'use strict';
    
    // Генерируем уникальный timestamp для версии (обновляется каждые 5 минут)
    const version = Math.floor(Date.now() / (5 * 60 * 1000));
    
    console.log(`🔄 Cache Buster v${version} - Telegram WebApp`);
    
    // Функция для добавления версии к URL
    function addVersionToUrl(url) {
        if (!url || url.includes('?v=')) return url;
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}v=${version}&t=${Date.now()}`;
    }
    
    // Обновляем CSS файлы
    const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
    cssLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            const newHref = addVersionToUrl(href);
            if (newHref !== href) {
                console.log(`🎨 Updating CSS: ${href} -> ${newHref}`);
                link.setAttribute('href', newHref);
            }
        }
    });
    
    // Обновляем JS файлы
    const scriptTags = document.querySelectorAll('script[src]');
    scriptTags.forEach(script => {
        const src = script.getAttribute('src');
        if (src && (src.includes('/static/') || src.includes('/js/'))) {
            const newSrc = addVersionToUrl(src);
            if (newSrc !== src) {
                console.log(`📜 Updating JS: ${src} -> ${newSrc}`);
                script.setAttribute('src', newSrc);
            }
        }
    });
    
    // Очищаем различные типы кеша
    const lastVersion = localStorage.getItem('app_version');
    if (lastVersion !== version.toString()) {
        console.log('🧹 Clearing cache due to version change');
        
        // Сохраняем важные данные
        const authToken = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('user_data');
        const userSettings = localStorage.getItem('user_settings');
        
        // Очищаем все виды кеша
        try {
            localStorage.clear();
            sessionStorage.clear();
            
            // Очищаем кеш браузера если доступно
            if ('caches' in window) {
                caches.keys().then(names => {
                    names.forEach(name => {
                        console.log(`🗑️ Clearing cache: ${name}`);
                        caches.delete(name);
                    });
                });
            }
        } catch (e) {
            console.warn('⚠️ Cache clearing error:', e);
        }
        
        // Восстанавливаем важные данные
        if (authToken) localStorage.setItem('auth_token', authToken);
        if (userData) localStorage.setItem('user_data', userData);
        if (userSettings) localStorage.setItem('user_settings', userSettings);
        
        // Сохраняем новую версию
        localStorage.setItem('app_version', version.toString());
        localStorage.setItem('last_cache_clear', Date.now().toString());
    }
    
    // Принудительное обновление для Telegram
    if (window.Telegram && window.Telegram.WebApp) {
        console.log('📱 Telegram WebApp detected - applying aggressive cache busting');
        
        // Добавляем мета-теги для предотвращения кеширования
        const metaTags = [
            { name: 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
            { name: 'Pragma', content: 'no-cache' },
            { name: 'Expires', content: '0' }
        ];
        
        metaTags.forEach(tag => {
            let meta = document.querySelector(`meta[http-equiv="${tag.name}"]`);
            if (!meta) {
                meta = document.createElement('meta');
                meta.setAttribute('http-equiv', tag.name);
                document.head.appendChild(meta);
            }
            meta.setAttribute('content', tag.content);
        });
        
        // Принудительная перезагрузка стилей каждые 30 секунд в Telegram
        setInterval(() => {
            const currentTime = Date.now();
            document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                const href = link.getAttribute('href');
                if (href && href.includes('/static/')) {
                    const baseUrl = href.split('?')[0];
                    link.setAttribute('href', `${baseUrl}?v=${version}&refresh=${currentTime}`);
                }
            });
        }, 30000);
    }
    
    console.log(`✅ Cache buster initialized - Version: ${version}`);
})();