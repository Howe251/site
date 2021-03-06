import os
import shiki_parcer as parcer
import Database
from imdb import IMDb
from shikimori_api import Shikimori
from kinopoisk.movie import Movie


# mysql.connector.connect(host='localhost', database='mysql', user='root', password='aNfCT9BKTeYyVqBn')

def files_check():
    # os.system("find /srv/hp/Downloads/films -name *.mkv -printf '%f\n'> playlist.txt")
    os.system("find /srv/hp/Downloads/films/ -type d -maxdepth 2 -printf '%f\n'> playlist.txt")
    f = open("playlist.txt", "r")
    k = f.readlines()
    f.close()
    linest = ("(", ")", "[", "]")
    # print(k[2])
    for idx, i in enumerate(k):
        i = i.replace(".", " ")
        # k[idx] = i
        restart = True
        if linest[0] in i or linest[3] in i:
            while restart:
                string = i[i.find(linest[0]):i.find(linest[1]) + 1]
                print(string)
                string2 = i[i.find(linest[2]):i.find(linest[3]) + 1]
                print(string2)
                # print(str(k).find(linest, lineen))
                i = i.replace(string, "")
                i = i.replace(string2, "")
                i = i.lstrip()
                k[idx] = i
                if i.find(linest[0]) == -1 and i.find(linest[3]) == -1:
                    restart = False
    k = remove(k)
    for item in k:
        if len(item) != 0:
            #print(parcer.search(params={'search': item.strip().replace(' ', '+')}))
            Database.export(parcer.parce(params={'search': item.strip().replace(' ', '+')}))
    #f = open("playlist.txt", "w+")
    #f.writelines(k)
    y = 2
    film = False
    while y < len(k):
        print(k[y])
        if len(k[y]) == 0:
            film = True
        if not film:
            #Database.export(parcer.parce(params={'search': k[y].replace(' ', '+')}))
            y += 1
    #f.close()


def remove(k):
    z = open("forbidden.txt", "r")
    # words = z.readlines()
    words = [line[:-1] for line in z]
    k = [line[:-1] for line in k]
    # words = z.readlines().splitlines()
    z.close()
    '''for idx, i in k:
        if i in words:
            k[idx] = i.replace(words, "")
    z.close()'''
    for idy, i in enumerate(k):
        for idx, word in enumerate(words):
            if word in i:
                k[idy] = k[idy].replace(word, "").strip()
                if len(k[idy]) == 0:
                    break
                # er = k.index(word)
                # re_ = re.compile(r'{}'.format(word))
                # k[k.index(word)] = re.sub(re_, '', k[k.index(word)])
                print(k[idy])
    """for idx, i in enumerate(k):
        if len(k[idx]) != 0:
            k[idx] += "\n"""
    return k


def search():
    with open("playlist.txt", "r") as f:
        ia = IMDb()
        k = f.readlines()
        # print(Movie.objects.search(f))
        # for idx in k:

        session = Shikimori()
        api = session.get_api()
        api.animes.Get(search="Sword Art Online Alicization - War of Underworld 2nd Season", kind='movie')
        api.animes(1).GET()
        api.animes(1).screenshots.GET()

        print(ia.search_movie("Shingeki no Kyojin"))
        # TODO: Парсер Шикимори
        # f.write(k)


# connect(read_db_config())
# files_check()
# search()
# parce("Sword+Art+Online+Alicization+-+War+of+Underworld+2nd+Season")

Database.drop()
files_check()
