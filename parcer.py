import requests
from bs4 import BeautifulSoup
import logging
from grab import Grab

#URL = 'https://shikimori.one/animes'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
           'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup)
    items = soup.find_all('a', 'cover')
    animes = []
    for item in items:
        animes.append({
            'href': item.find('a', class_='cover').get_text()
        })
    print(animes)


    #with open("test.json", "w") as f:
        #f.writelines(items)
    #print(items)



def parce(params):
    url = "https://shikimori.one/animes"
    html = get_html(url, params)
    if html.status_code == 200:
        #print(html.text)
        get_content(html.text)
    else:
        print("Error")

'''def parce():
    g = Grab(log_file='out.html')
    g.go('https://shikimori.one/animes', method='get')'''

params = None
parce(params)
