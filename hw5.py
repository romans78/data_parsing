# Написать программу, которая собирает товары "В тренде"
# с сайта техники mvideo и складывае данные в БД.


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
import time

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']

driver = webdriver.Chrome()

driver.get('https://www.mvideo.ru')

driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2.5);")
time.sleep(5)
elem = driver.find_element(By.XPATH, "//button[contains(@class,'tab-button ng-star-inserted')]")
elem.send_keys(Keys.ENTER)
products = driver.find_elements(By.XPATH, "//a[@_ngcontent-serverapp-c226]")
for i in range(0, len(products), 2):
    product_link = products[i].get_attribute('href')
    product_desc = products[i + 1].text
    product_id = product_link.split('/')[-1].split('-')[-1]
    entry_dic = {'_id': product_id, 'product_desc': product_desc, 'product_link': product_link}
    try:
        db['mvideo'].insert_one(entry_dic)

    except dke:
        print(f"Попытка ввода уже существующей записи с id {product_id}")
