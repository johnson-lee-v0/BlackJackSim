# DataCollection.py

import sqlite3

class DatabaseManager:
    def __init__(self, db_name="game_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS hands (
                    id INTEGER PRIMARY KEY,
                    game_id INTEGER,
                    player_cards TEXT,
                    dealer_cards TEXT,
                    advice TEXT,
                    action TEXT,
                    result TEXT,
                    FOREIGN KEY(game_id) REFERENCES games(id)
                );
            """)

    def insert_game(self):
        with self.conn:
            cur = self.conn.execute("INSERT INTO games DEFAULT VALUES;")
            return cur.lastrowid  # Return the ID of the created game

    def insert_hand(self, game_id, player_cards, dealer_cards, advice, action, result):
        with self.conn:
            cur = self.conn.execute("""
                INSERT INTO hands (game_id, player_cards, dealer_cards, advice, action, result)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (game_id, player_cards, dealer_cards, advice, action, result))
            return cur.lastrowid  # Return the ID of the created hand

    def close(self):
        self.conn.close()
