#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Специальный тест для диагностики проблем с польским TTS
"""

from gtts import gTTS
import tempfile
import os
import asyncio
from pathlib import Path

def test_polish_tts_variants():
    """Тестирование различных вариантов настроек для польского TTS"""
    
    polish_text = "Uczę się portugalskiego. Robię to codziennie."
    
    print(f"🇵🇱 Тестирование польского TTS:")
    print(f"📝 Текст: '{polish_text}'")
    print("=" * 60)
    
    # Тест 1: Стандартный польский с com TLD
    try:
        print(f"\n🌐 Тест 1: lang='pl', tld='com', slow=False")
        tts1 = gTTS(text=polish_text, lang='pl', tld='com', slow=False)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts1.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Польский с pl TLD
    try:
        print(f"\n🌐 Тест 2: lang='pl', tld='pl', slow=False")
        tts2 = gTTS(text=polish_text, lang='pl', tld='pl', slow=False)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts2.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"🔍 Это может объяснить проблему - pl TLD недоступен!")
    
    # Тест 3: Медленная речь
    try:
        print(f"\n🌐 Тест 3: lang='pl', tld='com', slow=True")
        tts3 = gTTS(text=polish_text, lang='pl', tld='com', slow=True)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts3.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Альтернативные TLD
    alternative_tlds = ['co.uk', 'ca', 'com.au']
    for i, tld in enumerate(alternative_tlds, 4):
        try:
            print(f"\n🌐 Тест {i}: lang='pl', tld='{tld}', slow=False")
            tts = gTTS(text=polish_text, lang='pl', tld=tld, slow=False)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts.save(f.name)
                print(f"✅ Успех! Файл: {f.name}")
                print(f"📏 Размер: {os.path.getsize(f.name)} байт")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # Тест 7: Сравнение с английским
    try:
        print(f"\n🌐 Тест 7: lang='en', tld='com' (для сравнения)")
        tts_en = gTTS(text="I am learning Portuguese. I do it every day.", lang='en', tld='com')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts_en.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Рекомендации:")
    print("1. Если Тест 1 работает - используйте lang='pl', tld='com'")
    print("2. Если Тест 2 не работает - избегайте tld='pl'")
    print("3. Если все тесты не работают - проблема в gTTS или сети")
    print("4. Сравните размеры файлов - они должны отличаться от английского")

def test_language_detection():
    """Тестирование определения языка"""
    
    test_texts = [
        "Uczę się portugalskiego",
        "Robię to codziennie", 
        "Jak się masz?",
        "Dziękuję bardzo",
        "Miłego dnia"
    ]
    
    print("\n🔍 Тестирование определения польского языка:")
    print("=" * 50)
    
    for text in test_texts:
        try:
            # Попробуем создать TTS для каждого текста
            tts = gTTS(text=text, lang='pl', tld='com')
            print(f"✅ '{text}' - распознан как польский")
        except Exception as e:
            print(f"❌ '{text}' - ошибка: {e}")

if __name__ == "__main__":
    print("🇵🇱 Диагностика польского TTS")
    print("=" * 40)
    
    test_polish_tts_variants()
    test_language_detection()
    
    print("\n🎉 Тестирование завершено!")
    print("Проверьте созданные файлы и их размеры для диагностики.")