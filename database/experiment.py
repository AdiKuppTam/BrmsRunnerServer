from .db import db


class Experiment(db.Document):
    timeline = db.EmailField(required=True, unique=True)
    uid = db.StringField(required=True, min_length=6)