import mysql.connector
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


def get_subs():
    subs = []
    conn = connect(read_db_config())
    cursor = conn.cursor()
    cursor.execute("SELECT name_sub, id FROM mult_subs")  # Список всех субтитров
    subs = cursor.fetchall()
    return subs


def get_audio():
    conn = connect(read_db_config())
    cursor = conn.cursor()
    cursor.execute("SELECT name_audio, id FROM mult_audio")  # Список всех субтитров
    subs = cursor.fetchall()
    return subs


def get_films():
    films = []
    conn = connect(read_db_config())
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
    conn.close()
    return films


def drop(films=False, mults=False, subs=False, audio=False):
    conn = connect(read_db_config())
    cursor = conn.cursor()
    try:
        if mults:
            rows = get_mults()
            for row in rows:
                cursor.execute(f"DELETE FROM mult_mult WHERE id = {row['id']};")
            conn.commit()
            cursor.execute("""ALTER TABLE mult_mult AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_series AUTO_INCREMENT=1;""")
            conn.commit()
        if films:
            rows = get_films()
            for row in rows:
                cursor.execute(f"DELETE FROM mult_film WHERE id = {row['id']};")
            conn.commit()
            cursor.execute("""ALTER TABLE mult_seriesfilms AUTO_INCREMENT=1;""")
            cursor.execute("""ALTER TABLE mult_film AUTO_INCREMENT=1;""")
            conn.commit()
        if subs:
            for row in get_subs():
                cursor.execute(f"DELETE FROM mult_subs WHERE id = {row[1]};")
            cursor.execute("""ALTER TABLE mult_subs AUTO_INCREMENT=1;""")
        if audio:
            for row in get_audio():
                cursor.execute(f"DELETE FROM mult_audio WHERE id = {row[1]};")
            cursor.execute("""ALTER TABLE mult_audio AUTO_INCREMENT=1;""")
        conn.close()
    except Error:
        conn.close()
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
            item['directory'] = item['directory'].replace("'", "\\'")
            item['directory'] = item['directory'].replace('"', '\\"')
            item['detail']['name'] = item['detail']['name'].replace("'", "\\'")
            insert = f"""INSERT INTO mult_mult (name, episodes, status, description, img_url, genre, unformated_name, mult) VALUES ('{item['detail']['name']}', '{item['detail']['episodes']}', '{item['detail']['status']}', '{item['detail']['description']}', '{item['detail']['img']}', '{item['detail']['genre']}', '{item['directory']}', True)"""
            print(insert)
            cursor.execute(insert)
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
                            export_series(serie, row[1])
                else:
                    into_series = f"SELECT unformated_name, id FROM mult_mult WHERE name='{item['detail']['name']}';"
                    cursor.execute(into_series)
                    rows = cursor.fetchall()
                    export_series(serie, rows[0][1])
    except mysql.connector.errors.DatabaseError as err:
        with open("error.txt", "a+") as f:
            print("Error: ", err)
            f.write(str(err)+"\n"+insert+"\n")


def export_series(item, id):
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        item[1]['full_path'], item[1]['full_name'] = item[1]['full_path'].replace("'", "\\'"), item[1]['full_name'].replace("'", "\'")
        item[1]['full_path'], item[1]['full_name'] = item[1]['full_path'].replace('"', '\\"'), item[1]['full_name'].replace('"', '\"')
        insert = f"""INSERT INTO mult_series (name_serie, href, full_name, name_id) VALUES ("{item[1]['name']}", "{item[1]['full_path']}", "{item[1]['full_name']}", "{id}")"""
        print(insert)
        cursor.execute(insert)
        conn.commit()
    except mysql.connector.errors.DatabaseError as err:
        with open("error.txt", "a+") as f:
            print("Error: ", err)
            f.write(str(err) + "\n" + insert + "\n")


def export_sub_audio(items, type):
    try:
        conn = connect(read_db_config())
        cursor = conn.cursor()
        for item in items:
            into_subs = f"SELECT name_serie, id, name_id FROM mult_series WHERE name_serie = '{item['name']}';"
            cursor.execute(into_subs)
            rows = cursor.fetchall()
            if len(rows) > 0:
                if type == "subs":
                    insert = f"""INSERT INTO mult_subs (name_sub, autor, href, name_id, mult_id) VALUES ("{item['name']}", "{item['autor']}", "{item['full_path']}", {rows[0][1]}, {rows[0][2]});"""
                elif type == "audio":
                    insert = f"""INSERT INTO mult_audio (name_audio, autor, href, name_id, mult_id) VALUES ("{item['name']}", "{item['autor']}", "{item['full_path']}", {rows[0][1]}, {rows[0][2]});"""
                print(insert)
                cursor.execute(insert)
                conn.commit()
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


def export_film(k):
    try:
        for item in k:
            conn = connect(read_db_config())
            cursor = conn.cursor()
            print(item['series'][0])
            #season = item['detail'][0]['season']-1
            description = item['detail']['description']
            description = str(description).replace('"', '\\"')
            description = str(description).replace("'", "\\'")
            insert = f"""INSERT INTO mult_film (country, description, filmtype, img_url, name, seasons, unformated_name, year, mult) VALUES ("{item['detail']['country']}", "{description}", "{item['detail']['type']}", "{item['detail']['img']}", "{item['detail']['name'].replace('"', '')}", "{item['detail']['seasons']}", "{item['directory']}", "{item['detail']['year']}", False)"""
            print(insert)
            cursor.execute(insert)
            conn.commit()
            for serie in item['series']:
                into_series = f"""SELECT "{item['directory'].replace('"', '')}", id FROM mult_film WHERE unformated_name="{item['directory'].replace('"', '')}";"""
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
        insert = f"""INSERT INTO mult_seriesfilms (name_serie, href, full_name, name_id) VALUES ("{item['name']}", "{item['full_path']}", "{item['full_name']}", "{id}")"""
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