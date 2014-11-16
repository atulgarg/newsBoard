from userHomePage.models import users, articles
from urllib2 import *
import mongoengine
import simplejson
import logging


def updateUserProfile(loginId, section) :

  #can also use this line to update values
  #users.objects(_id=loginId).update_one(inc__total =1)

  for user in  users.objects(_id=loginId) :
    user.categories[section][0] = user.categories[section][0] + 1
    user.total = user.total + 1
    logging.info('Article count for section ' + section + 'is ' + str(user.categories[section][0]))
    logging.info('Total count is ' + str(user.total))
    user.save()



def getDataFromSolr(id):

    print id

    connstring = 'http://54.148.69.86:8983/solr/collection1/similararticles?q=id:'+ id +'&fl=id,webTitle,thumbNail&wt=json'
    connection = urlopen(connstring)
    response = simplejson.load(connection)
    similarArticles = []
    for document in response['response']['docs']:
            similarArticles.append([document['id'], document['webTitle'], document['thumbNail'][0]])

    return similarArticles


