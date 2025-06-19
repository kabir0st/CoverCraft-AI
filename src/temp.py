import json

with open('datasets/cleaned.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(len(data))
