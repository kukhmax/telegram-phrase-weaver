import requests
import json

print('Создание новой колоды с французским языком...')
data = {
    'name': 'Французский тест',
    'description': 'Тестовая колода',
    'source_language': 'fr',
    'target_language': 'ru'
}

r = requests.post('http://localhost:8000/api/decks/?user_id=1', json=data)
print('Status:', r.status_code)

if r.status_code == 201:
    response = r.json()
    print('Создана колода:', response['name'])
    print('ID:', response['id'])
    print('Языки:', response['source_language'], '->', response['target_language'])
    
    # Тестируем API enrich с новой колодой
    print('\nТестирование API enrich с новой колодой...')
    enrich_data = {
        'original_phrase': 'Bonjour le monde',
        'keyword': 'bonjour',
        'deck_id': response['id']
    }
    
    r2 = requests.post('http://localhost:8000/api/cards/enrich?user_id=1', json=enrich_data)
    if r2.status_code == 200:
        enrich_response = r2.json()
        print('Языки из API enrich:')
        print('source_language:', enrich_response.get('source_language'))
        print('target_language:', enrich_response.get('target_language'))
        print('deck_id:', enrich_response.get('deck_id'))
    else:
        print('Ошибка enrich:', r2.text)
else:
    print('Ошибка создания колоды:', r.text)