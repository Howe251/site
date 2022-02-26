from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import time

import kinopoisk_parcer
import shiki_parcer
from main import scanpath
import main
import Database


def checkDB(film, serie, isMult):
    flag = True
    if isMult:
        mults_online = Database.get_mults()
    else:
        mults_online = Database.get_films()
    for mults in mults_online:
        if film[0]['directory'] == mults['title_name']:
            print("Найдено совпадение")
            is_in_base = False
            for series in mults['serie_name']:
                if series[0] == film[0]['series'][0]['full_path']:
                    print(series[0], "уже есть")
                    flag = False
                    is_in_base = True
                    break
                is_in_base = False
            if not is_in_base:
                print("Тайтл есть, но серии нет в базе")
                serie = [0, serie[0]]
                if isMult:
                    Database.export_series(serie, mults['id'])
                else:
                    Database.export_series_film(serie[1], mults['id'])
                print("записал в БД")
                flag = False
    return flag


def add(path, mult_path):
    name, route, serial = main.prepare_to_export(path, mult_path)
    serie = []
    film = []
    seria = path.replace(mult_path, '')[
            path.replace(mult_path, '').find('/') + 1::]
    nameofseria = main.remove(seria)
    full_path = path.replace(mult_path, "")
    serie.append({'name': nameofseria,
                   'full_name': seria,
                   'full_path': full_path})
    print(seria)
    film.append({
        'name': name,
        'directory': route,
        'series': serie,
        'detail': None
    })
    if checkDB(film, serie, 'Фильмы' not in path):
        if 'Фильмы' in path:
            film[0]['detail'] = kinopoisk_parcer.tryKinopoisk(name)
        else:
            film[0]['detail'] = shiki_parcer.find({'search': name})
        main.export(film, 'Фильмы' not in path)


def addSerie(path):
    print(path)
    directory = path[path.find("Мультики")+9:path.rfind("/")]
    mults_online = Database.get_mults()
    for mult in mults_online:
        if directory == mult['title_name']:
            if ".mkv" in path:
                serie = [{}]
                serie.append({
                    'full_name': path[path.rfind("/")+1:],
                    'full_path': path[path.find("Мультики")+9:],
                    'name': main.remove(path[path.rfind("/")+1:])
                })
                Database.export_series(serie, mult['id'])
                break
    print("нет такого тайтла")
    mults = main.check_files_mkv_mult()
    for mult in mults:
        if mult['directory'] == directory:
            main.export(main.mult_detail([mult]), True)
            print("Добавил в бд")
            break


def delete():
    mults_online = Database.get_mults()
    mults_local = main.check_files_mkv_mult()
    for DB in mults_online:
        if DB["title_name"] not in [ser_title_DB['directory'] for ser_title_DB in mults_local]:
            print(DB["title_name"], "Есть в базе данных, но нет на сервере --> Удаляю из БД")
            Database.delete_mults_by_name(DB["title_name"], True, False)
            break


def deleteSeries(path):
    mults_online = Database.get_mults()
    for DB in mults_online:
        print(path[:path.find("/")])
        if path[:path.find("/")] == DB["title_name"]:
            for serie in DB["serie_name"]:
                if serie[1] == path[path.find("/")+1:]:
                    Database.delete_mults_by_name(serie, True, True)
                    print("Удалил ->", serie)
                    break


def get_bool(prompt):
    while True:
        try:
            return {"yes": True, "no": False}[input(prompt).lower()]
        except KeyError:
            print("Введите yes или no: ")


def modify_event(path, is_multy_path, f):
    if is_multy_path:
        return scanpath+path[path.rfind(f):]
    else:
        return path


class Handler(PatternMatchingEventHandler):
    def on_created(self, event):
        print(event)
        """path = str(event.src_path)
        if "Мультики" in path and not event.is_directory:
            addSerie(path)
        elif "Мультики" in path and event.is_directory:
            pass"""

    def on_deleted(self, event):
        print(event)
        """path = str(event.src_path)
        if "Мультики" in path and event.is_directory:
            delete()
        elif "Мультики" in path and not event.is_directory:
            path = path[path.find("Мультики")+9:]
            if path.find("/") != -1:
                deleteSeries(path)
            else:
                delete()"""

    def on_moved(self, event):
        print(event)
        if "Мультики" in event.dest_path and ".part" not in event.dest_path:
            add(modify_event(event.dest_path, is_multy_path, "/Мультики"), scanpath+"/Мультики/")
        elif "Фильмы" in event.dest_path and ".part" not in event.dest_path:
            add(modify_event(event.dest_path, is_multy_path, "/Фильмы"), scanpath+"/Фильмы/")


if __name__ == "__main__":
    event_handler = Handler(patterns=['*.mkv'])
    observer = Observer()
    is_multy_path = get_bool("Multy path? Yes No \n")
    if is_multy_path:
        #observer.schedule(event_handler, path="/home/howe251/test", recursive=True)
        observer.schedule(event_handler, path="/ext_disk/Downloads/films", recursive=True)
        observer.schedule(event_handler, path="/disk1/Downloads/films", recursive=True)
        observer.schedule(event_handler, path="/disk2/Downloads/films", recursive=True)
    else:
        observer.schedule(event_handler, path=scanpath, recursive=True)
    observer.start()
    print("Сканер запущен")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

