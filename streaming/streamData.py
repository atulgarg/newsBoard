'''
Created on Nov 24, 2014

@author: Anil
'''
import time
import getdataNew
import hello_analytics_api_v3
from datetime import date
import os
import json
from sklearn.externals import joblib
from pymongo import MongoClient
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
#Tokenizer
#categories = dict([(4,'fashion'),(15,'travel'),(2,'education'),(12,'science'),(9,'money'),(3,'environment'),(14,'technology'),(7,'lifeandstyle'),(11,'politics'),(5,'film'),(0,'books'),(1,'business'),(10,'music'),(8,'media'),(6,'football'),(16,'world'),(13,'sport')])
categories = dict([(0,'art.artanddesign'),(1,'art.books'),(2,'art.books.nintendo-100-classic-book-collection'),(3,'art.music'),(4,'art.stage'),(5,'art.tv-and-radio'),(6,'business'),(7,'commentisfree'),(8,'crosswords'),(9,'culture'),(10,'education'),(11,'environment'),(12,'fashion'),(13,'film'),(14,'global'),(15,'global-development'),(16,'law'),(17,'lifeandstyle'),(18,'media'),(19,'money'),(20,'politics'),(21,'science'),(22,'society'),(23,'sport'),(24,'sport.cricket'),(25,'sport.football'),(26,'sport.formula'),(27,'sport.golf'),(28,'sport.rugby'),(29,'sport.tennis'),(30,'sustainable-business'),(31,'sustainable-business.fairtrade-partner-zone'),(32,'technology'),(33,'theguardian'),(34,'theobserver'),(35,'travel'),(36,'travel.america'),(37,'travel.england'),(38,'travel.france'),(39,'travel.hongkong'),(40,'travel.ireland'),(41,'travel.switzerland'),(42,'uk-news'),(43,'us-news'),(44,'world'),(45,'world.afghanistan'),(46,'world.australia'),(47,'world.china'),(48,'world.india'),(49,'world.israel'),(50,'world.pakistan'),(51,'world.russia')])

class LemmaTokenizer(object):
        def __init__(self):
                self.wnl = WordNetLemmatizer()
        def __call__(self, doc):
                return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

datadir='../jsonData'
print 'Test Files loaded'
client=MongoClient()
#db_name newsboard
db = client.newsBoard
#table name articles
articles = db.articles
#load data from classifier dump
text_clf = joblib.load('classifier_model.pkl')
print text_clf
wnl = WordNetLemmatizer()
stopset = set(stopwords.words('english'))

def pushData():
    for filename in os.listdir(datadir):
        try:
            filename = '../jsonData/' + filename
            with open(filename, 'r') as file_json:
                data = file_json.read().decode("utf-8")
                jsonData = json.loads(data)
                file_json.close()
                index = text_clf.predict([jsonData[0]['body']])
                index = index.tolist()[0] 
                #print index
                #print categories[index]
                jsonData[0]['predictedSectionId'] = categories[index]
                jsonData[0]['_id'] = jsonData[0]['id']
                del jsonData[0]['id']
                articles.insert(jsonData)
        except:
            print 'sectionID not found'

def fetchCurrentData():
    getdataNew.fetchData()
    print 'getdata done'
    pushData()
    os.system('java -Dtype=application/json -Durl="http://localhost:8983/solr/collection1/update" -jar /mnt/instance-data/solr-4.10.2/example/exampledocs/post.jar ../jsonData/*.json')
    os.system("rm -rf ../jsonData/*")
    hello_analytics_api_v3.main()
    print 'one cycle done'

while True:
    t1 = time.time()
    print 'calling fetch data'
    fetchCurrentData()
    t2 = time.time()
    time.sleep(86400 - (t2 -t1))

