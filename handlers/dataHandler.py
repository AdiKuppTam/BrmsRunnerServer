import os

import pandas as pd
from pymongo import MongoClient

from constants import EnvironmentVariables, DBTables


class DataHandler:
    def __init__(self):
        conn_str = os.environ[EnvironmentVariables.CONNECTION_STRING]
        self._client = MongoClient(conn_str)
        self._db = self._client.RMS

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataHandler, cls).__new__(cls)
        return cls.instance

    def find_user_by_email(self, email):
        user = self._db[DBTables.Users]
        return user.find_one({"email": email})

    def find_user_by_email_and_password(self, email, password):
        users = self._db[DBTables.Users]
        return users.find_one({"email": email, "password": password})

    def get_experiments_by_user_id(self, uid):
        experiments = self._db[DBTables.Experiments]
        return experiments.find({}, {"uid": uid})

    def create_new_user(self, user_info):
        users = self._db[DBTables.Users]
        users.insert_one(user_info)

    def upload_experiment(self, experiment_details):
        experiments = self._db[DBTables.Experiments]
        experiments.insert_one(experiment_details)

    def upload_data(self, name, results):
        data_table = self._db[name]
        data_table.insert_one(results)

    def export_experiment(self, experiment_id):
        results = self._db[DBTables.Results]
        return pd.DataFrame(list(results.find({experiment_id: experiment_id})))

    def get_experiment_by_id(self, experiment_id):
        experiments = self._db[DBTables.Experiments]
        experiments.find_one({"experiment_id": experiment_id})
