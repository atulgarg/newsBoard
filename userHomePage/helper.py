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
	
        if isinstance(user.categories[section], dict) :
	    user.categories[section]['total'][0] = user.categories[section]['total'][0] + UPDATE_FACTOR
        else :
            user.categories[section][0] = user.categories[section][0] + UPDATE_FACTOR
	    print "inside second else" + section
	    print user.categories[section][0]
    user.total = user.total + UPDATE_FACTOR
   # logging.info('Article count for section ' + section + 'is ' + str(user.categories[section][0]))
    logging.info('Total count is ' + str(user.total))
    user.save()



def getDataFromSolr(id):

    print id

    connstring = 'http://54.149.58.17:8983/solr/collection1/similararticles?q=id:'+ id +'&fl=id,webTitle,thumbNail&wt=json'
    connection = urlopen(connstring)
    response = simplejson.load(connection)
    #thumbDict = {'thumbNail':"http://demopcr.wpindeed.com/wp-content/plugins/pcr-listing-posts/image/no-thumbnail.png"}
    similarArticles = []
    try:
        if  response is None or 'response' not in response.keys()  or 'docs' not in response['response'].keys():
            return
    except:
        return
    for document in response['response']['docs']:
	    if 'thumbNail' in document.keys():
                similarArticles.append([document['id'], document['webTitle'], document['thumbNail'][0]])
	    else:
		similarArticles.append([document['id'], document['webTitle'], "http://demopcr.wpindeed.com/wp-content/plugins/pcr-listing-posts/image/no-thumbnail.pn"])
    return similarArticles


