import time
from googletrans import Translator, constants
import re
import requests
import json
import main
import shiki_parcer


def translate(params):
    text = params['search']
    translator = Translator()
    translation = translator.translate(text, dest='ru')
    print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
    text = translation.text
    i = 1
    while i < len(text) - 1:
        if text[i + 1].isupper():
            text = text[0:i + 1] + " " + text[i + 1::]
            i += 1
        i += 1
    params['search'] = text
    return params


def imgResize(movie):
    img = movie['cover url']
    img_ap = img.rfind("@") + 1
    if not img_ap:
        print("None @")
        img_ap = img.rfind("._V")
    img = img[0:img_ap] + img[-4::]
    movie['cover url'] = img
    return movie


def SeasonDelete(title):
    match = re.search(r'S\d{2}', title)
    season = 1
    if match:
        season = int(title[match.start() + 1:match.end()])
        title = title[0:-4]
        print(season)
    return title, season


def tryKinopoisk(title, tries=4):
    for attempt in range(tries):
        try:
            return KinopoiskParse(title)
        except IndexError as error:
            if attempt < (tries-1) and attempt < 1:
                print("Ошибка! Попытка удалить сезон")
                title, season = SeasonDelete(title)
            elif (tries - 1) > attempt == 1:
                print("Ошибка! Попытка убрать лишнее")
                title = main.remove(title)
            elif (tries - 1) > attempt > 1:
                print("Попытка перевода названия")
                title = translate({"search": title})["search"]
            else:
                file = open("error.txt", "a")
                file.write("Неудалось распознать " + title + "\n")
                file.close()
                return {'name': title,
                        'country': None,
                        'seasons': None,
                        'type': None,
                        'img': None,
                        'status': "Вышло",
                        'genre': None,
                        'episodes': 1,
                        'description': None,
                        'isShown': False,
                        'year': None}
        except requests.exceptions.ConnectionError:
            checkInternet()
            time.sleep(5)
            tryKinopoisk(title)


def KinopoiskParse(title):
    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword=" + title
    response = requests.get(url, headers={'Accept': 'application/json',
                                          'X-API-KEY': '548541a6-5382-488d-b52f-69a946bad55b'})
    response = json.loads(response.text)
    film_id = str(response['films'][0]['filmId'])
    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/" + film_id
    response = json.loads(requests.get(url, headers={'Accept': 'application/json',
                                                     'X-API-KEY': '548541a6-5382-488d-b52f-69a946bad55b'}).text)
    seasons = 0
    id_last_season = 0
    film = response['data']
    genres = []
    for genre in film['genres']:
        if genre['genre'] == "аниме":
            film2 = shiki_parcer.parce(params={'search': title})
            if len(set(film['nameEn'].lower().split()) &
                   set(film2['name'].split("/")[1].lower().split())) > 1:
                return film2
        genres.append(genre['genre'].capitalize())
    if film['seasons']:
        for i, season in enumerate(film['seasons']):
            if season['number'] >= seasons:
                seasons = int(season['number'])
                id_last_season = i
        for serie in film['seasons'][id_last_season]['episodes']:
            if serie['releaseDate'] is None and serie['episodeNumber'] == 1:
                seasons -= 1
    else:
        seasons = "Фильм"
    if film['type'] == 'TV_SHOW':
        film_type = "Сериал"
    elif film['type'] == 'FILM':
        film_type = "Фильм"
    else:
        film_type = film['type']
    countries = ''
    episodes = 1
    for country in film['countries']:
        countries += country['country'] + " "
    status = "Вышло "+str(film['year'])
    if not film["nameRu"] and film["nameEn"]:
        name = film["nameEn"]
    else:
        name = film["nameRu"]
    films = {'name': name,
             'country': countries.strip(),
             'seasons': seasons,
             'type': film_type,
             'year': film['year'],
             'img': film['posterUrl'],
             'genre': genres,
             'status': status,
             'episodes': episodes,
             'description': film['description'],
             'isShown': True}
    print(films)
    return films


def checkInternet():
    internet = False
    while not internet:
        try:
            requests.get("http://google.com")
            internet = True
        except requests.exceptions.ConnectionError:
            print("Интеренета нет")
            time.sleep(10)
