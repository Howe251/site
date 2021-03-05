import mysql.connector
import os
import parcer
from imdb import IMDb
from shikimori_api import Shikimori
from kinopoisk.movie import Movie
from mysql.connector import Error
from configparser import ConfigParser



def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db


def connect(db):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(**db)
        if conn.is_connected():
            print('Connected to MySQL database')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalog_films")
        row = cursor.fetchone()

        while row is not None:
            print(row)
            row = cursor.fetchone()
    except Error as e:
        print(e)
    finally:
        conn.close()
        print("Connection closed")


def files_check():
    # os.system("find /srv/hp/Downloads/films -name *.mkv -printf '%f\n'> playlist.txt")
    os.system("find /srv/hp/Downloads/films/ -type d -maxdepth 2 -printf '%f\n'> playlist.txt")
    f = open("playlist.txt", "r")
    k = f.readlines()
    f.close()
    f = open("playlist.txt", "w+")
    linest = "("
    lineen = ")"
    liness = "["
    linesn = "]"
    # print(k[2])
    for idx, i in enumerate(k):
        i = i.replace(".", " ")
        k[idx] = i
        restart = True
        if linest in i or liness in i:
            while restart:
                string = i[i.find(linest):i.find(lineen) + 1]
                print(string)
                string2 = i[i.find(liness):i.find(linesn) + 1]
                print(string2)
                # print(str(k).find(linest, lineen))
                i = i.replace(string, "")
                i = i.replace(string2, "")
                i = i.lstrip()
                k[idx] = i
                if i.find(liness) == -1 and i.find(linest) == -1:
                    restart = False
    k = remove(k)
    for item in k:
        if len(item) != 0:
            print(parcer.parce(params={'search': item.replace(' ', '+')}))
    f.writelines(k)
    f.close()


def remove(k):
    z = open("forbidden.txt", "r")
    #words = z.readlines()
    words = [line[:-1] for line in z]
    k = [line[:-1] for line in k]
    #words = z.readlines().splitlines()
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
    #print(Movie.objects.search(f))
        #for idx in k:

        session = Shikimori()
        api = session.get_api()
        api.animes.Get(search="Sword Art Online Alicization - War of Underworld 2nd Season", kind='movie')
        api.animes(1).GET()
        api.animes(1).screenshots.GET()

        print(ia.search_movie("Shingeki no Kyojin"))
        # TODO: Парсер Шикимори
        # f.write(k)

# connect(read_db_config())
#files_check()
#search()
#parce("Sword+Art+Online+Alicization+-+War+of+Underworld+2nd+Season")


files_check()
