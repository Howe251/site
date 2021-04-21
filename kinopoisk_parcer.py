from googletrans import Translator, constants
from imdb import IMDb
import re


def translate(params):
    text = params['search']
    translator = Translator()
    translation = translator.translate(text, dest='ru')
    print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
    text = translation.text
    i = 1
    while i < len(text)-1:
        if text[i+1].isupper():
            text = text[0:i+1] + " " + text[i+1::]
            i+=1
        i+=1
    params['search'] = text
    return params


def imgResize(movie):
    img = movie['cover url']
    img_ap = img.rfind("@")+1
    if not img_ap:
        print("None @")
        img_ap = img.rfind("._V")
    img = img[0:img_ap]+img[-4::]
    movie['cover url'] = img
    return movie


def Film_parse(title):
    country = "США"
    season = 1
    films = []
    match = re.search(r'S\d{2}', title)
    if match:
        season = int(title[match.start()+1:match.end()])
        title = title[0:-4]
        print(season)
    ia = IMDb()
    print(title)
    search = ia.search_movie(title=title)
    if len(search) > 0:
        print(search[0].movieID)
        movie = ia.get_movie(search[0].movieID)
        if 'cover url' not in movie:
            title = translate({'search': title})
            print(title)
            search = ia.search_movie(title=title['search'])
            print(search[0].movieID)
            movie = ia.get_movie(search[0].movieID)
        print(movie['original title'])
        imgResize(movie)
        if movie['kind'] == 'tv series' and 'plot' in movie:
            seasons = movie['number of seasons']
            description = movie['plot'][season - 1]
        elif 'plot' in movie:
            seasons = 'Фильм'
            description = movie['plot']
        else:
            seasons = 'Фильм'
            description = 'Нет данных'
        if 'year' in movie:
            year = movie['year']
        else:
            year = 'Нет данных'
        if 'countries' in movie:
            for country in movie['countries']:
                country = country + " "
        films.append({'name': movie['original title'],
                      'country': country,
                      'seasons': seasons,
                      'season': season,
                      'type': movie['kind'],
                      'year': year,
                      'img': movie['cover url'],
                      'description': description})
        return films
    else:
        return ([{'name': title,
                'country': 'Нет данных',
                'seasons': '1',
                'season': 1,
                'type': 'Нет данных',
                'year': '0',
                'img': 'Нет данных',
                'description': [{"Нет данных"},]},])

# print(Film_parse("Avatar 2009"))
