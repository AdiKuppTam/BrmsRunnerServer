from mongoengine import Document
from mongoengine import DateTimeField, StringField, ListField, EmailField


class User(Document):
    email = EmailField(required=True, unique=True)
    name = StringField(max_length=60)
    experiments = ListField()
    last_visit = DateTimeField()
    creation_time = DateTimeField()

    def __unicode__(self):
        return self.email

    def __repr__(self):
        return self.email

    def __str__(self):
        return self.name
