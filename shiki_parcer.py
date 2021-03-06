import requests
from bs4 import BeautifulSoup
import logging
from grab import Grab

URL = 'https://shikimori.one/animes'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
           'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find('article')
    link = items.find('a').get('href')
    return link


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('h1').get_text()
    eps = "Фильм"
    #item = soup.find('div', class_='b-db_entry')
    anime = []
    #for item in items:
    info = soup.find_all('div', class_='line-container')
    print(len(info))
    for item in info:
        print(item.find('div', class_='key'))
        if item.find('div', class_='key') is not None:
            a = item.find('div', class_='key').get_text()
            if a == 'Эпизоды:':
                eps = item.find('div', class_='value').get_text()
            elif a == 'Статус:':
                st = item.find('span', class_='b-anime_status_tag')
                status = st.get('data-text') + item.find('div', class_='value').get_text()
                break
    desc = soup.find('div', class_='b-text_with_paragraphs').get_text()
    print(desc)

    anime.append({
            'name': name,
            'episodes': eps,
            'status': status,
            'description': desc
        })
    return anime[0]

    # with open("test.json", "w") as f:
    # f.writelines(items)
    # print(items)


def search(params):
    # url = "https://shikimori.one/animes"
    # params = "search=" + params
    print(params)
    html = get_html(URL, params)
    if html.status_code == 200:
        # print(html.text)
        url = get_url(html.text)
        return url
    else:
        print("Error")


def parce(params):
    url = search(params)
    html = get_html(url)
    title = get_content(html.text)
    print(title)
    return title






'''def parce():
    g = Grab(log_file='out.html')
    g.go('https://shikimori.one/animes', method='get')'''

# params = None
# parce(params)
