import sqlite3


class PolDB(object):
    def __init__(self, filename: str):
        """
        This is the source wikidb to do more specific actions on
        Generated by wikiparse.py
        :param filename: Filename for your db
        """
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS politicians (
          url text,
          name text,
          full_text text,
          party text)""")
        self.conn.commit()
        self.cur = self.conn.cursor()
        self.pending = 0  # Counter for when to commit
        self.column_names = ['url', 'name', 'full_text', 'party']

    def commit(self):
        self.conn.commit()


    def insert(self, url: str, name: str, full_text: str, party: str):
        """
        Compresses article and inserts values into db
        :param pageid: Unique identifier for every wiki article
        :param title: Title of wiki article
        :param categories: repr of list of categories
        :param article: Wiki article
        """

        self.conn.execute("""
          INSERT or IGNORE INTO politicians VALUES (?, ?, ?, ?);
        """, (url, name, full_text, party))
        self.commit()
    
    def __repr__(self):
      return '<SQLite DB (' +  self.filename + '): ' + ', '.join(self.column_names) + '>'



