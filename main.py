import time
import mysql.connector
import requests
import pytesseract as tess
from bs4 import BeautifulSoup as BS
from datetime import datetime
from telegram import Bot
from PIL import Image
from selenium import webdriver
import os

new = []
vip = []
obv_sql = []


# start_time = datetime.now()
class ParseMode(object):
    HTML = 'HTML'
    """:obj:'str': 'HTML """




def send_message(text):

    bot = Bot(
        token='1073700436:AAGRNtbf2_gW7W5WxehQn8uVUVRzqW1UGKI',
        base_url='https://telegg.ru/orig/bot',

    )
    bot.send_message(
        chat_id=325363221,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def connect():
    db = mysql.connector.connect(
        # host="127.0.0.1",
        user="rooter",
        passwd="17721338",
        port="3306",
        database="aviator")
    return db



# CREATE USER 'rooter'@'localhost' IDENTIFIED BY '17721338'
# GRANT ALL PRIVILEGES ON *.* TO 'rooter'@'localhost'
# SHOW GRANTS FOR 'rooter'@'localhost'
# SHOW GRANTS FOR 'aviator'@'localhost'

def stav():
    session = requests.Session()
    request = session.get('https://www.avito.ru/moskva_i_mo/kvartiry/sdam/'
                          'na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&user=1&f=ASgBAQICAkSSA8gQ8AeQUgFAzAhEklmQWY5ZjFk',
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                 ' (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    soup = BS(request.content, 'lxml')
    divs = soup.find_all('div', class_='item__line')
    return divs


def login():
    driver = webdriver.Chrome()
    driver.get('https://www.avito.ru')
    driver.find_element_by_class_name(
        'header-services-menu-link-TRWKh.header-services-menu-link-not-authenticated-3kAga').click()
    driver.find_element_by_class_name(
        'social-network-item-icon-1tXjO.social-network-item-icon_gp-30vPn').click()
    time.sleep(3)
    handles = driver.window_handles
    for handle in handles:
        driver.switch_to.window(handle)
    driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys('maxim8686866@gmail.com')
    driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@name="password"]').send_keys('17721338_aA_aA')
    driver.find_element_by_xpath('//*[@id="passwordNext"]/span/span').click()
    time.sleep(5)

    driver.switch_to.window(
        'https://www.avito.ru/moskva_i_mo/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&user=1&f=ASgBAQICAkSSA8gQ8AeQUgFAzAhEklmQWY5ZjFk')
    time.sleep(10)


def stav_2(hrefs):
    session = requests.Session()
    request = session.get(hrefs,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                                 ' (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'})
    soup = BS(request.content, 'lxml')
    see = soup.find_all('div', class_='item-view-search-info-redesign')
    sees = []

    for x in see:
        sees.append(x.text)
    return sees[0][17::]


def img(hrefs):
    driver = webdriver.Chrome()
    driver.get(hrefs)
    driver.find_element_by_partial_link_text('8 9').click()
    time.sleep(3)
    # driver.find_element_by_class_name('item-phone-big-number.js-item-phone-big-number').screenshot('/Users/mac/Desktop/test.png')
    try:
        driver.find_element_by_xpath('/html/body/div[11]/div/div/div/div/div[1]').screenshot(
            '/Users/mac/Desktop/test.png')
    except:
        return "Не удалось скопировать номер"
    img = Image.open('/Users/mac/Desktop/test.png')

    text = tess.image_to_string(img)
    os.remove('/Users/mac/Desktop/test.png')
    return text


def stav_1():
    count = 0
    count_1 = 0
    db = connect()
    cursor = db.cursor()
    for div in stav():
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
                # if city == 'Москва':
                send_message(
                    f'<i>{city}</i> {kv[0]} {price[0]} <a href="{hrefs}">ссылка</a> {stav_2(hrefs)} {img(hrefs)}')
                count_1 += 1
    if count_1 > 0:
        print('Добавилось ' + str(count_1) + ' объявлений по МСК')
    if count > 0:
        print('Добавилось ' + str(count - count_1) + ' объявлений по МО')


# login()
while True:
    stav_1()

    time.sleep(10)
# print(datetime.now() - start_time)
