import requests
from bs4 import BeautifulSoup
import kinopoisk_parcer

URL = 'https://shikimori.one/animes/status/released'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
           'accept': '*/*'}


def get_html(url, params=None):
    try:
        r = requests.get(url, headers=HEADERS, params=params)
        return r
    except requests.exceptions.MissingSchema as e:
        print(e)


def get_url(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find('article')
        link = items.find('a').get('href')
        return link
    except AttributeError as e:
        print(e)


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find('h1').get_text()
    eps = "Фильм"
    item = soup.find('div', class_='b-db_entry')
    img = item.find('img').get('src')
    anime = []
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
            elif a == 'Жанры:':
                genre = ''
                for n in item.find_all('span', class_='genre-ru'):
                    genre += n.get_text() + ' '
                print(genre)
                break
    desc = soup.find('div', class_='b-text_with_paragraphs').get_text()
    print(desc)

    anime.append({
            'name': name,
            'episodes': eps,
            'status': status,
            'description': desc,
            'genre': genre,
            'img': img
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


def find(params, tries=3):
    for attempt in range(tries):
        try:
            #kinopoisk_parcer.translate(params)
            name = params["search"]
            title = kinopoisk_parcer.KinopoiskParse(name)
            if not title:
                raise IndexError
            else:
                return title
        except IndexError:
            if attempt < (tries - 1) and attempt < 1:
                print("Ошибка! попытка перевода")
                kinopoisk_parcer.translate(params)
                name = params["search"]
                try:
                    title = kinopoisk_parcer.KinopoiskParse(name)
                    return title
                except IndexError:
                    print("Ошибка поиска")
            elif (tries - 1) > attempt >= 1:
                try:
                    print("Ошибка! попытка поиска на Shikimori")
                    title = parce(params)
                    return title
                except AttributeError:
                    file = open("error.txt", "a")
                    file.write("Неудалось распознать " + params["search"] + "\n")
                    file.close()
                    print("На Shikimori этого нет")


# params = None
#parce(params={'search': 'DityaPogody'})
