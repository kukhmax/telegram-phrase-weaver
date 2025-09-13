#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки различий между польским и английским произношением в gTTS
"""

from gtts import gTTS
import tempfile
import os
import hashlib

def test_polish_vs_english_accent():
    """Сравнение польского и английского произношения одного и того же текста"""
    
    # Тестовые фразы
    test_cases = [
        {
            'polish': 'Uczę się portugalskiego',
            'english': 'I am learning Portuguese',
            'description': 'Обучение португальскому'
        },
        {
            'polish': 'Robię to codziennie', 
            'english': 'I do it every day',
            'description': 'Ежедневная деятельность'
        },
        {
            'polish': 'Jak się masz',
            'english': 'How are you',
            'description': 'Приветствие'
        }
    ]
    
    print("🔍 Тестирование различий польского и английского произношения")
    print("=" * 70)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {case['description']}")
        print(f"🇵🇱 Польский: '{case['polish']}'")
        print(f"🇺🇸 Английский: '{case['english']}'")
        print("-" * 50)
        
        # Тест польского произношения
        try:
            print("🇵🇱 Генерация польского аудио...")
            tts_pl = gTTS(text=case['polish'], lang='pl', tld='com')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts_pl.save(f.name)
                pl_size = os.path.getsize(f.name)
                pl_file = f.name
                print(f"   ✅ Файл: {pl_file}")
                print(f"   📏 Размер: {pl_size} байт")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
            
        # Тест английского произношения
        try:
            print("🇺🇸 Генерация английского аудио...")
            tts_en = gTTS(text=case['english'], lang='en', tld='com')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts_en.save(f.name)
                en_size = os.path.getsize(f.name)
                en_file = f.name
                print(f"   ✅ Файл: {en_file}")
                print(f"   📏 Размер: {en_size} байт")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
            
        # Сравнение
        print("📊 Сравнение:")
        if pl_size != en_size:
            print(f"   ✅ Размеры различаются: {pl_size} vs {en_size} байт")
            print(f"   🎯 Это указывает на разное произношение")
        else:
            print(f"   ⚠️ Размеры одинаковые: {pl_size} байт")
            print(f"   🤔 Возможно, используется одинаковое произношение")
            
        # Тест с польским текстом, но английским языком (для сравнения)
        try:
            print("🧪 Тест: польский текст с английским языком...")
            tts_pl_as_en = gTTS(text=case['polish'], lang='en', tld='com')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts_pl_as_en.save(f.name)
                pl_as_en_size = os.path.getsize(f.name)
                print(f"   📏 Размер: {pl_as_en_size} байт")
                
                if pl_as_en_size == pl_size:
                    print(f"   ⚠️ ПРОБЛЕМА: Польский текст с lang='pl' и lang='en' дает одинаковый размер!")
                    print(f"   🔍 Это может означать, что gTTS не различает языки для этого текста")
                else:
                    print(f"   ✅ Размеры различаются, языки обрабатываются по-разному")
                    
        except Exception as e:
            print(f"   ❌ Ошибка теста: {e}")

def test_polish_specific_sounds():
    """Тест специфических польских звуков"""
    
    print("\n\n🇵🇱 Тестирование специфических польских звуков")
    print("=" * 60)
    
    # Слова с характерными польскими звуками
    polish_words = [
        'ą',      # носовое a
        'ę',      # носовое e  
        'ć',      # мягкое c
        'ń',      # мягкое n
        'ś',      # мягкое s
        'ź',      # мягкое z
        'ż',      # твердое zh
        'ł',      # w-подобное l
        'szcz',   # сложный звук
        'chrząszcz', # очень сложное слово
        'źdźbło',    # комбинация мягких звуков
        'węże',      # носовые звуки
    ]
    
    for word in polish_words:
        try:
            print(f"\n🔤 Тестирование: '{word}'")
            
            # Польское произношение
            tts_pl = gTTS(text=word, lang='pl', tld='com')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts_pl.save(f.name)
                pl_size = os.path.getsize(f.name)
                print(f"   🇵🇱 Польский: {pl_size} байт")
                
            # "Английское" произношение того же слова
            tts_en = gTTS(text=word, lang='en', tld='com')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts_en.save(f.name)
                en_size = os.path.getsize(f.name)
                print(f"   🇺🇸 Английский: {en_size} байт")
                
            if pl_size != en_size:
                print(f"   ✅ Различие: {abs(pl_size - en_size)} байт")
            else:
                print(f"   ⚠️ Одинаковые размеры - возможная проблема")
                
        except Exception as e:
            print(f"   ❌ Ошибка для '{word}': {e}")

def test_alternative_polish_settings():
    """Тест альтернативных настроек для польского языка"""
    
    print("\n\n🔧 Тестирование альтернативных настроек польского TTS")
    print("=" * 65)
    
    text = "Dzień dobry, jak się Pan ma?"
    print(f"📝 Тестовый текст: '{text}'")
    
    settings = [
        {'lang': 'pl', 'tld': 'com', 'slow': False, 'desc': 'Стандартный польский'},
        {'lang': 'pl', 'tld': 'pl', 'slow': False, 'desc': 'Польский с польским TLD'},
        {'lang': 'pl', 'tld': 'com', 'slow': True, 'desc': 'Медленный польский'},
        {'lang': 'pl', 'tld': 'co.uk', 'slow': False, 'desc': 'Польский с UK TLD'},
        {'lang': 'en', 'tld': 'com', 'slow': False, 'desc': 'Английский (для сравнения)'},
    ]
    
    results = []
    
    for setting in settings:
        try:
            print(f"\n🧪 {setting['desc']}:")
            print(f"   Параметры: lang='{setting['lang']}', tld='{setting['tld']}', slow={setting['slow']}")
            
            tts = gTTS(
                text=text, 
                lang=setting['lang'], 
                tld=setting['tld'], 
                slow=setting['slow']
            )
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tts.save(f.name)
                size = os.path.getsize(f.name)
                
                results.append({
                    'desc': setting['desc'],
                    'size': size,
                    'file': f.name,
                    'settings': setting
                })
                
                print(f"   ✅ Размер: {size} байт")
                print(f"   📁 Файл: {f.name}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            results.append({
                'desc': setting['desc'],
                'size': 0,
                'error': str(e),
                'settings': setting
            })
    
    # Анализ результатов
    print("\n📊 Анализ результатов:")
    print("-" * 40)
    
    successful_results = [r for r in results if 'error' not in r]
    if len(successful_results) > 1:
        sizes = [r['size'] for r in successful_results]
        unique_sizes = set(sizes)
        
        print(f"Уникальных размеров: {len(unique_sizes)}")
        
        if len(unique_sizes) == 1:
            print("⚠️ ПРОБЛЕМА: Все настройки дают одинаковый размер файла!")
            print("🔍 Это может означать, что gTTS игнорирует языковые настройки")
        else:
            print("✅ Размеры различаются - настройки работают")
            
        for result in successful_results:
            print(f"  {result['desc']}: {result['size']} байт")
    
    return results

if __name__ == "__main__":
    print("🔍 Диагностика польского произношения в gTTS")
    print("=" * 50)
    
    test_polish_vs_english_accent()
    test_polish_specific_sounds()
    results = test_alternative_polish_settings()
    
    print("\n🎯 Заключение:")
    print("=" * 30)
    print("1. Если размеры файлов различаются - gTTS работает правильно")
    print("2. Если размеры одинаковые - проблема в gTTS или настройках")
    print("3. Проверьте созданные файлы на слух для окончательной диагностики")
    print("4. Возможно, потребуется альтернативный TTS сервис для польского языка")