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
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db


def drop():
    conn = connect(read_db_config())
    cursor = conn.cursor()
    try:
        cursor.execute("""DROP TABLE mults;""")
        conn.commit()
        cursor.execute("""DROP TABLE films;""")
        conn.commit()
        create(conn)
        conn.close()
    except Error:
        print(Error)



def create(conn):
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS mults(
                               idm INT NOT NULL AUTO_INCREMENT,
                               name TEXT NOT NULL,
                               episodes TEXT NOT NULL,
                               status TEXT NOT NULL,
                               description TEXT NOT NULL,
                               PRIMARY KEY (`idm`)) ENGINE = InnoDB;""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS films(
                                           idf INT PRIMARY KEY,
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
        y = 1
        insert = f"INSERT INTO mults(name, episodes, status, description) VALUES ('{k['name']}', '{k['episodes']}', '{k['status']}', '{k['description']}')"
        print(insert)
        cursor.execute(insert)
        conn.commit()
        y += 1
        conn.close()
    except mysql.connector.errors.DatabaseError as err:
        print("Error: ", err)


