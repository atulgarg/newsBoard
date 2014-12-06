from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django import forms
import json
import operator
import logging
from helper import *

from userHomePage.models import users, articles
import mongoengine


def home(request):
    now = datetime.datetime.now()
    return render(request, 'home.html', {'current_date': now})


class LoginForm(forms.Form):
    loginId = forms.CharField(label="loginId", max_length="100")


def news(request):
    # if request.method == 'POST':
    #	form = LoginForm(request.POST)
    loginId = request.POST.get('loginId', '')
    loggedUser = users.objects(_id=loginId)

    #userData = json.dumps(loggedUser)
    articleList = []
    lastSection = None
    preferredSections = {}
    preferredSubSections = {}
    for u in loggedUser:
        logging.info("user logged in is : " + u._id)
        keys = u.categories.keys()
        totalCount = u.total
        for key in keys:
            data = u.categories[key]
	    # If category has subsection it will be a dictionary
	    # If data is dictionary then  check for value to be greater than 0 in the total field
	    if isinstance(data, dict) :
		if (data['total'][0] > 0) :
			# If total is greater than 0, take the count of each subsection
			# If subsection count total does not exhaust the entire total then
			# remaining articles will come from the section 
			subSectionTotal = 0
			subSectionMap = {}
			for subSection in data :
				# We do not want to add key for 'total'
				if 'total' not in subSection  :
					subSectionMap[key + "." + subSection] = data[subSection][0]
					subSectionTotal += data[subSection][0]
			preferredSubSections[key] = subSectionMap
			print "subSectionTotal for " + key + " "  + str(subSectionMap.items())
		#	if (data['total'][0] - subSectionTotal > 0) :
			preferredSections[key] = data['total'][0]
	    else:
            	if (data[0] > 0):
                	preferredSections[key] = data[0]

	print preferredSections.items()	
        #sorting the dictionary in descending order based on the number of articles read in each section
        # Below line returns a list of list with each list representing key value pairs and sorting is based on value (descending)
        sortedSections = sorted(preferredSections.items(), key=operator.itemgetter(1), reverse=True)
	print sortedSections
        #looping through sections and print the articles from db in users order of preference
        for sectionData in sortedSections :
            noOfArticles = sectionData[1]*50/totalCount
            articlePercent = sectionData[1]*100/totalCount
	    predictedSection = sectionData[0]
	    if sectionData[0] in preferredSubSections.keys() :
		for subSectionData in preferredSubSections[sectionData[0]].items() :
			noOfArticles = noOfArticles*subSectionData[1]*100/sectionData[1]
			predictedSection = subSectionData[0]
            		print predictedSection + "  " + str(noOfArticles)
            		for article in articles.objects(predictedSectionId=predictedSection)[:noOfArticles]:
                	#passing sectionId only to the first article of each section
               			if( lastSection != article.predictedSectionId) :
                    			articleData = [article._id, article.webTitle, article.thumbNail,article.predictedSectionId, articlePercent]
                    			lastSection = article.predictedSectionId
               			else :
                    			articleData = [article._id, article.webTitle, article.thumbNail]
                			#  print article.date

               			articleList.append(articleData)
	    else :
			for article in articles.objects(predictedSectionId=predictedSection)[:noOfArticles]:
                        #passing sectionId only to the first article of each section
                        	if( lastSection != article.predictedSectionId) :
                        		articleData = [article._id, article.webTitle, article.thumbNail,article.predictedSectionId, articlePercent]
                        		lastSection = article.predictedSectionId
                        	else :  
                                	articleData = [article._id, article.webTitle, article.thumbNail]
                        		#  print article.date

            			articleList.append(articleData)

    return render(request, 'news.html', {'loginId': loginId, 'user': loggedUser, 'articleList': articleList, 'google_analytics_var1': ('user', loginId)})



def article(request):

       idAndUser =  request.path.split('&')
       print idAndUser
	
       articleData = []
       _id = None
       section = None
       for article in articles.objects(_id=idAndUser[1]) :
             articleData = [article.webTitle, article.body, article.thumbNail]
             _id = article._id
             section = article.sectionId

       updateUserProfile(idAndUser[2], section)
       similarArticlesData = None
      # similarArticlesData = getDataFromSolr(_id)

       return render(request, 'article.html', {'articleData' : articleData, 'similarArticlesData' : similarArticlesData,'loginId' : idAndUser[2]  })





