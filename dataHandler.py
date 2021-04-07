import os

from pymongo import MongoClient

from constants import EnvironmentVariables, DBTables


class DataHandler:
    def __init__(self):
        conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
        self._client = MongoClient(conn_str)
        self._db = self._client.test

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataHandler, cls).__new__(cls)
        return cls.instance

    def find_user_by_email(self, email):
        user = self._db[DBTables.Users]
        return user.find_one({"email": email})

    def find_user_by_email_and_password(self, email, password):
        user = self._db[DBTables.Users]
        return user.find_one({"email": email, "password": password})

    def create_new_user(self, user_info):
        user = self._db[DBTables.Users]
        user.insert_one(user_info)
