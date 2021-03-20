from googletrans import Translator, constants
from imdb import IMDb
import re


def translate(params):
    text = params['search']
    translator = Translator()
    translation = translator.translate(text, dest='ru')
    print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
    text = translation.text
    pattern = '[А-Я]'
    i = 1
    while i < len(text)-1:
        if text[i+1].isupper():
            text = text[0:i+1] + " " + text[i+1::]
            i+=1
        i+=1
    params['search'] = text
    return params


def Film_parse(title):
    country = "США"
    season = 1
    films = []
    match = re.search(r'S\d{2}', title)
    if match:
        season = int(title[match.start()+1:match.end()])
        title = title[0:-4]
        print(season)
    match = re.search(r'\d{4}', title)
    #if match:
    #    title = title[0:match.start()]+title[match.end()::].strip()
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
        return {'name': title,
                'country': 'Нет данных',
                'seasons': '0',
                'season': '0',
                'type': 'Нет данных',
                'year': '0',
                'img': 'Нет данных',
                'description': 'Нет данных'}



# print(Film_parse("Avatar 2009"))
