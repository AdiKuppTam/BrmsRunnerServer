import os

from pymongo import MongoClient

from constants import EnvironmentVariables, DBTables


class DataHandler:
    def __init__(self):
        conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
        self.client = MongoClient(conn_str)
        self.db = self.client.test
