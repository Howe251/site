import os
import shiki_parcer as parcer
import Database
from imdb import IMDb
from shikimori_api import Shikimori
from kinopoisk.movie import Movie

mults = []
films = []
serial = False

def check_files_mkv():
    os.system("find /srv/hp/Downloads/films -name *.mkv > playlist.txt")
    k = open("playlist.txt", "r").readlines()
    film = "/srv/hp/Downloads/films/Фильмы/"
    mult = "/srv/hp/Downloads/films/Мультики/"
    k = [line[:-1] for line in k]
    i=0
    while i < len(k):
        print(k[i])
        m = True
        print(k[i].count('/'))
        if mult in k[i]: #playlist.index(k[i][0:k[i].find('/')]) == 0:
            directory = k[i].replace(mult, '')
            if k[i].count('/') > 6:
                serial = True
                pathid = directory.find('/')
                path = directory[0:pathid]
                print(path)
                print(directory[0:pathid].replace(".", " "))
                name = remove(directory[0:pathid].replace(".", " "))
            else:
                path = directory
                name = remove(directory.replace(".", " "))
                serial = False
            series = []
            if serial:
                while path in k[i]:
                    seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/')+1::]
                    nameofseria = remove(seria)
                    series.append({'name': nameofseria,
                                   'full_name': seria})
                    print(seria)
                    if path not in k[i+1]:
                        break
                    i+=1
            else:
                seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/') + 1::]
                nameofseria = remove(seria)
                series.append({'name': nameofseria,
                               'full_name': seria})
                print(seria)
            mults.append({'name': name,
                          'directory': path,
                          'series': series,
                          'detail': parcer.parce(params={'search': name.replace(' ', '+')})})
        elif film in k[i]:

            m = False
            route = k[i].replace(film, '')
        i+=1
    Database.export_mult(mults)




def files_check():
    # os.system("find /srv/hp/Downloads/films -name *.mkv -printf '%f\n'> playlist.txt")
    os.system("find /srv/hp/Downloads/films/ -type d -maxdepth 2 -printf '%f\n'> playlist.txt")
    f = open("playlist.txt", "r")
    k = f.readlines()
    k = [line[:-1] for line in k]
    f.close()
    linest = ("(", ")", "[", "]")
    # print(k[2])
    untuched = k
    k = remove(k)
    for idx, i in enumerate(k):
        i = i.replace(".", " ")
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
    #for id, item in enumerate(k):
    #    if len(item) != 0:
    #        playlist.append({'name': item, 'unformated_name': untuched[id]})
    #untuched.clear()
    for id, item in enumerate(k):
        if len(item) != 0:
            #print(parcer.search(params={'search': item.strip().replace(' ', '+')}))
            Database.export_mult(parcer.parce(params={'search': item.strip().replace(' ', '+')}), untuched[id])
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
    linest = ("(", ")", "[", "]")
    if ".mkv" in k:
        k = k.replace(".", " ")[0:-3].strip()
    else:
        k = k.replace(".", " ").strip()
    restart = True
    if linest[0] in k or linest[3] in k:
        while restart:
            string = k[k.find(linest[0]):k.find(linest[1]) + 1]
            print(string)
            string2 = k[k.find(linest[2]):k.find(linest[3]) + 1]
            print(string2)
            k = k.replace(string, "")
            k = k.replace(string2, "")
            k = k.strip()
            if k.find(linest[0]) == -1 and k.find(linest[3]) == -1:
                restart = False
    z = open("forbidden.txt", "r")
    # words = z.readlines()
    words = [line[:-1] for line in z]
    # words = z.readlines().splitlines()
    z.close()
    '''for idx, i in k:
        if i in words:
            k[idx] = i.replace(words, "")
    z.close()'''
    for idx, word in enumerate(words):
        if word in k:
            k = k.replace(word, "").strip()
            if len(k) == 0:
                break
            # er = k.index(word)
            # re_ = re.compile(r'{}'.format(word))
            # k[k.index(word)] = re.sub(re_, '', k[k.index(word)])
            print(k)

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
        #
        # f.write(k)


# connect(read_db_config())
# files_check()
# search()
# parce("Sword+Art+Online+Alicization+-+War+of+Underworld+2nd+Season")

#Database.drop()
check_files_mkv()
