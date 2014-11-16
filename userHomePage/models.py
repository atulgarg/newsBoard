from django.db import models

# Create your models here.
from mongoengine import *


class users(Document):
	_id = StringField(primary_key=True)
	total = IntField()
	categories = DictField()


class articles(Document):

    body = StringField()
    sectionId =  StringField()
    predictedSectionId = StringField()
    webTitle =  StringField()
    webUrl =  StringField()
    date =  DateTimeField()
    _id =  StringField(primary_key=True)
    thumbNail =  StringField()


    meta = {
        'indexes' : ['id' ,'predictedSectionId', 'date' ],
        'ordering' : ['+date']
    }
