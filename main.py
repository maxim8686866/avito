import time
import mysql.connector
import requests
import pytesseract as tess
from bs4 import BeautifulSoup as BS
from telegram import Bot
from PIL import Image
from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options

new = []
vip = []
obv_sql = []


class ParseMode(object):
    HTML = 'HTML'
    """:obj:'str': 'HTML """

# отправка сообщений
def send_message(text):
    chat_id = []

    bot = Bot(
        token='1073700436:AAGRNtbf2_gW7W5WxehQn8uVUVRzqW1UGKI',
        base_url='https://telegg.ru/orig/bot',
    )
    for user_id in chat_id:
        bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

# соедение с таблицей
def connect():
    db = mysql.connector.connect(
        host="0.0.0.0",
        user="-",
        passwd="-",
        port="3306",
        database="aviator",
        charset='utf8'
    )
    return db

# парсинг страницы поиска
def soups():
    session = requests.Session()
    request = session.get('https://www.avito.ru/moskva_i_mo/kvartiry/sdam/'
                          'na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&user=1&f=ASgBAQICAkSSA8gQ8AeQUgFAzAhEklmQWY5ZjFk',
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                 ' (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    soup = BS(request.content, 'lxml')
    divs = soup.find_all('div', class_='item__line')
    return divs

# функция извлечения просмотров с страницы объявления
def procmotr(hrefs):
    session = requests.Session()
    request = session.get(hrefs,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                 ' (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    soup = BS(request.content, 'lxml')
    see = soup.find_all('div', class_='item-view-search-info-redesign')
    sees = []

    for x in see:
        sees.append(x.text)
    try:
        return sees[0][17::]
    except:
        return 'N'

# создание файла
def file():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'test.png')
    return path

# парсинг телефона с страницы объявления
def telefon(hrefs):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(hrefs)
    try:
        driver.find_element_by_partial_link_text('8 9').click()
    except:
        return "Не удалось скопировать номер"
    time.sleep(3)
    try:
        driver.find_element_by_xpath('/html/body/div[11]/div/div/div/div/div[1]').screenshot(file())
    except:
        return "Не удалось скопировать номер"
    img = Image.open(file())
    text = tess.image_to_string(img)
    os.remove(file())
    return text

# основной код
def osnova():
    count = 0
    count_1 = 0
    db = connect()
    cursor = db.cursor()
    for div in soups():
        premium = div.find_all('div', attrs={'data-props': '{"vas":[]}'})
        if (len(premium)) == 0:
            vip.append(div)
        else:
            kv = div.find('a', class_='snippet-link').text
            kv = list(filter(None, map(lambda i: i.strip(), kv.split('\n'))))
            price = div.find(class_='snippet-price').text
            price = list(filter(None, map(lambda i: i.strip(), price.split('\n'))))
            data = div.find(class_='snippet-date-info').text
            data = list(filter(None, map(lambda i: i.strip(), data.split('\n'))))
            href_0 = div.find('a', class_='snippet-link')['href']
            try:
                city = div.find('span', class_='item-address-georeferences-item__content').text
            except:
                return
            hrefs = 'https://www.avito.ru/' + href_0
            sql = "SELECT hrefs FROM pars_1 WHERE hrefs = %s"
            var = (hrefs,)
            cursor.execute(sql, var)
            res = cursor.fetchall()
            if not res:
                count += 1
                sql = "INSERT INTO pars_1 (city, kv, price, data, hrefs)  VALUES (%s, %s, %s, %s, %s)"
                var = (city,
                       kv[0],
                       price[0],
                       data[0],
                       hrefs,)
                cursor.execute(sql, var)
                db.commit()
                if city == 'Москва':
                    send_message(
                        f'<i>{city}</i> {kv[0]} {price[0]} <a href="{hrefs}">home</a> {procmotr(hrefs)} {telefon(hrefs)}')
                    count_1 += 1
    if count_1 > 0:
        print('Добавилось ' + str(count_1) + ' объявлений по МСК')
    if count > 0:
        print('Добавилось ' + str(count - count_1) + ' объявлений по МО')


if __name__ == '__main__':
    while True:
        try:
            osnova()
        except ConnectionError:
            pass
        time.sleep(10)
