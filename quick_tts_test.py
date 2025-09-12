#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест TTS для диагностики проблем с произношением
"""

from gtts import gTTS
import tempfile
import os

def quick_polish_test():
    """Быстрый тест польского произношения"""
    
    text = "Uczę się portugalskiego"
    
    print(f"🔊 Тестирование польского TTS:")
    print(f"📝 Текст: '{text}'")
    
    # Тест 1: com TLD (должен работать)
    try:
        print(f"\n🌐 Тест 1: lang='pl', tld='com'")
        tts1 = gTTS(text=text, lang='pl', tld='com')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts1.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: pl TLD (может не работать)
    try:
        print(f"\n🌐 Тест 2: lang='pl', tld='pl'")
        tts2 = gTTS(text=text, lang='pl', tld='pl')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts2.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"🔍 Это объясняет проблему - pl TLD недоступен!")
    
    # Тест 3: Английский для сравнения
    try:
        print(f"\n🌐 Тест 3: lang='en', tld='com' (для сравнения)")
        tts3 = gTTS(text="I am learning Portuguese", lang='en', tld='com')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts3.save(f.name)
            print(f"✅ Успех! Файл: {f.name}")
            print(f"📏 Размер: {os.path.getsize(f.name)} байт")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    quick_polish_test()