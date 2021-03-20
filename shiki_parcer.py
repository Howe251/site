import requests
from bs4 import BeautifulSoup
import kinopoisk_parcer
from kinopoisk.movie import Movie

URL = 'https://shikimori.one/animes'
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


def try_repeat(func):
    def wrapper(*args, **kwargs):
        count = 10

        while count:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print("Ошибка: Попытка поиска в IMDB")
                kinopoisk_parcer.translate(*args, **kwargs)
                print('Error:', e)
                count -= 1
    return wrapper


@try_repeat
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
#parce(params={'search': 'DityaPogody'})
