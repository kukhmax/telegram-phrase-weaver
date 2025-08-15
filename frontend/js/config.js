const config = {
    // Теперь URL будет всегда относительным. 
    // Nginx сам разберется, куда отправить запрос: к статике или к бэкенду.
    API_BASE_URL: '/api' 
};


// const config = {
//     // В Render URL бэкенда будет другим, его нужно будет взять из настроек сервиса
//     API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
//         ? 'http://localhost:8000' // URL для локальной разработки
//         : 'https://telegram-phrase-weaver.onrender.com' // URL для продакшена на Render
// };