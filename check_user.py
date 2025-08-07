#!/usr/bin/env python3
import sys
import os
sys.path.append('./backend')

# Меняем рабочую директорию на backend, чтобы использовать правильную базу данных
os.chdir('./backend')

from backend.app.core.database import SessionLocal
from backend.app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        # Проверяем, есть ли пользователь с ID=1
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"Пользователь найден: ID={user.id}, telegram_id={user.telegram_id}, username={user.username}")
        else:
            print("Пользователь с ID=1 не найден")
            
        # Создаем тестового пользователя, если его нет
        if not user:
            test_user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Создан тестовый пользователь: ID={test_user.id}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()