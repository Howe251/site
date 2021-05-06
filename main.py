import sys
import os
import shiki_parcer as parcer
import Database
import kinopoisk_parcer

mults = []
films = []
serial = False
scanpath = "/disk1/Downloads/films"


def find_series_mult(k, i, mult):
    print(k[i])
    if mult in k[i]:
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
                seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/') + 1::]
                nameofseria = remove(seria)
                full_path = k[i].replace(mult, "")
                series.append({'name': nameofseria,
                               'full_name': seria,
                               'directory': path,
                               'full_path': full_path})
                print(seria)
                if path not in k[i + 1]:
                    break
                i += 1
        else:
            seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/') + 1::]
            nameofseria = remove(seria)
            full_path = k[i].replace(mult, "")
            series.append({'name': nameofseria,
                           'full_name': seria,
                           'directory': path,
                           'full_path': full_path})
            print(seria)
    return name, series, path, i


def check_files_mkv_mult():
    os.system(f"find {scanpath} -name *.mkv > playlist.txt")
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
        i += 1
    return mults


def find_subs_mult():
    os.system(f"find {scanpath} -name *.ass > subs.txt")
    k = open("subs.txt", "r").readlines()
    mult = "/disk1/Downloads/films/Мультики/"
    k = [line[:-1] for line in k]
    i = 0
    subs = []
    print(k[i])
    while i < len(k):
        if mult in k[i]:
            directory = k[i].replace(mult, '')
            if k[i].count('/') > 6:
                pathid = directory.find('/')
                subdir = directory[pathid + 1:directory.find('/', pathid + 1)]
                path = directory[0:pathid]
                if subdir.find("[") == -1:
                    autor = directory[directory.rfind(subdir):directory.rfind("/")].replace(subdir + "/", "")
                    print(autor)
                else:
                    autor = subdir[subdir.find("[") + 1:subdir.find("]")]
            while path + "/" + subdir in k[i] and i < len(k):
                subid = k[i].rfind("/")
                subtitle = k[i][subid + 1::]
                nameofsub = remove(subtitle.replace(".ass", ""))
                full_path = k[i].replace(mult + path, "")
                if len(autor) == 0:
                    autor = "Нету"
                subs.append({'name': nameofsub,
                             'autor': autor,
                             'full_name': subtitle,
                             'directory': path,
                             'full_path': full_path})
                print(subtitle)
                if i + 1 < len(k):
                    if path + "/" + subdir not in k[i + 1]:
                        break
                else:
                    break
                i += 1
        i += 1
    return subs


def find_audio_mult():
    audio = []
    # os.system(f"find {scanpath} -name *.ass > subs.txt")
    try:
        for root, dirs, files in os.walk(f"{scanpath}/Мультики"):
            for file in files:
                if file.endswith(".mka") or file.endswith(".ac3"):
                    autor = root[root.rfind("/")+1:]
                    directory = root.replace(scanpath + "/Мультики/", "")
                    audio.append({"name": remove(os.path.splitext(file)[0]),
                                  "full_name": file,
                                  "autor": autor,
                                  "directory": directory[:directory.rfind("/")],
                                  "full_path": os.path.join(root, file).replace(scanpath+"/Мультики/", "")})
        return audio
    except FileNotFoundError as e:
        print("Нет такого файла или каталога:", str(e)[str(e).find("'"):str(e).rfind("'")+1])


def export(mults, i):
    if i:
        Database.export_mult(mults)
    else:
        Database.export_film(mults)


def check_files_mkv_film():
    os.system(f"find {scanpath} -name *.mkv > playlist.txt")
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
                    full_path = k[i].replace(film, "")
                    series.append({'name': nameofseria,
                                   'full_name': seria,
                                   'full_path': full_path})
                    print(seria)
                    if path not in k[i + 1]:
                        break
                    i += 1
            else:
                seria = k[i].replace(film, '')[k[i].replace(film, '').find('/') + 1::]
                nameofseria = remove(seria)
                full_path = k[i].replace(film, "")
                series.append({'name': nameofseria,
                               'full_name': seria,
                               'full_path': full_path})
                print(seria)
            films.append({'name': name,
                          'directory': path,
                          'series': series,
                          'detail': kinopoisk_parcer.Film_parse(name)})
        i += 1
    return films


# TODO Сделать проверку на 3х разных сервисах что-бы избежать ошибки правильности названия
#  (KinopoiskApi, IMDB, shikimori)

def find_new_mult():  # Делаем запрос к БД и ищем совпадения названий серий и папок с теми что есть
    series = Database.get_mults()
    mult = "/disk1/Downloads/films/Мультики/"
    os.system(f"find {mult} -name *.mkv > playlist.txt")
    k = open("playlist.txt", "r").readlines()
    k = [line[:-1] for line in k]
    i = 0
    mm = []
    while i < len(k) and mult in k[i]:
        name, ser, path, i = find_series_mult(k, i, mult)
        mm.append({'name': name,
                   'series': ser,
                   'path': path})
        i += 1
    ser = [{}, ]
    for title_local in mm:
        for title_BD in series:
            if title_BD['title_name'] == title_local['path']:
                for ser_title_local in title_local['series']:
                    if ser_title_local['full_name'] in [ser_title_BD[0] for ser_title_BD in title_BD['serie_name']]:
                        pass
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
    words = [line[:-1] for line in z]
    z.close()
    for idx, word in enumerate(words):
        if word in k:
            k = k.replace(word, "").strip()
            if len(k) == 0:
                break
    return k


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if ("--new" in sys.argv or "-n" in sys.argv) and ("--mults" in sys.argv or "-m" in sys.argv):
            find_new_mult()
        elif ("--drop" in sys.argv or "-d" in sys.argv) and ("--films" in sys.argv or "-f" in sys.argv):
            Database.drop(films=True)
            export(check_files_mkv_film(), False)
        elif ("--drop" in sys.argv or "-d" in sys.argv) and ("--mults" in sys.argv or "-m" in sys.argv):
            Database.drop(mults=True)
            export(check_files_mkv_mult(), True)
            Database.export_sub_audio(find_subs_mult(), "subs")
            Database.export_sub_audio(find_audio_mult(), "audio")
        elif ("--drop" in sys.argv or "-d" in sys.argv) and ("--subs" in sys.argv or "-s" in sys.argv):
            Database.drop(subs=True)
            Database.export_sub_audio(find_subs_mult(), "subs")
        elif ("--drop" in sys.argv or "-d" in sys.argv) and ("--audio" in sys.argv or "-a" in sys.argv):
            Database.drop(audio=True)
            Database.export_sub_audio(find_audio_mult(), "audio")
        elif "--drop" in sys.argv or "-d" in sys.argv:
            Database.drop(True, True, True, True)
            export(check_files_mkv_mult(), True)
            export(check_files_mkv_film(), False)
            Database.export_sub_audio(find_subs_mult(), "subs")
            Database.export_sub_audio(find_audio_mult(), "audio")
        elif "--help" in sys.argv or "-h" in sys.argv:
            print("-n, --new для поиска новых серий, c дополнительным параметром -m для мультиков, для фильмов -d -f\n"
                  "-d, --drop для сброса базы данных и нового сканирования\n"
                  "-h, --help для отображения помощи")
        elif "--new" in sys.argv or "-n" in sys.argv:
            print("Необходим дополнительный параметр -m")
        else:
            print("Ошибка в параметрах. Для вывода справки используйте параметр -h")
    else:
        print("Необходим параметр")
