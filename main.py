import sys
import os
import shiki_parcer as parcer
import Database
import kinopoisk_parcer
import subprocess
from subprocess import Popen, PIPE

mults = []
films = []
serial = False
#scanpath = "/home/howe251/test"
scanpath = "/var/www/films/films/assets/filmy"
#/var/www/films3/films/assets/filmy


def find_series_mult(k, i, mult):
    """
    Поиск серий к мультикам отсканированным в check_files_mkv_mult
    :type k: list
    :param k: Список файлов
    :type i: int
    :param i: Индекс в списке
    :type mult: str
    :param mult: Путь к папке с мультами
    :return: Имя, список серий, путь к папке/файлу, индекс
    """
    #print(k[i])
    if mult in k[i]:
        directory = k[i].replace(mult, '')
        if k[i].count('/') > scanpath.count('/') + 2:
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
            while path in k[i] and i < len(k) - 1:
                seria = k[i].replace(mult, '')[k[i].replace(mult, '').find('/') + 1::]
                nameofseria = remove(seria)
                full_path = k[i].replace(mult, "")
                series.append({'name': nameofseria,
                               'full_name': seria,
                               'directory': path,
                               'full_path': full_path})
                #print(seria)
                try:
                    if path not in k[i + 1]:
                        break
                except IndexError:
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
            #print(seria)
    return name, series, path, i


def find_files(root_dir, ext):
    """
    Поиск файлов с определенным расширением в папках
    :param root_dir: Корневая папка (с которой начинать поиск)
    :type root_dir: str
    :param ext: Расширения файлов
    :type ext: list
    :return: Список найденных файлов
    """
    k = []
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        for file in files:
            if file.endswith(tuple(ext)):
                k.append(os.path.join(root, file))
    return k


def check_files_mkv_mult():
    """
    Сканер папки на файлы mkv Мультики
    :return: список словарей с мультиками
    :type: dict
    """
    k = find_files(scanpath, ['mkv', 'avi'])
    mult = os.path.join(scanpath, "Мультики") + ("\\" if os.name == "nt" else "/")
    i = 0
    while i < len(k):
        if mult in k[i]:
            name, series, path, i = find_series_mult(k, i, mult)
            mults.append({'name': name,
                          'directory': path,
                          'series': series,
                          'detail': ''})
        i += 1
    return mults


def mult_detail(mults):
    """
    Поиск детальной информации по мультфильму на Shikimori и Kinopoisk
    :param mults: список словарей с мультфильмами
    :return: Обработанный словарь
    """
    for mult in mults:
        mult['detail'] = parcer.find(params={'search': mult['name'].replace(' ', '+')})
    return mults


def find_subs_mult():
    """
    Функция поиска субтитров к мультикам
    :return: список словарей сабов
    """
    k = find_files(scanpath, ['.ass'])
    mult = scanpath + "/Мультики/"
    i = 0
    subs = []
    print(k[i])
    while i < len(k):
        if mult in k[i]:
            directory = k[i].replace(mult, '')
            if k[i].count('/') > scanpath.count('/') + 2:
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
    """
    Функция поиска озвучек к мультикам в форматах ac3 и mka
    :return: список словарей с озвучками
    """
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
    """
    Экпортирует данные в базу данных
    :type mults: dict
    :param mults:
    :type i: bool
    :param i: Какой словарь? True - Мультфильмы, False - Фильмы
    :return:
    """
    if len(mults) == 0:
        print("Экспортировать нечего")
        sys.exit()
    else:
        if i:
            Database.export_mult(mults)
        else:
            Database.export_film(mults)


def prepare_to_export(path, film):
    """
    Функция подготовки к экспорту
    :type path: str
    :param path: Строка пути к файлу
    :type film: str
    :param film: Строка пути к папке с фильмами/мультиками
    :return: Обрезанные имя файла, путь к файлу, Тип (Сериал или нет)
    """
    directory = path.replace(film, '')
    if path.count('/') > scanpath.count('/') + 2:
        serial = True
        pathid = directory.find('/')
        path = directory[0:pathid]
        print(path)
        name = directory[0:pathid].replace("_", " ")
        name = name.replace(".1.", ".")
        name = remove(name.replace(".", " "))
    else:
        path = directory
        name = directory.replace("_", " ")
        name = remove(name.replace(r'\.(?=.*?\.)', ''))
        serial = False
    return name, path, serial


def check_files_mkv_film():
    """
    Сканирует папку на наличие фильмов и если это сериал делит по сериям
    :return: Словарь с фильмами
    """
    k = find_files(scanpath, ['.mkv'])
    film = scanpath + "/Фильмы/"
    i = 0
    while i < len(k):
        if film in k[i]:
            name, path, serial = prepare_to_export(k[i], film)
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
                    try:
                        if path not in k[i + 1]:
                            break
                    except IndexError:
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
                          'detail': kinopoisk_parcer.tryKinopoisk(name)})
        i += 1
    return films


def find_new_mult():  # Делаем запрос к БД и ищем совпадения названий серий и папок с теми что есть
    """
    Сканирует каталог на наличие Мультфильмов, затем делает запрос к БД. Если найденых файлов в базе нет -> добавляем
    :return: None
    """
    series = Database.get_mults()
    mult = scanpath + "/Мультики/"
    k = find_files(mult, ['.mkv'])
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
    """
    Принимает на вход строку и удаляет из нее все запрещенное
    :type k: str
    :param k: Строка перед обрезкой
    :return: Строка после обрезки
    """
    linest = ("(", ")", "[", "]", "{", "}")
    k = k.replace(".1.", ".")
    if "mkv" in k:
        k = k.replace(".", " ")[0:-3].strip()
    else:
        k = k.replace(".", " ").strip()
    k = k.replace("_", " ")
    restart = True
    if linest[0] in k or linest[3] in k:
        while restart:
            string = k[k.find(linest[0]):k.find(linest[1]) + 1]
            string2 = k[k.find(linest[2]):k.find(linest[3]) + 1]
            string3 = k[k.find(linest[4]):k.find(linest[5]) + 1]
            k = k.replace(string, "")
            k = k.replace(string2, "")
            k = k.replace(string3, "")
            k = k.strip()
            if k.find(linest[0]) == -1 and k.find(linest[3]) == -1:
                restart = False
    z = open("forbidden.txt", "r")
    words = [line[:-1] for line in z]
    z.close()
    for word in words:
        # if word in k:
        #     k = k.replace(word, "").strip()
        copyk = list(filter(None, k.lower().split(" ")))
        for i, w in enumerate(copyk):
            if word.lower() == w:
                k = list(filter(None, k.split()))
                k.pop(i)
                copyk.pop(i)
                k = " ".join(k)
                #k = "".join(k.split().pop(i))
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
            export(mult_detail(check_files_mkv_mult()), True)
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
            export(mult_detail(check_files_mkv_mult()), True)
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
