import os

from pymongo import MongoClient

from constants import EnvironmentVariables, DBTables


class DataHandler:
    def __init__(self):
        conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
        self._client = MongoClient(conn_str)
        self._db = self.client.test

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataHandler, cls).__new__(cls)
        return cls.instance

    def find_user_by_email(self, email):
        user = self.db[DBTables.Users]
        return user.find_one({"email": email})