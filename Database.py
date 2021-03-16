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


def drop():
    conn = connect(read_db_config())
    cursor = conn.cursor()
    try:
        cursor.execute("""DROP TABLE mults;""")
        conn.commit()
        #cursor.execute("""ALTER TABLE mults AUTO_INCREMENT=0;""")
        #conn.commit()
        cursor.execute("""DELETE FROM films;""")
        conn.commit()
        cursor.execute("""ALTER TABLE films AUTO_INCREMENT=0;""")
        conn.commit()
        create(conn)
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
        conn = connect(read_db_config())
        cursor = conn.cursor()
        for id, item in enumerate(k):
            print(id, k) # TODO Вписать сюда скрипт добавления серий в базу данных и разобраться с Дитя погоды
        print(k[0]['name'])
        insert = f"INSERT INTO mults (name, episodes, status, description, img, genre, unformated_name) VALUES ('{k[0]['detail']['name']}', '{k[0]['detail']['episodes']}', '{k[0]['detail']['status']}', '{k[0]['detail']['description']}', '{k[0]['detail']['img']}', '{k[0]['detail']['genre']}', '{k[0]['directory']}')"
        print(insert)
        cursor.execute(insert)
        conn.commit()
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


