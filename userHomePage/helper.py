from userHomePage.models import users, articles
from urllib2 import *
import mongoengine
import simplejson


#def updateUserProfile(loginId, section) :

  #  users.objects(_id=loginId).update_one(inc__total =1)

   # users.objects(_id=loginId).update_one(inc__categories =1)




def getDataFromSolr(id):

    print id

    connstring = 'http://54.148.69.86:8983/solr/collection1/similararticles?q=id:'+ id +'&fl=id,webTitle,thumbNail&wt=json'
    connection = urlopen(connstring)
    response = simplejson.load(connection)
    similarArticles = []
    for document in response['response']['docs']:
            similarArticles.append([document['id'], document['webTitle'], document['thumbNail'][0]])

    return similarArticles


