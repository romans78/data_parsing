# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию. Добавить в решение со
# сбором вакансий(продуктов) функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты - минимальнную и максимульную).

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke


def get_salary(vacancy_salary):
    if not vacancy_salary or vacancy_salary.text == '':
        return (None, None, None)
    else:
        salaries = list(map(lambda x: x.replace('\u202f', ''), vacancy_salary.text.split(' ')))
        min_salary = float(salaries[1]) if 'от' in salaries else (float(salaries[0]) if len(salaries) == 4 else None)
        max_salary = float(salaries[1]) if 'до' in salaries else (float(salaries[2]) if len(salaries) == 4 else None)
        return (min_salary, max_salary, salaries[-1])
    pass


search_word = 'python'
url = 'https://hh.ru/search/vacancy'
params = {'area': 1, 'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': search_word, 'page': 0}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'}
vacancy_names = []
vacancy_links = []
vacancy_salary_ranges = []
while True:
    response = requests.get(url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    vacancy_headers = [i.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}) for i in vacancies]
    vacancy_salary_ranges.extend(
        [get_salary(i.find('div', attrs={'class': 'vacancy-serp-item__sidebar'})) for i in vacancies])

    vacancy_names.extend([i.text for i in vacancy_headers])
    vacancy_links.extend([i['href'].split('?')[0] for i in vacancy_headers])
    if not response.ok:
        break
    print(f'page {params["page"]}', sep='\n')
    params['page'] += 1

result_list = list(zip(vacancy_names, vacancy_salary_ranges, vacancy_links))


def add_to_mongoDB(db, collection, entry):
    entry_dic = {'_id': entry[2].split('/')[-1], 'vacancy_name': entry[0], 'min_salary': entry[1][0],
                 'max_salary': entry[1][1],
                 'currency': entry[1][2], 'link': entry[2]}
    try:
        db[collection].insert_one(entry_dic)
        return 0
    except dke:
        print(f"Попытка ввода уже существующей записи с id {entry[2].split('/')[-1]}")
        return 1


client = MongoClient('127.0.0.1', 27017)
db = client['hhru']
vacancies = db.vacancies

duplicates = 0

for entry in result_list:
    duplicates += add_to_mongoDB(db, vacancies.name, entry)

print(f'Всего было {duplicates} попыток ввода существующих записей')

min_salary_amount = 200000


def find_vacancies_by_salary(min_salary_amount):
    result = db['vacancies'].find(
        {'$or': [{'min_salary': {'$gte': min_salary_amount}}, {'max_salary': {'$gte': min_salary_amount}}]})
    for i in result:
        pprint(i)


find_vacancies_by_salary(min_salary_amount)
