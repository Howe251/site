import mysql.connector
from mysql.connector import Error
from configparser import ConfigParser
import shiki_parcer


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


def get_mults():
    animes = []
    conn = connect(read_db_config())
    cursor = conn.cursor()
    cursor.execute("SELECT unformated_name, id FROM mult_mult")  # Список всех тайтлов
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute(f"SELECT href FROM `mult_series` "
                       f"WHERE name_id = (SELECT id FROM mult_mult WHERE id = {row[1]})")  # Спиоск всех серий с id
        series = cursor.fetchall()
        animes.append({'title_name': row[0],
                       'serie_name': series,
                       'id': row[1]})
    conn.close()
    return animes


def get_films():
    films = []
    conn = connect(read_db_config())
    cursor = conn.cursor()
    cursor.execute("SELECT unformated_name, id FROM mult_film")  # Список всех тайтлов
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute(f"SELECT href FROM `mult_seriesfilms` "
                       f"WHERE name_id = (SELECT id FROM mult_film WHERE id = {row[1]})")  # Спиоск всех серий с id
        series = cursor.fetchall()
        films.append({'title_name': row[0],
                       'serie_name': series,
                       'id': row[1]})
    conn.close()
    return films


def drop(films=False, mults=False):
    conn = connect(read_db_config())
    cursor = conn.cursor()
    try:
        if mults:
            rows = get_mults()
            cursor.execute("""DELETE FROM mults;""")
            conn.commit()
            cursor.execute("""ALTER TABLE mults AUTO_INCREMENT=1;""")
            conn.commit()
            for row in rows:
                cursor.execute(f"DELETE FROM mult_mult WHERE id = {row['id']};")
            conn.commit()
            cursor.execute("""ALTER TABLE mult_mult AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_series AUTO_INCREMENT=1;""")
            conn.commit()
            conn.close()
        elif films:
            rows = get_films()
            for row in rows:
                cursor.execute(f"DELETE FROM mult_film WHERE id = {row['id']};")
            conn.commit()
            cursor.execute("""ALTER TABLE mult_seriesfilms AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film AUTO_INCREMENT=1;""")
            conn.commit()
            conn.close()
    except Error:
        print(Error)


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
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(**db)
        if conn.is_connected():
            print('Connected to MySQL database')
        return conn
    except Error as e:
        print(e)


def export_mult(k):
    try:
        for item in k:
            conn = connect(read_db_config())
            cursor = conn.cursor()
            print(item['series'][0])
            insert = f"INSERT INTO mult_mult (name, episodes, status, description, img, genre, unformated_name) VALUES ('{item['detail']['name']}', '{item['detail']['episodes']}', '{item['detail']['status']}', '{item['detail']['description']}', '{item['detail']['img']}', '{item['detail']['genre']}', '{item['directory']}')"
            print(insert)
            cursor.execute(insert)
            conn.commit()
            for serie in enumerate(item['series']):
                into_series = f"SELECT '{item['detail']['name']}', id FROM mult_mult WHERE name='{item['detail']['name']}';"
                print(into_series)
                cursor.execute(into_series)
                rows = cursor.fetchall()
                for row in rows:
                    print(f"{row}")
                export_series(serie, rows[0][1])
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_series(item, id):
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        insert = f"""INSERT INTO mult_series (name_serie, href, name_id) VALUES ("{item[1]['name']}", "{item[1]['full_name']}", "{id}")"""
        print(insert)
        cursor.execute(insert)
        conn.commit()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_film(k):
    try:
        for item in k:
            conn = connect(read_db_config())
            cursor = conn.cursor()
            print(item['series'][0])
            season = item['detail'][0]['season']-1
            description = item['detail'][0]['description'][season]
            description = str(description).replace('"', '')
            insert = f"""INSERT INTO mult_film (country, description, filmtype, img, name, seasons, unformated_name, year) VALUES ("{item['detail'][0]['country']}", "{description}", "{item['detail'][0]['type']}", "{item['detail'][0]['img']}", "{item['detail'][0]['name'].replace('"', '')}", "{item['detail'][0]['seasons']}", "{item['directory']}", "{item['detail'][0]['year']}")"""
            print(insert)
            cursor.execute(insert)
            conn.commit()
            for serie in item['series']:
                into_series = f"""SELECT "{item['detail'][0]['name'].replace('"', '')}", id FROM mult_film WHERE name="{item['detail'][0]['name'].replace('"', '')}";"""
                print(into_series)
                cursor.execute(into_series)
                rows = cursor.fetchall()
                for row in rows:
                    print(f"{row}")
                export_series_film(serie, rows[0][1])
            conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_series_film(item, id):
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        insert = f"""INSERT INTO mult_seriesfilms (name_serie, href, name_id) VALUES ("{item['name']}", "{item['full_name']}", "{id}")"""
        print(insert)
        cursor.execute(insert)
        conn.commit()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


#export_mult([{'name': 'Доктор Стоун',
#             'directory': 'Доктор Стоун S01',
#             'series': [{'name': 'Dr  Stone - серия 07 - Убежие, которому 100 миллионов лет',
#                        'full_name': '[AniPlague] Dr. Stone - серия 07 - Убежие, которому 100 миллионов лет.mkv'},
#                        {'name': 'Dr  Stone - серия 16 - История, которой несколько тысяч лет',
#                         'full_name':'[AniPlague] Dr. Stone - серия 16 - История, которой несколько тысяч лет.mkv'}],
#             'detail': shiki_parcer.parce(params={'search': 'Доктор Стоун'})},])