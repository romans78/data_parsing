# Вариант 1
# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
# с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
# Сохраните в json либо csv.

import requests
from bs4 import BeautifulSoup as bs


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

print(*result_list, sep='\n')

with open('results.csv', 'w', encoding='utf-8') as file:
    file.write('Наименование вакансии,Минимальная зарплата,Максимальная зарплата,Валюта,Ссылка на вакансию\n')
    for i in result_list:
          file.write(f'"{i[0]}",{i[1][0]},{i[1][1]},{i[1][2]},{i[2]}\n')
