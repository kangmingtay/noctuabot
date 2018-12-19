import urllib.parse as urlparse
import os
import psycopg2

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

# todo reset the database
# todo refactor the names
# Used to setup and store user information: id, owner number, name.
# Ensures that the name of the owner is unique
class userdb:
    def __init__(self):
        self.connection = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cur = self.connection.cursor()

    def setup(self):
        # todo what happens if the user name is non-unique?
        tblstmt = "CREATE TABLE IF NOT EXISTS users (id serial, owner integer, name varchar, CONSTRAINT owner_name UNIQUE (owner, name));"
        self.cur.execute(tblstmt)
        self.connection.commit()

    def add_user(self, owner, name):
        stmt = "INSERT INTO users (owner, name) VALUES (%s, %s) ON CONFLICT (owner,name) DO NOTHING"
        args = (owner, name)
        self.cur.execute(stmt, args)
        self.connection.commit()


class onodb:
    def __init__(self):
        self.connection = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cur = self.connection.cursor()

    # todo need to reset this
    # Creates a postgresql table if it does not exist.
    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS ONO (id serial, four varchar, owner integer, name varchar, registered varchar);"
        self.cur.execute(tblstmt)
        self.connection.commit()

    # def start(self, four):
    #     stmt = "INSERT INTO ONO (four, owner, name, registered) VALUES (%s, %s, %s, %s)"
    #     args = (four, 0, "-", "no")
    #     self.cur.execute(stmt, args)
    #     self.connection.commit()

    # rename variables
    # Item[0] = serial number
    # Item[1] = unique identifier (game_id)
    # Item[2] = user chat_id
    # Item[3] = name on telegram
    # Item[4] = isRegistered todo change to boolean
    def register(self, four, owner, name):
        stmt = "DELETE FROM ONO WHERE four = %s"
        args = (four, )
        self.cur.execute(stmt, args)
        self.connection.commit()
        stmt = "INSERT INTO ONO (four, owner, name, registered) VALUES (%s, %s, %s, %s)"
        args = (four, owner, name, "yes")
        self.cur.execute(stmt, args)
        self.connection.commit()

    # def reset(self, four):
    #     stmt = "DELETE FROM ONO WHERE four = %s"
    #     args = (four, )
    #     self.cur.execute(stmt, args)
    #     self.connection.commit()
    #     stmt = "INSERT INTO ONO (four, owner, name, registered) VALUES (%s, %s, %s, %s)"
    #     args = (four, 0, "-", "no")
    #     self.cur.execute(stmt, args)
    #     self.connection.commit()

    # Retrieves all database entries, each entry contains 4 values
    def get_four(self):
        stmt = "SELECT * FROM ONO"
        try:
            self.cur.execute(stmt)
            return self.cur
        except:
            print("Failure")
            return []

    # Retrieves the 4 values for an entry which matches a user_id
    def get_user_record_from_user_chat_id(self, owner):
        stmt = "SELECT * FROM ONO WHERE owner = %s"
        args = (owner, )
        try:
            self.cur.execute(stmt, args)
            return self.cur
        except:
            print("Failure")
            return []

    # Retrieves a User's chat id from its unique 8-character alphanumeric game identifier
    def get_user_record_from_game_id(self, game_id):
        stmt = "SELECT * FROM ONO WHERE four = %s"
        args = (game_id,)
        try:
            self.cur.execute(stmt, args)
            return self.cur
        except:
            print("Failure")
            return []

    # def clear(self):
    #     stmt = "DELETE FROM ONO;"
    #     self.cur.execute(stmt)
    #     self.connection.commit()


