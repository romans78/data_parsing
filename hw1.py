# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.


import requests
import json

username = 'romans78'

url = f'https://api.github.com/users/{username}/repos'

response = requests.get(url).json()

result = []

for _ in response:
    result.append(_['name'])

result = [{username: result}]

with open('result.json', 'w') as file:
    file.write(str(json.dumps(result)))
