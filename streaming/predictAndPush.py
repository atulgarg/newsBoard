import json
import os
from sklearn.externals import joblib
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
#Tokenizer
categories = dict([(4,'fashion'),(15,'travel'),(2,'education'),(12,'science'),(9,'money'),(3,'environment'),(14,'technology'),(7,'lifeandstyle'),(11,'politics'),(5,'film'),(0,'books'),(1,'business'),(10,'music'),(8,'media'),(6,'football'),(16,'world'),(13,'sport')])
class LemmaTokenizer(object):
        def __init__(self):
                self.wnl = WordNetLemmatizer()
        def __call__(self, doc):
                return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

rootdir='/home/atulgarg/newsboard/old/test_data25'
datadir='../jsonData'
#test_data = load_files(rootdir)
print 'Test Files loaded'
client=MongoClient()
#db_name newsboard
db = client.newsBoard
#table name articles
articles = db.articles
#load data from classifier dump
text_clf = joblib.load('classifier_model.pkl')
print text_clf
print 'dump loaded'
wnl = WordNetLemmatizer()
stopset = set(stopwords.words('english'))
def pushData():
    for filename in os.listdir(datadir):
        try:
            with open(f, 'r') as file_json:
                data = file_json.read().decode("utf-8")
                jsonData = json.loads(data)
                file_json.close()
                index = text_clf.predict([jsonData[0]['body']])
                jsonData[0]['predictedSectionId'] = categories[index]
                jsonData[0]['_id'] = jsonData[0]['id']
                del jsonData[0]['id']
                articles.insert(jsonData)
        except (KeyError, ValueError):
            print 'sectionID not found'
            
            
