import ssl
from urllib.parse import urlparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine

def create_async_engine_with_ssl_context(db_url: str):
    """
    Создает асинхронный движок SQLAlchemy, корректно обрабатывая
    параметры SSL из URL для asyncpg.
    """
    parsed_url = urlparse(db_url)
    query_params = parse_qs(parsed_url.query)

    connect_args = {}
    
    # Fly.io требует SSL, поэтому мы создаем SSL-контекст.
    # Это решает проблему `unexpected keyword argument 'sslmode'`.
    if 'sslmode' in query_params and query_params['sslmode'][0] != 'disable':
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx

    # Создаем URL без query-параметров, так как мы их обработали
    clean_url = parsed_url._replace(query=None).geturl()

    return create_async_engine(
        clean_url,
        connect_args=connect_args,
        echo=True
    )