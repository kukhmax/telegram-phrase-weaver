#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования TTS (Text-to-Speech) с различными языками
Использует gTTS для генерации аудио файлов с правильным произношением
"""

import os
import sys
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import subprocess
from pathlib import Path

def get_available_languages():
    """Получить список доступных языков в gTTS"""
    try:
        langs = tts_langs()
        return langs
    except Exception as e:
        print(f"Ошибка получения языков: {e}")
        return {}

def test_tts_pronunciation(text, lang_code, tld='com', play_audio=False):
    """
    Тестирование произношения текста на указанном языке
    
    Args:
        text (str): Текст для озвучивания
        lang_code (str): Код языка (например, 'pl', 'pt', 'en')
        tld (str): Top-level domain для Google Translate ('com', 'pl', 'pt', etc.)
        play_audio (bool): Воспроизвести аудио после генерации
    
    Returns:
        str: Путь к созданному аудио файлу или None при ошибке
    """
    
    print(f"\n🔊 Тестирование TTS:")
    print(f"   📝 Текст: '{text}'")
    print(f"   🌍 Язык: {lang_code}")
    print(f"   🌐 TLD: {tld}")
    
    try:
        # Проверяем поддержку языка
        available_langs = get_available_languages()
        if lang_code not in available_langs:
            print(f"   ❌ Язык '{lang_code}' не поддерживается gTTS")
            print(f"   📋 Доступные языки: {list(available_langs.keys())[:10]}...")
            return None
        
        print(f"   ✅ Язык поддерживается: {available_langs[lang_code]}")
        
        # Создаем временный файл
        output_dir = Path("./audio_test")
        output_dir.mkdir(exist_ok=True)
        
        filename = f"test_{lang_code}_{tld}.mp3"
        output_path = output_dir / filename
        
        print(f"   🎯 Создание TTS объекта...")
        
        # Создаем TTS объект
        tts = gTTS(
            text=text,
            lang=lang_code,
            tld=tld,
            slow=False
        )
        
        print(f"   💾 Сохранение в файл: {output_path}")
        
        # Сохраняем аудио
        tts.save(str(output_path))
        
        print(f"   ✅ Аудио успешно создано!")
        print(f"   📁 Файл: {output_path}")
        print(f"   📏 Размер: {output_path.stat().st_size} байт")
        
        # Воспроизведение (опционально)
        if play_audio and sys.platform == "darwin":  # macOS
            print(f"   🔊 Воспроизведение...")
            subprocess.run(["afplay", str(output_path)])
        elif play_audio and sys.platform == "linux":
            print(f"   🔊 Воспроизведение...")
            subprocess.run(["aplay", str(output_path)])
        
        return str(output_path)
        
    except Exception as e:
        print(f"   ❌ Ошибка TTS: {e}")
        return None

def test_multiple_languages():
    """Тестирование нескольких языков с одним текстом"""
    
    test_cases = [
        # Польский
        {
            'text': 'Uczę się portugalskiego.',
            'lang': 'pl',
            'tld': 'com',
            'description': 'Польский с com TLD'
        },
        {
            'text': 'Uczę się portugalskiego.',
            'lang': 'pl', 
            'tld': 'pl',
            'description': 'Польский с pl TLD (может не работать)'
        },
        
        # Португальский
        {
            'text': 'Eu aprendo português.',
            'lang': 'pt',
            'tld': 'com',
            'description': 'Португальский с com TLD'
        },
        {
            'text': 'Eu aprendo português.',
            'lang': 'pt',
            'tld': 'pt',
            'description': 'Португальский с pt TLD'
        },
        
        # Русский
        {
            'text': 'Я изучаю португальский.',
            'lang': 'ru',
            'tld': 'com',
            'description': 'Русский с com TLD'
        },
        
        # Английский для сравнения
        {
            'text': 'I am learning Portuguese.',
            'lang': 'en',
            'tld': 'com',
            'description': 'Английский с com TLD'
        }
    ]
    
    print("🎯 Запуск тестирования множественных языков...\n")
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Тест {i}/{len(test_cases)}: {test_case['description']}")
        print(f"{'='*60}")
        
        result = test_tts_pronunciation(
            text=test_case['text'],
            lang_code=test_case['lang'],
            tld=test_case['tld']
        )
        
        results.append({
            'test': test_case['description'],
            'success': result is not None,
            'file': result
        })
    
    # Сводка результатов
    print(f"\n{'='*60}")
    print("📊 СВОДКА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅ Успех" if result['success'] else "❌ Ошибка"
        print(f"{status}: {result['test']}")
        if result['file']:
            print(f"         Файл: {result['file']}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n🎯 Успешно: {success_count}/{len(results)}")
    
    return results

def interactive_test():
    """Интерактивное тестирование TTS"""
    
    print("🎤 Интерактивное тестирование TTS")
    print("Введите 'quit' для выхода\n")
    
    while True:
        try:
            text = input("📝 Введите текст для озвучивания: ").strip()
            if text.lower() == 'quit':
                break
                
            lang_code = input("🌍 Введите код языка (pl, pt, ru, en, etc.): ").strip().lower()
            if not lang_code:
                lang_code = 'en'
                
            tld = input("🌐 Введите TLD (com, pl, pt, ru, etc.) [по умолчанию: com]: ").strip().lower()
            if not tld:
                tld = 'com'
                
            play = input("🔊 Воспроизвести аудио? (y/n) [по умолчанию: n]: ").strip().lower()
            play_audio = play in ['y', 'yes', 'да']
            
            test_tts_pronunciation(text, lang_code, tld, play_audio)
            
        except KeyboardInterrupt:
            print("\n👋 Выход...")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    
    print("🎵 TTS Тестер для PhraseWeaver")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Выберите режим:")
        print("1. Автоматическое тестирование (auto)")
        print("2. Интерактивный режим (interactive)")
        print("3. Быстрый тест польского (polish)")
        
        choice = input("\nВведите номер или название режима: ").strip()
        
        if choice in ['1', 'auto']:
            mode = 'auto'
        elif choice in ['2', 'interactive']:
            mode = 'interactive'
        elif choice in ['3', 'polish']:
            mode = 'polish'
        else:
            mode = 'auto'
    
    if mode == 'auto':
        test_multiple_languages()
    elif mode == 'interactive':
        interactive_test()
    elif mode == 'polish':
        # Быстрый тест польского языка
        print("🇵🇱 Быстрый тест польского языка...")
        test_tts_pronunciation(
            text="Uczę się portugalskiego. Ona uczy się szybko.",
            lang_code="pl",
            tld="com",
            play_audio=True
        )
    else:
        print(f"❌ Неизвестный режим: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()