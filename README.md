### Поэтапный План Разработки Telegram Mini App "PhraseWeaver"

Этот план представляет собой детальный, последовательный roadmap для разработки приложения. Каждый этап включает аргументированные пояснения, почему именно такой подход выбран, какие инструменты используются, и как интегрировать предоставленные файлы (auth_service.py, ai_service.py, image_finder.py, enrichment.py). Я учту необходимость их подключения и возможных изменений для эффективности: например, адаптацию под FastAPI, асинхронность для производительности (учитывая нагрузку до 20 пользователей), и интеграцию с Redis для кэширования. Структура проекта будет модульной для удобства масштабирования.

Общая структура проекта:
- **Backend**: Python 3.12 + FastAPI (асинхронный фреймворк для API, идеален для реального времени и интеграций).
- **Frontend**: Vanilla JS + HTML/CSS (минималистично, без тяжёлых фреймворков как React, чтобы минимизировать размер Mini App и обеспечить быструю загрузку в Telegram).
- **DB**: PostgreSQL с SQLAlchemy ORM (надёжная реляционная БД для хранения пользователей, колод, карточек).
- **Кэширование**: Redis (для сессий, результатов AI, метаданных файлов).
- **Файлы**: Локальное хранение в /assets (как в предоставленных файлах), с CDN (например, Cloudinary free tier) для раздачи.
- **Интеграции**: Telegram WebApp API для auth и UI, Gemini AI (как в ai_service.py), Pexels (как в image_finder.py, но можно сменить на Unsplash для большего лимита), gTTS/Edge-TTS для аудио, deep_translator для переводов (как в enrichment.py).
- **Контейнеризация**: Docker + Compose для локальной разработки и развертывания на Render.
- **Изменения в файлах**: 
  - auth_service.py: Интегрировать как сервис в FastAPI, добавить Redis для хранения токенов.
  - ai_service.py: Сделать асинхронным, кэшировать результаты в Redis (чтобы избежать повторных запросов к Gemini).
  - image_finder.py: Добавить кэширование URL в Redis, сменить на Unsplash если Pexels лимит исчерпан (аргумент: Unsplash имеет больше бесплатных запросов).
  - enrichment.py: Центральный модуль; сделать полностью асинхронным, интегрировать с DB для хранения результатов, добавить Edge-TTS как fallback к gTTS (для лучшей поддержки языков).

#### Этап 1: Подготовка и Планирование (1-2 дня)
- **Действия**:
  - Создать репозиторий на GitHub (private для безопасности).
  - Установить окружение: Python 3.12, Node.js (для JS dev), Docker.
  - Определить структуру проекта:
    ```
    phraseweaver/
    ├── backend/
    │   ├── app/
    │   │   ├── core/          # config, settings, utils
    │   │   ├── models/        # SQLAlchemy модели (User, Deck, Card, etc.)
    │   │   ├── schemas/       # Pydantic схемы для API
    │   │   ├── services/      # auth_service.py, ai_service.py, image_finder.py, enrichment.py (адаптированные)
    │   │   ├── routers/       # FastAPI роуты (auth, decks, cards, training, notifications)
    │   │   ├── main.py        # Entry point FastAPI
    │   │   └── db.py          # DB сессии
    │   ├── assets/            # audio/, images/ (локальное хранение)
    │   ├── requirements.txt   # FastAPI, SQLAlchemy, psycopg2, redis, aiohttp, etc.
    │   └── Dockerfile
    ├── frontend/
    │   ├── js/                # main.js, utils.js (логика окон, API calls)
    │   ├── css/               # styles.css
    │   ├── html/              # index.html (основной шаблон Mini App)
    │   └── assets/            # локальные иконки, флаги
    ├── docker-compose.yml     # Postgres, Redis, Backend
    └── .env                   # Ключи: GOOGLE_API_KEY, PEXELS_API_KEY, TELEGRAM_BOT_TOKEN, etc.
    ```
  - Зарегистрировать API ключи: Telegram Bot, Gemini, Pexels/Unsplash, Google TTS.
- **Аргументация**: Это закладывает основу, предотвращая хаос. Модульная структура облегчает интеграцию файлов (например, services/ для ai_service.py). Docker с самого начала упрощает тестирование и развертывание на Render (бесплатный хостинг с поддержкой Docker).

#### Этап 2: Настройка Backend и API (3-5 дней)
- **Действия**:
  - Установить FastAPI: `pip install fastapi uvicorn sqlalchemy pydantic redis aiohttp gtts deep-translator pexels-api google-generativeai`.
  - Интегрировать предоставленные файлы в services/:
    - auth_service.py: Добавить в routers/auth.py роут /auth/telegram (POST: verify init_data, create token). Изменить: Добавить Redis для хранения сессий (ключ: user_id, value: token, TTL 24h) для rate limiting.
    - ai_service.py: Сделать часть enrichment.py; добавить кэширование в Redis (ключ: hash(phrase+keyword), value: JSON data, TTL 7 days) для повторных запросов.
    - image_finder.py: Интегрировать в enrichment.py; сменить на Unsplash (если нужно: pip install unsplash-py) для большего бесплатного лимита (5000 req/hour vs Pexels 200).
    - enrichment.py: Центральный сервис; вызвать в routers/cards.py. Изменения: Полностью асинхронный (asyncio.gather для AI, image, TTS, translate); хранить файлы в assets/, метаданные в DB/Redis.
  - Определить API роуты (routers/):
    - /auth: Telegram auth (исп. auth_service.py).
    - /decks: GET list, POST create (сохранить в DB: User -> Deck with name, desc, lang_from, lang_to).
    - /cards: POST enrich (ввод phrase+keyword -> вызов enrichment.py -> return enriched data); POST save (выбранные фразы -> DB Card: phrase, translation, audio_path, image_path, keyword, srs_data).
    - /training: GET due_cards (SRS filter: due_date < now); POST answer (update SRS: interval based on rating - again:1d, good:2d, easy:4d).
    - /notifications: POST schedule (Telegram Bot API sendMessage для reminders).
  - Реализовать SRS: В модели Card добавить поля (due_date, interval, ease_factor). Алгоритм: SuperMemo-like (interval *= ease_factor on good/easy).
- **Аргументация**: FastAPI идеален для async интеграций (AI/TTS). Интеграция файлов обеспечивает обогащение карточек (AI генерирует фразы, image finder - картинки, TTS - аудио). Кэширование в Redis снижает нагрузку на API (экономия на Gemini/Pexels). Нагрузка 20 пользователей - async справится без проблем.

#### Этап 3: Настройка Базы Данных (1-2 дня)
- **Действия**:
  - В db.py: SQLAlchemy setup с asyncpg для async.
  - Модели (models/):
    - User: telegram_id (PK), username, etc. (из auth_service.py).
    - Deck: id (PK), user_id (FK), name, desc, lang_from, lang_to, cards_count, due_count.
    - Card: id (PK), deck_id (FK), phrase, translation, keyword, audio_path, image_path, due_date, interval, ease_factor, examples (JSON для доп. фраз).
  - Миграции: Alembic для схем.
  - Docker Compose: services для postgres (port 5432), redis (6379).
- **Аргументация**: PostgreSQL надёжна для реляционных данных (пользователи -> колоды -> карточки). Asyncpg для производительности. SRS поля в Card позволяют фильтровать due_cards.

#### Этап 4: Настройка Frontend (JS) (4-6 дней)
- **Действия**:
  - Использовать Telegram WebApp API (window.Telegram.WebApp) для init, theme, buttons.
  - main.js: Логика навигации (show/hide divs для окон: main, create_deck, generate_cards, generated_phrases, cards_list, training).
    - Главное окно: Fetch /decks -> render list (с кнопками cards, train, delete). + button -> show create_deck.
    - Создание колоды: Selects для языков (как в описании), POST /decks.
    - Генерация карточек: Inputs phrase/keyword, button "Обогатить" -> POST /cards/enrich -> show generated_phrases window.
    - Сгенерированные фразы: Render cards с <b> tags, checkboxes "Выбрать", buttons delete. "Сохранить" -> POST /cards/save.
    - Карточки список: Fetch /cards?deck_id -> render with status (due/learned), delete button.
    - Тренировка: Fetch /training/due?deck_id -> show card (image, phrase/translation random direct/reverse), audio play (HTML5 audio), input check (color change), buttons again/good/easy -> POST /training/answer -> update progress bar.
    - Статистика/Настройки: Modals с fetch /stats (cards learned, etc.), settings (langs, notifications).
  - CSS: Responsive, Telegram theme vars (var(--tg-theme-bg-color)).
  - API calls: Fetch с Bearer token (из auth).
- **Аргументация**: Vanilla JS лёгкий для Mini App (Telegram ограничивает размер). Навигация divs/show-hide быстрее SPA. Интеграция с API backend обеспечивает данные (например, enrich -> AI+images+TTS).

## Описание дизайна окон

```
1. ГЛАВНОЕ ОКНО: 
header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками

mascot img
заголовок: "Мои колоды"
        если еще нет колод выводиться сообщение:
         "Здесь появятся ваши колоды"
        если уже есть колоды ,далее плашки с колодами со следующими данными:
        1. Название колоды
        2. Описание 
        3. язык изучения с флагом
        4. язык перевода с флагом
        5. а) Общее количество карточек б) количество карточек для повторения
        
        справа три кнопки: а) кнопка "карточки" , при нажатии на которую появляестя список карточек в всплывающем окне
                          б) кнопка "тренировки", при нажатии открывает окно с тернировками
                          в) кнопка "удалить" , удаляет колоду
       При нажатии на плашку с колодой открывается окно для генерации карточек
       
       внизу галвного окна кнопка с + , которая открывает окно для создания колоды


       
 2. ОКНО СОЗДАНИЯ КОЛОДЫ
 header и mascot  остается как на гланом окне:
 header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками
     при нажатии на PHRASE WEAVER возвращаемся на главное окно
     
   Заголовок: "Создать новую колоду"
	Название колоды:
	поле для вписывания названия колоды с hint: Введите название колоды
	
	Описание:
	поле для описания колодыс hint: Введите описание колоды
	
	Изучаемый язык:
	<select id="sourceLanguageSelect" name="source_language" required="">
                                <option value="">Выберите язык</option>
                                <option value="en">🇺🇸 English</option>
                                <option value="ru">🇷🇺 Русский</option>
                                <option value="fr">🇫🇷 Français</option>
                                <option value="de">🇩🇪 Deutsch</option>
                                <option value="es">🇪🇸 Español</option>
                                <option value="pl">🇵🇱 Polski</option>
                                <option value="pt">🇵🇹 Portuguese</option>
                            </select>
        Язык перевода:
        <select id="sourceLanguageSelect" name="source_language" required="">
                                <option value="">Выберите язык</option>
                                <option value="en">🇺🇸 English</option>
                                <option value="ru">🇷🇺 Русский</option>
                                <option value="fr">🇫🇷 Français</option>
                                <option value="de">🇩🇪 Deutsch</option>
                                <option value="es">🇪🇸 Español</option>
                                <option value="pl">🇵🇱 Polski</option>
                                <option value="pt">🇵🇹 Portuguese</option>
                            </select>
        Кнопка : "Создать колоду" , при нажатии на которую создается колода и перебрасывется на гланое окно, где эта колода показывается
        Кнопка возврата на главную страницу "<- Назад на главную"
       
  файлы с эксизами : ./PHRASE WEAVER(main window).png  и    ./PRASE WEAVER (1).png
       
3. ОКНО ГЕНЕРАЦИИ КАРТОЧЕК
 header и mascot  остается как на гланом окне:
 header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками
     при нажатии на PHRASE WEAVER возвращаемся на главное окно
     
   Заголовок: "Генерация карточек (<название колоды>)"
   <флаг  язык изучения ,указанный в колоде> - <флаг язык перевода , указанный в колоде>
   
   Фраза:
   Поле для фразы
   
   Ключевое слово:
   Поле для ключевого слова
   
   Кнопка "Обогатить", при нажатии отправляется запрос с промптом в ai gemini 
   (также генерируется аудио для фраз и через API Pexels получаем картинку по ключевому слову)
   
  ```
  # Файл: core/ai_generator.py 
  
import os
import google.generativeai as genai
import logging
import json
from typing import Optional

# Обновленный промпт с поддержкой исходной фразы
PROMPT_TEMPLATE = """
Your task is to help with language learning.
Given:
- Original phrase: "{phrase}" 
- Keyword to focus on: "{keyword}"
- Language: "{language}"
- Target language for translation: "{target_language}"

Please:
1. Create an English search query (1-2 words) for finding an image that best visually represents the keyword "{keyword}". Call this field "image_query".
2. Take the original phrase "{phrase}" and provide its accurate translation to {target_language}. In the original phrase, wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.
3. Generate 5 additional realistic example sentences using the keyword "{keyword}" in different grammatical forms (conjugations, declensions, etc.).
4. For each of the 5 additional examples, provide accurate translations to {target_language}.
5. In each of the 5 additional examples, find and wrap the keyword "{keyword}" (in any of its forms) with HTML tags <b> and </b>.

Return ONLY a valid JSON object without any other words or formatting.
Format example:
{{
  "image_query": "walking home sunset",
  "original_phrase": {{"original": "Eu estou <b>indo</b> para casa.", "translation": "Я иду домой."}},
  "additional_examples": [
    {{"original": "Eles <b>vão</b> para a praia.", "translation": "Они идут на пляж."}},
    {{"original": "Nós <b>fomos</b> ao cinema.", "translation": "Мы пошли в кино."}},
    {{"original": "Ela <b>vai</b> trabalhar.", "translation": "Она идет работать."}},
    {{"original": "Vocês <b>foram</b> embora.", "translation": "Вы ушли."}},
    {{"original": "Eu <b>irei</b> amanhã.", "translation": "Я пойду завтра."}}
  ]
}}
"""

async def generate_examples_with_ai(phrase: str, keyword: str, language: str, target_language: str) -> Optional[dict]:
    """
    Генерирует примеры фраз с помощью AI, включая исходную фразу и дополнительные примеры.
    """
    
    # Создаем и настраиваем модель ВНУТРИ функции для каждого асинхронного вызова
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except KeyError:
        logging.error("КРИТИЧЕСКАЯ ОШИБКА: Ключ GOOGLE_API_KEY не установлен!")
        return None
    except Exception as e:
        logging.error(f"Ошибка конфигурации Gemini API: {e}")
        return None
    
    if not model:
        return None

    prompt = PROMPT_TEMPLATE.format(
        phrase=phrase,
        keyword=keyword, 
        language=language, 
        target_language=target_language
    )
    logging.info(f"Отправка AI-запроса для фразы '{phrase}' с ключевым словом '{keyword}'...")

    try:
        response = await model.generate_content_async(prompt)
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        logging.info(f"AI успешно сгенерировал данные для '{phrase}'.")
        return data
    except Exception as e:
        logging.error(f"Ошибка при работе с AI: {e}")
        return None
  ```
   далее открывается окно со сгенерироваными фразами:
   
   5. ОКНО СО СГЕНЕРИРОВАННЫМИ ФРАЗАМИ
   
    header и mascot  остается как на гланом окне:
 header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками
     при нажатии на PHRASE WEAVER возвращаемся на главное окно
     
     Заголовок: "Фразы для тренировки"   <количество всех фраз> фраз |<количество выьраных фраз> выбрано
     
     Первая карточка
     --------------------------------
     <флаг изучаемого языка> Введенная фраза с выделенным ключевым словом
     например, 🇵🇹 Eu <storng>aprendo</strong> portuges
     <флаг языка перевода> Перевод с выделеннвм перевоодом ключевого слова
     например, 🇷🇺 Я <storng>изучаю</strong> португальский
     
     кнопка "Выбрать"    кнопка"Удалить"
     ---------------------------------------
     
     Вторая, третья , четвертая, пятая и шестая карточки
     ----------------------------------------
     <флаг изучаемого языка> фраза с выделенным ключевым словом 
     например, 🇵🇹 Eu <storng>aprendo</strong> portuges
     <флаг языка перевода> Перевод с выделеннвм перевоодом ключевого слова
     например, 🇷🇺 Я <storng>изучаю</strong> португальский
     
     кнопка "Выбрать"    кнопка"Удалить"
     --------------------------------------
     (кнопка "выбрать" отмечает карточку для добавления в колоду;
      кнопка "удалить" удаляет карточку из списка)
      
      кнопка "Сохранить выбранные <количество выбранных>" , после нажатия карточки сохраняются в базе и будут готовы к тренировке и отображатся в окне Карточки, при нажатии кнопки "карточки" в колоде на гланом окне
      
      кнопка "обогатить заново", которая возвращает на окно генерации фраз
      кнопка "<- Назад на главную", возвращает на главное окно
      
     
     6. ОКНО С КАРТОЧКАМИ
     
       header и mascot  остается как на гланом окне:
 header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками
     при нажатии на PHRASE WEAVER возвращаемся на главное окно
     
     заголовок "Карточки для изучения"
     
     кнопка "обогатить" (перключает на окно с генерацией карточек)
     
     список карточек в формате
      ----------------------------------------
     <флаг изучаемого языка> фраза с выделенным ключевым словом 
     например, 🇵🇹 Eu <storng>aprendo</strong> portuges
     <флаг языка перевода> Перевод с выделеннвм перевоодом ключевого слова
     например, 🇷🇺 Я <storng>изучаю</strong> португальский
     
     Статус "повторяем"( либо "изучено")
     
      кнопка"Удалить" (удаляет из списка и из базы)
     --------------------------------------
     
     кнопка "<- Назад на главную", возвращает на главное окно
     
     7. ОКНО ДЛЯ ТРЕНИРОВКИ
     
     header и mascot  остается как на гланом окне:
 header: кнопка "Статистика" PHRASE WEAVER "Настройки"
     при нажатии на "Статистика" ,открывается окно со статистикой
     при нажатии на "Настройки" , отскрывается окно с настройками
     при нажатии на PHRASE WEAVER возвращаемся на главное окно
     
     заголовок "Тренировка"
     
     ----------------------------------
     ПОЛОСА С ПРОГРЕССОМ ( УВЕЛИЧИВАЕТСЯ С КАЖДОЙ ПРОЙДЕННОЙ КАРТОЧКОЙ)
     ----------------------------------
     
     фото по ключевому слову
     
     фраза на языке изучения\ либо фраза перевода  [ кнопка для воспроизведения аудио фразы ]
     
     поле для ввода перевода \либо на языке изучения (если вводится правильно менят цвет фона на зеленый, если нет - на красный)
      под полем ввода: если вводиться не правильно: появляется правильный ответ 
      				кнопка "check" после нажатия меняет цвет фона поля , в зависимости от правильности  ответа
      				
      	кнопка "Снова"  кнопка "хорошо"  кнопка "легко"
      	
      	(при нажатии на "Снова" карточка добавляется к повторяемым в колоде и прибаляет +1 к счетчику карточек для повторения на колоде и ставиться в очередь на повторение в ближайшую тренировку;
      	при нажатии на "хорошо" карточка добавляется к повторяемым в колоде и прибаляет +1 к счетчику карточек для повторения на колоде и ставиться в очередь на повторение в тренировку в конец списка
      	при нажатии на "легко" карточка добавляется к изученным)
      	
      	кнопка "<- Назад на главную", возвращает на главное окно
```


#### Этап 5: Интеграции и Уведомления (2-3 дня)
- **Действия**:
  - Telegram: Bot для sendMessage (reminders: cron-like в backend с APScheduler).
  - AI/TTS/Images: Уже в enrichment.py; добавить fallbacks (Edge-TTS если gTTS fails).
  - Notifications: В backend scheduler: daily check due_cards -> send via Telegram API.
- **Аргументация**: APScheduler для уведомлений (бессерверный на Render). Fallbacks повышают надёжность (Gemini downtime -> skip).

#### Этап 6: Безопасность и Кэширование (1-2 дня)
- **Действия**:
  - Auth: Только Telegram initData (как в auth_service.py), rate limit (FastAPI middleware + Redis).
  - Encryption: AES для sensitive (но минимально, т.к. данные не критичны).
  - Validation: Pydantic schemas.
  - Redis: Как в изменениях файлов.
- **Аргументация**: Защищает от abuse (20 users max, но rate limit предотвращает спам). Кэш снижает costs на API.

#### Этап 7: Тестирование (2-3 дня)
- **Действия**:
  - Unit: Pytest для backend (auth, enrichment).
  - E2E: Manual в Telegram (create deck -> enrich -> train).
  - Load: Locust для 20 users.
- **Аргументация**: Обеспечивает стабильность перед deploy.

#### Этап 8: Развертывание (1 день)
- **Действия**:
  - Docker build, push to Render (free web service + DB).
  - Env vars на Render.
  - Telegram Bot: Set Mini App URL.
- **Аргументация**: Render бесплатен, auto-deploys from GitHub. Backup: Render snapshots для DB.

Общее время: 14-24 дня. Это реалистично для solo dev. Если нужно, добавьте milestones (e.g., MVP: auth + decks).