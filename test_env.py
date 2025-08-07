#!/usr/bin/env python3

import os
import sys
sys.path.append('./backend')

from backend.app.core.config import settings

print("=== Проверка переменных окружения ===")
print(f"GOOGLE_API_KEY из os.environ: {os.environ.get('GOOGLE_API_KEY', 'НЕ НАЙДЕН')}")
print(f"google_api_key из settings: {settings.google_api_key}")
print(f"Текущая рабочая директория: {os.getcwd()}")
print(f"Файл .env существует: {os.path.exists('.env')}")

if os.path.exists('.env'):
    print("\nСодержимое .env:")
    with open('.env', 'r') as f:
        content = f.read()
        print(content)
else:
    print("Файл .env не найден!")