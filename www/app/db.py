from mongoengine import Document, StringField, BooleanField, EmailField, DateTimeField, IntField


class User(Document):
    meta = {'collection': "users"}

    id = StringField(primary_key=True, min_length=4)
    password = StringField(required=True, default="")

    # true - male, false - female
    # gender = BooleanField(required=True, default=True)
    first_name = StringField(required=True, default="")
    last_name = StringField(required=True, default="")
    # email = EmailField(required=True)

    address = StringField(required=True, default="")
    postal_code = StringField(required=True, default="")
    city = StringField(required=True, default="")
    language = StringField(required=True, default="")
    country = StringField(required=True, default="")


class Admin(Document):
    _id = StringField(required=True)
    password = StringField(required=True)