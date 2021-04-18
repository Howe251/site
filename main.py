import sys
import os
import shiki_parcer as parcer
import Database
import kinopoisk_parcer

mults = []
films = []
serial = False


def find_series_mult(k, i, mult):
    print(k[i])
    if mult in k[i]: #playlist.index(k[i][0:k[i].find('/')]) == 0:
        directory = k[i].replace(mult, '')
        if k[i].count('/') > 5:
            serial = True
            pathid = directory.find('/')
            path = directory[0:pathid]
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
                               'full_name': seria,
                               'directory': path})
                print(seria)
                if path not in k[i+1]:
                    break
                i+=1
        else:
            seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/') + 1::]
            nameofseria = remove(seria)
            series.append({'name': nameofseria,
                           'full_name': seria,
                           'directory': path})
            print(seria)
    return name, series, path, i


def check_files_mkv_mult():
    os.system("find /disk1/Downloads/films -name *.mkv > playlist.txt")
    k = open("playlist.txt", "r").readlines()
    mult = "/disk1/Downloads/films/Мультики/"
    k = [line[:-1] for line in k]
    i = 0
    while i < len(k):
        if mult in k[i]:
            name, series, path, i = find_series_mult(k, i, mult)
            mults.append({'name': name,
                          'directory': path,
                          'series': series,
                          'detail': parcer.parce(params={'search': name.replace(' ', '+')})})
        i+=1
    return mults


def export(mults, i):
    if i:
        Database.export_mult(mults)
    else:
        Database.export_film(mults)


def check_files_mkv_film():
    os.system("find /disk1/Downloads/films -name *.mkv > playlist.txt")
    k = open("playlist.txt", "r").readlines()
    film = "/disk1/Downloads/films/Фильмы/"
    k = [line[:-1] for line in k]
    i = 0
    while i < len(k):
        if film in k[i]:
            directory = k[i].replace(film, '')
            if k[i].count('/') > 5:
                serial = True
                pathid = directory.find('/')
                path = directory[0:pathid]
                print(path)
                name = directory[0:pathid].replace("_", " ")
                name = remove(name.replace(".", " "))
            else:
                path = directory
                name = directory.replace("_", " ")
                name = remove(name.replace(".", " "))
                serial = False
            series = []
            if serial:
                while path in k[i]:
                    seria = k[i].replace(film, '')[k[i].replace(film, '').find('/') + 1::]
                    nameofseria = remove(seria)
                    series.append({'name': nameofseria,
                                   'full_name': seria})
                    print(seria)
                    if path not in k[i + 1]:
                        break
                    i += 1
            else:
                seria = k[i].replace(film, '')[k[i].replace(film, '').find('/') + 1::]
                nameofseria = remove(seria)
                series.append({'name': nameofseria,
                               'full_name': seria})
                print(seria)
            films.append({'name': name,
                          'directory': path,
                          'series': series,
                          'detail': kinopoisk_parcer.Film_parse(name)})
        i+=1
    return films


"""def files_check():
    # os.system("find /disk1/Downloads/films -name *.mkv -printf '%f\n'> playlist.txt")
    os.system("find /disk1/Downloads/films/ -type d -maxdepth 2 -printf '%f\n'> playlist.txt")
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
    #f.close()"""


def find_new_mult():  # Делаем запрос к БД и ищем совпадения названий серий и папок с теми что есть
    series = Database.get_mults()
    os.system("find /disk1/Downloads/films -name *.mkv > playlist.txt")
    k = open("playlist.txt", "r").readlines()
    mult = "/disk1/Downloads/films/Мультики/"
    k = [line[:-1] for line in k]
    i = 0
    mm = []
    while i < len(k) and mult in k[i]:
        name, ser, path, i = find_series_mult(k, i, mult)
        mm.append({'name': name,
                   'series': ser,
                   'path': path})
        i += 1
    ser = [{},]
    for title_local in mm:
        for title_BD in series:
            if title_BD['title_name'] == title_local['path']:
                for ser_title_local in title_local['series']:
                    if ser_title_local['full_name'] in [ser_title_BD[0] for ser_title_BD in title_BD['serie_name']]:
                        pass
                        # print(ser_title_local[0], " --> ", "ЕСТЬ")
                    else:
                        print(ser_title_local['full_name'], " --> ", "НЕТУ")
                        ser.append({'name': ser_title_local['name'],
                                    'full_name': ser_title_local['full_name']})
                        Database.export_series(ser, title_BD['id'])
                        series = Database.get_mults()
                        break


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
            string2 = k[k.find(linest[2]):k.find(linest[3]) + 1]
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

    """for idx, i in enumerate(k):
        if len(k[idx]) != 0:
            k[idx] += "\n"""
    return k


# connect(read_db_config())
# files_check()
# search()
# parce("Sword+Art+Online+Alicization+-+War+of+Underworld+2nd+Season")

#Database.drop()
#find_new()
#export(check_files_mkv_mult())
#Database.get_mults()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        #if (param_name == "--new" or param_name == "-n") and (param_name2 == "--mults" or param_name2 == "-m"):
        if ("--new" in sys.argv or "-n" in sys.argv) and ("--mults" in sys.argv or "-m" in sys.argv):
            find_new_mult()
        elif ("--new" in sys.argv or "-n" in sys.argv) and ("--films" in sys.argv or "-f" in sys.argv):
            Database.drop(films=True)
            export(check_files_mkv_film(), False)
        elif ("--drop" in sys.argv or "-d" in sys.argv) and ("--mults" in sys.argv or "-m" in sys.argv):
            Database.drop(mults=True)
            export(check_files_mkv_mult(), True)
        elif "--drop" in sys.argv or "-d" in sys.argv:
            Database.drop(True, True)
            export(check_files_mkv_mult(), True)
            export(check_files_mkv_film(), False)
        elif "--help" in sys.argv or "-h" in sys.argv:
            print("-n, --new для поиска новых серий, c дополнительным параметром -f для фильмов и -m для мультиков\n"
                  "-d, --drop для сброса базы данных и нового сканирования\n"
                  "-h, --help для отображения помощи")
        elif "--new" in sys.argv or "-n" in sys.argv:
            print("Необходим дополнительный параметр -f или -m")
        else:
            print("Ошибка в параметрах. Для вывода справки используйте параметр -h")
    else:
        print("Необходим параметр")
