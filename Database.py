from sys import exit
import mysql.connector
from mysql.connector import Error
from mysql.connector.errors import IntegrityError, ProgrammingError
from configparser import ConfigParser
from datetime import datetime


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
        raise Exception(f'{section} not found in the {filename} file')
    return db


def get_mults(conn=None):
    """
    Функция получения мультфильмов из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список мультфильмов в базе
    """
    animes = []
    if not conn:
        conn = connect(read_db_config())
        global_conn = True
    cursor = conn.cursor()
    cursor.execute("SELECT unformated_name, id FROM mult_mult")  # Список всех тайтлов
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute(f"SELECT href, full_name FROM `mult_series` "
                       f"WHERE name_id = (SELECT id FROM mult_mult WHERE id = {row[1]})")  # Спиоск всех серий с id
        series = cursor.fetchall()
        animes.append({'title_name': row[0],
                       'serie_name': series,
                       'id': row[1]})
    if "global_conn" in dir(): conn.close()
    return animes


def get_subs(conn=None):
    """
    Функция получения субтитров из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список субтитров в базе
    """
    if not conn:
        conn = connect(read_db_config())
        global_conn = True
    cursor = conn.cursor()
    cursor.execute("SELECT name_sub, id FROM mult_subs")  # Список всех субтитров
    if "global_conn" in dir(): conn.close()
    return cursor.fetchall()


def get_audio(conn=None):
    """
    Функция получения аудио к мультфильмам из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список аудио к мультфильмам в базе
    """
    if not conn:
        conn = connect(read_db_config())
        global_conn = True
    cursor = conn.cursor()
    cursor.execute("SELECT name_audio, id FROM mult_audio")  # Список всех аудио
    if "global_conn" in dir(): conn.close()
    return cursor.fetchall()


def get_films(conn=None):
    """
    Функция получения фильмов из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список фильмов в базе
    """
    films = []
    if not conn:
        conn = connect(read_db_config())
        global_conn = False
    cursor = conn.cursor()
    cursor.execute("SELECT unformated_name, id FROM mult_film")  # Список всех фильмов
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute(f"SELECT href FROM `mult_seriesfilms` "
                       f"WHERE name_id = (SELECT id FROM mult_film WHERE id = {row[1]})")  # Спиоск всех серий с id
        series = cursor.fetchall()
        films.append({'title_name': row[0],
                       'serie_name': series,
                       'id': row[1]})
    if "global_conn" in dir(): conn.close()
    return films


def get_genres(conn=None):
    """
    Функция получения списка жанров из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список жанров в базе
    """
    if not conn:
        conn = connect(read_db_config())
        global_conn = False
    cursor = conn.cursor()
    cursor.execute("SELECT `id`, `name` FROM mult_genre")
    if "global_conn" in dir(): conn.close()
    return cursor.fetchall()


def get_mult_genre(id, conn=None):
    """
    Функция получения жанров к мультфильму по id из базы данных
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return: Список жанров к мультфильму по id в базе
    """
    if not conn:
        conn = connect(read_db_config())
        global_conn = False
    cursor = conn.cursor()
    cursor.execute(f"SELECT `id`, `mult_id`, `genre_id` FROM mult_mult_genre WHERE mult_id = {id}")
    if "global_conn" in dir():
        conn.close()
    return cursor.fetchall()


def get_mult_id(mult, cursor):
    cursor.execute(f"SELECT `id` FROM mult_mult WHERE unformated_name = '{mult}'")
    return cursor.fetchall()[0]


def get_film_id(film, cursor):
    cursor.execute(f"""SELECT `id` FROM mult_film WHERE unformated_name = "{film}";""")
    return cursor.fetchall()[0]


def get_genre_id(genre, cursor):
    cursor.execute(f"SELECT `id` FROM mult_genre WHERE name = '{genre}'")
    return cursor.fetchall()[0]


def add_genre(genre, conn=None):
    """
    Функция добавления жанров в базу данных
    :param genre: Жанр
    :type genre: str
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    """
    if not conn:
        conn = connect(read_db_config())
        global_conn = False
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO mult_genre (`name`) VALUES ('{genre}')")
    conn.commit()
    if "global_conn" in dir(): conn.close()


def delete_by_name(name, mults=False, serie=False, conn=None):
    """
    Удалить объект из базы данных по имени
    :param name: Имя объекта
    :type name: str, list
    :param mults: Искать в мультиках?
    :type mults: bool
    :param serie: True - name -> list, False - name -> str
    :type serie: bool
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    """
    table = "mult" if mults else "film"
    if not conn:
        conn = connect(read_db_config())
        global_conn = False
    cursor = conn.cursor()
    try:
        if not serie:
            name = name.replace("'", '\'')
            cursor.execute(f"""SELECT id, unformated_name, name FROM mult_{table} WHERE unformated_name="{name}";""")
            rows = cursor.fetchall()
            cursor.execute(f"DELETE FROM `mult_{table}` WHERE `mult_{table}`.`id` = {rows[0][0]}")
            conn.commit()
        else:
            print(name[0][:name[0].find('/')])
            cursor.execute(f"SELECT id, unformated_name, name FROM mult_{table} WHERE unformated_name='{name[0][:name[0].find('/')]}';")
            rows = cursor.fetchall()
            cursor.execute(f"SELECT id, name_serie FROM mult_series{'films' if table=='film' else ''} WHERE name_id='{rows[0][0]}' AND full_name='{name[1]}';")
            rows = cursor.fetchall()
            if rows:
                cursor.execute(f"DELETE FROM mult_series{'films' if table=='film' else ''} WHERE id='{rows[0][0]}'")
                conn.commit()
        if "global_conn" in dir(): conn.close()
    except IntegrityError as e:
        print(e)
        if "constraint fails" in e.msg:
            print("Попытка изменить FK с RESTRICT на CASCADE")
            FK = e.msg[e.msg.find("(")+1:e.msg.rfind(")")].split()
            print("Удаляю старый FK")
            cursor.execute(f"""ALTER TABLE {FK[0].replace(',','')} DROP FOREIGN KEY {FK[FK.index('CONSTRAINT')+1]};""")
            conn.commit()
            print("Устанавливаю новый")
            cursor.execute(f"""ALTER TABLE {FK[0].replace(',','')} ADD CONSTRAINT {FK[FK.index('CONSTRAINT')+1]} 
            FOREIGN KEY {FK[FK.index('KEY')+1]} REFERENCES {FK[FK.index('REFERENCES')+1]}{FK[FK.index('REFERENCES')+2]}
             ON DELETE CASCADE ON UPDATE CASCADE;""")
            conn.commit()
            print("Успешно! Пробую еще раз")
            delete_by_name(name, mults, serie, conn)
    except ProgrammingError as e:
        print(e)


def drop(films=False, mults=False, subs=False, audio=False):
    """
    Удаление всего из базы данных
    :param films: Удалить все фильмы?
    :param mults: Удалить все мультфильмы?
    :param subs: Удалить все субтитры к мультфильмам?
    :param audio: Удалить все аудио к мультфильмам?
    """
    conn = connect(read_db_config())
    cursor = conn.cursor()
    try:
        if mults:
            rows = get_mults(conn)
            for row in rows:
                delete_by_name(row['title_name'], True, False, conn)
            cursor.execute("""ALTER TABLE mult_mult AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_series AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_subs AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_audio AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_mult_likes AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_mult_dislikes AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_mult_genre AUTO_INCREMENT=1;""")
            conn.commit()
        if films:
            rows = get_films(conn)
            for row in rows:
                delete_by_name(row['title_name'], False, False, conn)
            cursor.execute("""ALTER TABLE mult_film_genre AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_seriesfilms AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film_likes AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film_dislikes AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film_genre AUTO_INCREMENT=1;""")
            conn.commit()
        if subs:
            for row in get_subs(conn):
                cursor.execute(f"DELETE FROM mult_subs WHERE id = {row[1]};")
            cursor.execute("""ALTER TABLE mult_subs AUTO_INCREMENT=1;""")
            conn.commit()
        if audio:
            for row in get_audio(conn):
                cursor.execute(f"DELETE FROM mult_audio WHERE id = {row[1]};")
            cursor.execute("""ALTER TABLE mult_audio AUTO_INCREMENT=1;""")
            conn.commit()
        conn.close()
    except Error:
        conn.close()
        print("База данных не очищена!!!")
        exit()


def create(conn):
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS mults(
                               id INT NOT NULL AUTO_INCREMENT,
                               name TEXT NOT NULL,
                               episodes TEXT NOT NULL,
                               status TEXT NOT NULL,
                               description TEXT NOT NULL,
                               img TEXT NOT NULL,
                               genre TEXT NOT NULL,
                               unformated_name TEXT NOT NULL,
                               PRIMARY KEY (`id`)) ENGINE = InnoDB;""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS films(
                               idf INT NOT NULL AUTO_INCREMENT,
                               name TEXT,
                               episodes TEXT,
                               status TEXT,
                               description TEXT);""")
    conn.commit()


def connect(db):
    """
    Подключение к MySQL базе данных
    :param db: Данные для подключения к базе данных
    :type db: dict
    :return: Объект подключения к базе данных
    """
    try:
        conn = mysql.connector.connect(**db)
        if conn.is_connected():
            print('Connected to MySQL database')
        return conn
    except Error as e:
        print(e)


def export_mult(k):
    """
    Экспорт найденных мультфильмов в базу данных
    :param k: Словарь с мультфильмами на экспорт
    :type k: dict
    """
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        for item in k:
            print(item['series'][0])
            item['directory'] = item['directory'].replace("'", "\\'")
            item['directory'] = item['directory'].replace('"', '\\"')
            item['detail']['name'] = item['detail']['name'].replace("'", "\\'")
            insert = f"""INSERT INTO mult_mult (name, episodes, status, description, img_url, unformated_name, mult, isShown, create_date) VALUES ('{item['detail']['name']}', '{item['detail']['episodes']}', '{item['detail']['status']}', '{item['detail']['description']}', '{item['detail']['img']}', '{item['directory']}', True, {item['detail']['isShown']}, '{datetime.now()}')"""
            print(insert)
            cursor.execute(insert)
            conn.commit()
            genres = get_genres(conn)
            mult_genres = item["detail"]["genre"]
            if mult_genres:
                for genre in mult_genres:
                    if genre not in [g[1] for g in genres]:
                        add_genre(genre)
                        genres = get_genres(conn)
                    cursor.execute(f"""INSERT INTO mult_mult_genre (mult_id, genre_id) VALUES 
                                    ('{get_mult_id(item["directory"], cursor)[0]}', '{get_genre_id(genre, cursor)[0]}');""")
                    conn.commit()
            for serie in enumerate(item['series']):
                into_series = f"SELECT unformated_name, id FROM mult_mult WHERE name in " \
                              f"(SELECT '{item['detail']['name']}' " \
                              f"FROM mult_mult GROUP BY name HAVING COUNT(*) > 1) ORDER BY id;"
                print(into_series)
                cursor.execute(into_series)
                rows = cursor.fetchall()
                if len(rows) > 1:
                    for row in rows:
                        if serie[1]['directory'] == row[0]:
                            export_series(serie, row[1], conn)
                else:
                    into_series = f"SELECT unformated_name, id FROM mult_mult WHERE name='{item['detail']['name']}';"
                    cursor.execute(into_series)
                    rows = cursor.fetchall()
                    export_series(serie, rows[0][1], conn)
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        with open("error.txt", "a+") as f:
            print("Error: ", err)
            f.write(str(err)+"\n"+insert+"\n")


def export_series(item, id, conn=None):
    """
    Экспорт серий мультфильмов в базу данных
    :param item: Серия
    :param id: ID мультфильма
    :type id: int
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    :return:
    """
    try:
        if not conn:
            conn = connect(read_db_config())
            global_conn = False
        cursor = conn.cursor()
        item[1]['full_path'], item[1]['full_name'] = item[1]['full_path'].replace("'", "\\'"), item[1]['full_name'].replace("'", "\'")
        item[1]['full_path'], item[1]['full_name'] = item[1]['full_path'].replace('"', '\\"'), item[1]['full_name'].replace('"', '\"')
        insert = f"""INSERT INTO mult_series (name_serie, href, full_name, name_id) VALUES ("{item[1]['name']}", "{item[1]['full_path']}", "{item[1]['full_name']}", "{id}")"""
        print(insert)
        cursor.execute(insert)
        conn.commit()
        if "global_conn" in dir(): conn.close()
    except mysql.connector.errors.DatabaseError as err:
        with open("error.txt", "a+") as f:
            print("Error: ", err)
            f.write(str(err) + "\n" + insert + "\n")


def export_sub_audio(items, type):
    """
    Экспорт субтитров или аудио
    :param items: Субтитры/аудио
    :param type: тип audio/subs
    :type type: str
    :return:
    """
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        for item in items:
            into_subs = f"SELECT name_serie, id, name_id FROM mult_series WHERE name_serie = '{item['name']}';"
            cursor.execute(into_subs)
            rows = cursor.fetchall()
            if len(rows) > 0:
                insert = f"""INSERT INTO mult_{type} (name_{type.replace('subs', 'sub')}, autor, href, name_id, mult_id) VALUES ("{item['name']}", "{item['autor']}", "{item['full_path']}", {rows[0][1]}, {rows[0][2]});"""
                print(insert)
                cursor.execute(insert)
                conn.commit()
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_film(k):
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        for item in k:
            print(item['series'][0])
            #season = item['detail'][0]['season']-1
            description = item['detail']['description']
            description = str(description).replace('"', '\"')
            description = str(description).replace("'", "\'")
            directory = item['directory'].replace("'", "\'")
            directory = directory.replace('"', '\"')
            insert = f"""INSERT INTO mult_film (country, description, filmtype, img_url, name, seasons, unformated_name, year, mult, isShown, create_date) VALUES ("{item['detail']['country']}", "{description}", "{item['detail']['type']}", "{item['detail']['img']}", "{item['detail']['name'].replace('"', '')}", "{item['detail']['seasons']}", "{directory}", "{item['detail']['year']}", False, {item['detail']['isShown']}, '{datetime.now()}')"""
            print(insert)
            cursor.execute(insert)
            conn.commit()
            genres = get_genres(conn)
            film_genres = item['detail']['genre']
            if film_genres:
                for genre in film_genres:
                    if genre not in [g[1] for g in genres]:
                        add_genre(genre, conn)
                        genres = get_genres(conn)
                    cursor.execute(f"""INSERT INTO mult_film_genre (film_id, genre_id) VALUES 
                                    ("{get_film_id(directory, cursor)[0]}", "{get_genre_id(genre, cursor)[0]}");""")
                    conn.commit()
            for serie in item['series']:
                into_series = f"""SELECT "{directory}", id FROM mult_film WHERE unformated_name="{directory}";"""
                print(into_series)
                cursor.execute(into_series)
                rows = cursor.fetchall()
                for row in rows:
                    print(f"{row}")
                export_series_film(serie, rows[0][1], conn)
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_series_film(item, id, conn):
    """
    Экспорт серий фильмов в базу данных
    :param item: Серия
    :param id: ID фильма
    :param conn: Подключение к базе
    :type conn: MySQLConnection
    """
    try:
        if not conn:
            conn = connect(read_db_config())
            global_conn = False
        cursor = conn.cursor()
        insert = f"""INSERT INTO mult_seriesfilms (name_serie, href, full_name, name_id) VALUES ("{item['name']}", "{item['full_path']}", "{item['full_name']}", "{id}")"""
        print(insert)
        cursor.execute(insert)
        conn.commit()
        if "global_conn" in dir(): conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


#export_mult([{'name': 'Доктор Стоун',
#             'directory': 'Доктор Стоун S01',
#             'series': [{'name': 'Dr  Stone - серия 07 - Убежие, которому 100 миллионов лет',
#                        'full_name': '[AniPlague] Dr. Stone - серия 07 - Убежие, которому 100 миллионов лет.mkv'},
#                        {'name': 'Dr  Stone - серия 16 - История, которой несколько тысяч лет',
#                         'full_name':'[AniPlague] Dr. Stone - серия 16 - История, которой несколько тысяч лет.mkv'}],
#             'detail': shiki_parcer.parce(params={'search': 'Доктор Стоун'})},])