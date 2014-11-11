from django.db import models

# Create your models here.
from mongoengine import *


class users(Document):
	_id = StringField(primary_key=True)
	total = StringField()
	categories = DictField()


class articles(Document):

    body = StringField()
    sectionId =  StringField()
    predictedSectionId = StringField()
    webTitle =  StringField()
    webUrl =  StringField()
    date =  StringField()
    _id =  StringField(primary_key=True)
    thumbNail =  StringField()
