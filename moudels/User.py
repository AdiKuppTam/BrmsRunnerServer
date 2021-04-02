from app import db


class User(db.Document):
    name = db.StringField()
    email = db.StringField()
