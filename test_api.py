#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8001/api/cards/enrich/?user_id=1'
data = {
    'original_phrase': 'beber',
    'keyword': 'beber',
    'deck_id': 2
}

headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")