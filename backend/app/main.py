from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
import hmac, hashlib
from urllib.parse import parse_qsl, quote
import jwt
import redis
from sqlalchemy import Column, Integer, String, create_engine, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .auth import router as auth_router


app = FastAPI(title="PhraseWeaver API", version="1.0.0")

# CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# Статические файлы (фронтенд)
if os.path.exists("../frontend/public"):
    app.mount("/static", StaticFiles(directory="../frontend/public"), name="static")

# === CONFIG ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TEST_BOT_TOKEN")
JWT_SECRET = os.getenv("SECRET_KEY", "change_me_in_env")
JWT_ALGORITHM = "HS256"
DEBUG_MODE = os.getenv("ENVIRONMENT", "development") == "development"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/phraseweaver"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# === REDIS CONNECTION ===
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# === DB SETUP ===
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Deck(Base):
    __tablename__ = "decks"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# === APP SETUP ===
app = FastAPI(title="Phrase Weaver - Backend")

origins = os.getenv("CORS_ORIGINS", "*")
if origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === TELEGRAM INIT_DATA VERIFICATION ===
def verify_telegram_init(init_data: str, max_age_seconds: int = 86400):
    """Verify and parse Telegram WebApp initData."""
    items = dict(parse_qsl(init_data, keep_blank_values=True))
    if 'hash' not in items:
        raise ValueError("missing hash in init_data")
    received_hash = items.pop("hash")

    data_check_list = []
    for k in sorted(items.keys()):
        data_check_list.append(f"{k}={items[k]}")
    data_check_string = "\n".join(data_check_list)

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hmac = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hmac, received_hash):
        raise ValueError("invalid hash")

    auth_date = int(items.get("auth_date", "0"))
    now = int(datetime.utcnow().timestamp())
    if abs(now - auth_date) > max_age_seconds:
        raise ValueError("init_data expired")

    return items

# === JWT HELPERS ===
def create_jwt(payload: dict, expires_minutes: int = 60*24*7):
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire.isoformat()})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # store in Redis (session)
    session_key = f"session:{payload['telegram_id']}"
    redis_client.set(session_key, token, ex=expires_minutes*60)
    return token

def verify_jwt(token: str):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # check session in Redis
        session_key = f"session:{data['telegram_id']}"
        stored_token = redis_client.get(session_key)
        if stored_token != token:
            return None
        return data
    except jwt.PyJWTError:
        return None

# === SCHEMAS ===
class VerifyIn(BaseModel):
    init_data: str

class AuthResp(BaseModel):
    token: str
    user: dict

class DeckCreate(BaseModel):
    title: str
    description: Optional[str] = None

class DeckOut(BaseModel):
    id: int
    owner_id: int
    title: str
    description: Optional[str]

# === DEPENDENCIES ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth: str = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")
    token = auth.split(" ", 1)[1]
    data = verify_jwt(token)
    if not data or "telegram_id" not in data:
        raise HTTPException(status_code=401, detail="Invalid token or expired session")
    telegram_id = int(data["telegram_id"])
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# === ROUTES ===
@app.get("/")
async def root():
    return {"message": "PhraseWeaver API работает!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PhraseWeaver"}

@app.post("/api/auth/telegram/verify", response_model=AuthResp)
def auth_verify(payload: VerifyIn, db: Session = Depends(get_db)):
    # Check if init_data already verified and cached
    cache_key = f"initdata:{hashlib.sha256(payload.init_data.encode()).hexdigest()}"
    cached_user = redis_client.hgetall(cache_key)
    if cached_user:
        token = create_jwt({"telegram_id": int(cached_user["telegram_id"]), "user_db_id": int(cached_user["user_db_id"])})
        return {"token": token, "user": cached_user}

    try:
        items = verify_telegram_init(payload.init_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    telegram_id = None
    if "user" in items:
        import json
        try:
            user_json = json.loads(items["user"])
            telegram_id = int(user_json.get("id"))
            first_name = user_json.get("first_name")
            last_name = user_json.get("last_name")
            username = user_json.get("username")
        except Exception:
            telegram_id = None

    if telegram_id is None:
        for key in ("id", "user_id", "user.id"):
            if key in items:
                try:
                    telegram_id = int(items[key])
                    break
                except:
                    pass

    first_name = items.get("first_name") or items.get("user_first_name")
    last_name = items.get("last_name") or items.get("user_last_name")
    username = items.get("username") or items.get("user_username")

    if telegram_id is None:
        raise HTTPException(status_code=400, detail="telegram id not found in init_data")

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, first_name=first_name, last_name=last_name, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_jwt({"telegram_id": telegram_id, "user_db_id": user.id})
    user_data = {
        "telegram_id": str(telegram_id),
        "user_db_id": str(user.id),
        "first_name": first_name or "",
        "last_name": last_name or "",
        "username": username or ""
    }
    redis_client.hset(cache_key, mapping=user_data)
    redis_client.expire(cache_key, 86400)  # 1 день
    return {"token": token, "user": user_data}

@app.post("/api/decks", response_model=DeckOut)
def create_deck(d: DeckCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deck = Deck(owner_id=current_user.telegram_id, title=d.title, description=d.description)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return DeckOut(id=deck.id, owner_id=deck.owner_id, title=deck.title, description=deck.description)

@app.get("/api/decks", response_model=List[DeckOut])
def list_decks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decks = db.query(Deck).filter(Deck.owner_id == current_user.telegram_id).all()
    return [DeckOut(id=deck.id, owner_id=deck.owner_id, title=deck.title, description=deck.description) for deck in decks]

@app.delete("/api/decks/{deck_id}")
def delete_deck(deck_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.owner_id == current_user.telegram_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    db.delete(deck)
    db.commit()
    return {"ok": True}

@app.post("/api/debug/generate_init")
def debug_generate_init(payload: dict):
    if not DEBUG_MODE:
        raise HTTPException(status_code=403, detail="debug disabled")
    telegram_id = int(payload.get("telegram_id", 123456))
    first_name = payload.get("first_name", "DevUser")
    username = payload.get("username", "devuser")
    auth_date = int(datetime.utcnow().timestamp())
    params = {
        "id": str(telegram_id),
        "first_name": first_name,
        "username": username,
        "auth_date": str(auth_date)
    }
    items = sorted(params.items())
    data_check_string = "\n".join(f"{k}={v}" for k,v in items)
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hmac = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = computed_hmac
    qs = "&".join(f"{quote(k)}={quote(v)}" for k,v in params.items())
    return {"init_data": qs}

@app.get("/health")
def health():
    return {"status": "ok"}
