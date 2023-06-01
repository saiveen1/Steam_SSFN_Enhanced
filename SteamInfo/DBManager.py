import datetime
import json
import sqlite3


class DBManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_table(self):
        self.connect()
        try:
            self.cursor.execute(
                '''
                CREATE TABLE accounts (
                  id INTEGER PRIMARY KEY,
                  remark TEXT,
                  username TEXT UNIQUE,
                  password TEXT,
                  ssfn TEXT,
                  steamid TEXT,
                  sale_info TEXT,
                  CommunityBanned BOOLEAN,
                  VACBanned BOOLEAN,
                  NumberOfVACBans INTEGER,
                  DaysSinceLastBan INTEGER,
                  NumberOfGameBans INTEGER,
                  EconomyBan TEXT,
                  LastBanTime TEXT,
                  game_count INTEGER,
                  games TEXT,
                  cs_total INTEGER,
                  cs_2week INTEGER,
                  pubg_total INTEGER,
                  pubg_2week INTEGER
                )
                '''
            )
        finally:
            self.disconnect()

    def insert_data(self, table, data):
        self.connect()
        if 'games' in data:
            games_data = json.dumps(data['games'])
            data['games'] = games_data

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['last_api_check_time'] = current_time

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        self.cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
        self.connection.commit()
        self.disconnect()

    def select_data(self, table_name, condition=None):
        self.connect()
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.disconnect()
        return result


if __name__ == '__main__':
    db = DBManager("../accounts.db")
    username = "725mcyy397"
    t = db.select_data("accounts", f'''username="{username}"''')
    print(t)
    t = db.select_data("accounts", f'''username="123"''')
    print(len(t))
    db.disconnect()