# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru,
# yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
#
# Сложить собранные новости в БД

import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from lxml import html
from pprint import pprint
from datetime import date, timedelta

today = date.today().strftime("%d/%m/%Y")
yesterday = (date.today() + timedelta(days=-1)).strftime("%d/%m/%Y")

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

response = requests.get("https://yandex.ru/news")
dom = html.fromstring(response.text)

items = dom.xpath("//article")

client = MongoClient('127.0.0.1', 27017)
db = client['yandex_news']
news = db.news


for item in items:
    article_name = item.xpath(".//h2[contains(@class,'mg-card__title')]/text()")[0].replace('\xa0', ' ')
    article_link = item.xpath(".//a[contains(@class,'mg-card__source-link')]/@href")[0]
    article_source = item.xpath(".//a[contains(@class,'mg-card__source-link')]/@aria-label")[0].split(':')[-1].strip()
    article_date = item.xpath(".//span[contains(@class,'mg-card-source__time')]/text()")[0]
    article_date = yesterday if 'вчера' in article_date else today
    article_id = [id.split('=')[-1] for id in article_link.split('&') if 'persistent_id' in id][0]
    entry_dic = {'_id': article_id, 'source_name': article_source, 'name': article_name,
                 'link': article_link,
                 'date': article_date}
    try:
        db['yandex_news'].insert_one(entry_dic)

    except dke:
        print(f"Попытка ввода уже существующей записи с id {article_id}")
