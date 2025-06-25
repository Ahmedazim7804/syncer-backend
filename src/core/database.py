from sqlmodel import create_engine, SQLModel
from sqlmodel import Session as SQLModelSession
from contextlib import contextmanager


class Database:
    def __init__(self, db_url: str):
        self._engine = create_engine(db_url, echo=True)

        self.create_db()

    def create_db(self):
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session(self):
        session = SQLModelSession(bind=self._engine, autocommit=False, autoflush=False)
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()


# class Database:

#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls):
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     cls._instance = super(Database, cls).__new__(cls)
#                     cls._instance.__init__()
#         return cls._instance

#     def __init__(self):
#         self.conn : sqlite3.Connection | None = None
#         self.cursor: sqlite3.Cursor | None = None

#         self.createDatabase()

#     def createDatabase(self):
#         conn = sqlite3.connect('database.db', check_same_thread=False)
#         self.conn = conn
#         self.cursor = conn.cursor()

#         import os
#         print(os.listdir("./"));

#         with open("db.sql") as fp:
#             self.cursor.executescript(fp.read())

#     def addRefreshToken(self, refresh_token: str, role: str):
#         self.cursor.execute("INSERT INTO RefreshTokens (refresh_token, role) VALUES (?, ?)", (refresh_token, role))
#         self.conn.commit()

#     def removeRefreshToken(self, refresh_token: str):
#         self.cursor.execute("DELETE FROM RefreshTokens WHERE refresh_token = ?", (refresh_token,))
#         self.conn.commit()

#     def verifyRefreshToken(self, refresh_token: str) -> bool:
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT * FROM RefreshTokens WHERE refresh_token = ?", (refresh_token,))
#         return cursor.fetchone() is not None

#     def addClipboard(self, role, content: str) -> bool:
#         try:
#             self.cursor.execute("INSERT INTO Clipboard ('from', content) VALUES (?, ?)", (role, content))
#             self.conn.commit()
#             return True
#         except:
#             return False

#     def get_db():
#         db = Database()
#         try:
#             yield db
#         finally:
#             db.conn.close()
