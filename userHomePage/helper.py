from userHomePage.models import users, articles
from urllib2 import *
import mongoengine
import simplejson
import logging


def updateUserProfile(loginId, section) :

  #can also use this line to update values
  #users.objects(_id=loginId).update_one(inc__total =1)

  UPDATE_FACTOR = 1

  for user in  users.objects(_id=loginId) :
    # Checking if the section has a subcategory
    if "." in section :
      section, subsection = section.split('.')
      user.categories[section][subsection][0] = user.categories[section][subsection][0] + UPDATE_FACTOR
      user.categories[section]['total'][0] = user.categories[section]['total'][0] + UPDATE_FACTOR
    else :
     # Even if the section does not have a "." it might be a section with subsection and this will have total field
        if 'total' in user.categories[section].keys() :
            user.categories[section]['total'][0] = user.categories[section]['total'][0] + UPDATE_FACTOR
        else :
            user.categories[section][0] = user.categories[section][0] + UPDATE_FACTOR
    user.total = user.total + UPDATE_FACTOR
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


