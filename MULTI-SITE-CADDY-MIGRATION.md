Миграция двух приложений за единый Caddy (80/443)

Цель: разместить два приложения на одном сервере за единым HTTPS reverse proxy (Caddy), разделяя трафик по доменам:
- `pw-new.club` и/или `pw.pw-new.club` → существующее приложение Telegram Phrase Weaver (TPW)
- `diary.pw-new.club` → приложение Speaking Diary

Итог: только Caddy публикует порты `80/443` на хосте, оба приложения работают в своих внутренних сетях без публичных портов. Caddy маршрутизирует по заголовку `Host`.

Подготовка и требования
- DNS:
  - `pw-new.club` → A-запись на IP сервера `161.97.108.249`
  - `pw.pw-new.club` → A/CNAME на `pw-new.club` или напрямую на `161.97.108.249`
  - `diary.pw-new.club` → A-запись на `161.97.108.249`
- Фаервол: откройте `22/tcp`, `80/tcp`, `443/tcp` (например, `ufw allow 22,80,443/tcp`)
- Сервер: установлен Docker Engine и Docker Compose plugin, Git

Сетевой план
- Создаём внешнюю Docker-сеть для проксирования: `web`
- Контейнер `caddy` из Speaking Diary будет подключён к `web` и к своей внутренней сети `diary_network`
- Контейнер фронтенда TPW будет подключён к `web`, НЕ публикуя порты `80/443`
- Caddy будет проксировать:
  - `diary.pw-new.club` → `frontend:80` (Speaking Diary), `/api*` → `backend:5000`
  - `pw-new.club`, `pw.pw-new.club` → `weaver:80` (TPW, alias в сети `web`)

Шаг 1. Создать внешнюю сеть `web`
```bash
docker network create web || true
docker network ls | grep web
```

Шаг 2. Обновить Speaking Diary (Caddy подключить к `web`)
- В `docker_compose.prod.yml` (этот репозиторий) добавьте внешнюю сеть `web` и подключите к ней `caddy` (пример):
```yaml
services:
  caddy:
    image: caddy:2.7
    container_name: diary_caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - frontend
      - backend
    networks:
      - default
      - web

networks:
  default:
    name: diary_network
  web:
    external: true
    name: web
```
- Пересоберите и поднимите прод-стек Speaking Diary после настроек: `docker compose -f docker_compose_prod.yml up -d --build`

Шаг 3. Расширить Caddyfile для двух сайтов
- Пример конфигурации Caddy (этот репозиторий):
```caddyfile
diary.pw-new.club {
    encode gzip
    log {
        output stdout
        format json
    }
    handle /api* {
        reverse_proxy backend:5000
    }
    handle {
        reverse_proxy frontend:80
    }
}

# TPW — обслуживаем по двум доменам (можно оставить один или сделать редирект)
pw-new.club, pw.pw-new.club {
    encode gzip
    log {
        output stdout
        format json
    }
    # Контейнер TPW должен быть доступен в сети `web` под alias `weaver`
    reverse_proxy weaver:80
}
```
- Опционально: чтобы принудительно канонизировать один домен TPW (например, на `pw.pw-new.club`), можно использовать редирект:
```caddyfile
pw-new.club {
    redir https://pw.pw-new.club{uri}
}

pw.pw-new.club {
    encode gzip
    reverse_proxy weaver:80
}
```

Шаг 4. Обновить Telegram Phrase Weaver (TPW)
- В его `docker-compose.yml` (в проекте TPW):
  - Удалите публикацию портов `80:80` и `443:443` у фронтенда
  - Добавьте `expose: ["80"]` и подключение к сети `web`
  - Задайте удобное имя сервиса/контейнера или добавьте alias в сети `web` — `weaver`
- Пример фрагмента для фронтенда TPW:
```yaml
services:
  frontend:
    image: nginx:alpine
    container_name: tpw_frontend
    restart: always
    # ports:    # УДАЛИТЬ
    #   - "80:80"
    #   - "443:443"
    expose:
      - "80"
    networks:
      - web

networks:
  web:
    external: true
    name: web
```
- Если сейчас нет возможности править compose TPW, временный вариант (даунтайм 1–2 минуты):
  1) Подключить текущий контейнер TPW к сети `web` с alias:
  ```bash
  docker network connect web telegram-phrase-weaver_frontend_1 --alias weaver
  ```
  2) Остановить контейнер, чтобы освободить `80/443` на хосте:
  ```bash
  docker stop telegram-phrase-weaver_frontend_1
  ```
  3) После запуска Caddy — вернуть TPW уже без публикации портов (пересобрать compose TPW, как описано выше).

Шаг 5. Переключить `80/443` на Caddy (минимальный даунтайм)
```bash
# 1) Остановить фронтенд TPW, который держит 80/443
docker stop telegram-phrase-weaver_frontend_1

# 2) Поднять Caddy со Speaking Diary
cd /opt/speaking_diary
docker compose -f docker_compose_prod.yml up -d caddy

# 3) Проверить, что Caddy слушает порты и выдал TLS
docker compose logs -n 200 caddy
ss -tulpn | grep -E ":80|:443"

# 4) Вернуть TPW за Caddy (без публикации портов)
# Пересоберите/поднимите TPW c networks: [web], expose: ["80"]
```

Проверка
- Speaking Diary:
  - `curl -I https://diary.pw-new.club`
  - `docker compose -f docker_compose_prod.yml exec backend curl -s http://localhost:5000/api/health`
- TPW:
  - `curl -I https://pw-new.club`
  - `curl -I https://pw.pw-new.club` (если настроен)
- Логи и состояние:
  - `docker compose -f docker_compose_prod.yml ps`
  - `docker compose -f docker_compose_prod.yml logs -n 200 caddy backend frontend`
  - `docker logs tpw_frontend` (или действительное имя контейнера TPW)

Диагностика
- Убедитесь, что только Caddy публикует `80/443`: `ss -tulpn | grep -E ":80|:443"`
- Если сертификат не выдаётся: проверьте A‑записи, доступность портов, блокировки фаервола, логи Caddy
- Если Caddy не может достучаться до TPW: проверьте, что TPW в сети `web` и доступен по alias `weaver`

Откат (Rollback)
- Вернуть прежний TPW, публикующий `80/443`:
```bash
docker compose -f docker_compose_prod.yml down caddy
docker start telegram-phrase-weaver_frontend_1
```
- Или восстановить публикацию портов в compose TPW и выполнить `docker compose up -d`

Замечания по безопасности и эксплуатации
- Секреты (`DB_PASSWORD`, `SECRET_KEY`, `GROQ_API_KEY`) храните в `.env` на сервере; генерацию смотрите в `SECRETS-GENERATION.md`
- Порт БД не публикуйте наружу; доступ к БД только из приложений в одной сети Docker
- Для TPW и Speaking Diary рекомендуются отдельные внутренние сети; Caddy подключается к обеим (внутренняя + `web`)
- Логи Caddy в JSON — удобно для централизованного сбора; при необходимости можно направить в файл/стек логирования

Что нужно изменить в этом репозитории (Speaking Diary)
- `docker_compose_prod.yml`: добавить сеть `web` и подключить к ней `caddy`
- `Caddyfile`: добавить блоки для `pw-new.club` и/или `pw.pw-new.club` с `reverse_proxy weaver:80`
- После изменений: `docker compose -f docker_compose_prod.yml up -d --build`

Что нужно изменить в репозитории TPW
- Удалить публикацию портов `80/443` у фронтенда
- Добавить `expose: 80` и `networks: [web]`
- Обеспечить доступность по alias `weaver` в сети `web`
- Пересобрать и поднять: `docker compose up -d --build`

Готовность к запуску
- После выполнения шагов:
  - `pw-new.club` и/или `pw.pw-new.club` обслуживаются через Caddy → TPW
  - `diary.pw-new.club` обслуживается через Caddy → Speaking Diary
  - Авто‑TLS от Let's Encrypt активен для всех доменов