# tweet_storage.py
import sqlite3

class TweetStorage:
    def __init__(self, db_name='tweets.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY,
                    content TEXT,
                    sentiment TEXT,
                    style TEXT,
                    engagement INTEGER
                )
            """)

    def store_tweet(self, tweet_data):
        with self.conn:
            self.conn.execute("""
                INSERT INTO tweets (content, sentiment, style, engagement) VALUES (?, ?, ?, ?)
            """, (tweet_data['content'], tweet_data['sentiment'], tweet_data['style'], tweet_data['engagement']))
