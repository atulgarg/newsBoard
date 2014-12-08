from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django import forms
import json
import operator
import logging
import math
from helper import *

from userHomePage.models import users, articles
import mongoengine

def section(request):
    idAndsection =  request.path.split('&')
    loginId = idAndsection[2]
    section = idAndsection[1]
    if(section == "home"):
        return news(request)
    now = datetime.datetime.now()
    noOfArticles = 50
    articleList = []
    count = 0
    for article in articles.objects(predictedSectionId__startswith=section)[:noOfArticles]:
                #passing sectionId only to the first article of each section
        articleData = [article._id, article.webTitle, article.thumbNail,article.predictedSectionId]
	count = count + 1
        articleList.append(articleData)
    return render(request, 'section.html', {'loginId': loginId,'count': count, 'section': section, 'articleList': articleList, 'google_analytics_var1': ('user', loginId)})


def home(request):
    now = datetime.datetime.now()
    return render(request, 'home.html', {'current_date': now})


class LoginForm(forms.Form):
    loginId = forms.CharField(label="loginId", max_length="100")


def news(request):
	
    CLICK_FACTOR = 0.3
    TIME_FACTOR = 0.7
    # if request.method == 'POST':
    #	form = LoginForm(request.POST)
    loginId = request.POST.get('loginId', '')
    if not loginId:
	loginId = request.path.split('&')[2]

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
					subSectionMap[key + "." + subSection] = data[subSection][0]*CLICK_FACTOR + data[subSection][1]*TIME_FACTOR
					subSectionTotal += data[subSection][0]
			preferredSubSections[key] = subSectionMap
			print "subSectionTotal for " + key + " "  + str(subSectionMap.items())
		#	if (data['total'][0] - subSectionTotal > 0) :
			preferredSections[key] = data['total'][0]*CLICK_FACTOR + data['total'][1]*TIME_FACTOR
	    else:
            	if (data[0] > 0):
                	preferredSections[key] = data[0]*CLICK_FACTOR + data[1]*TIME_FACTOR 
	
	#All the percentages will be calculated over this total_value
	totalValue = u.total*CLICK_FACTOR + u.totalTime*TIME_FACTOR
	print "totalValue" + str(totalValue)	
	print preferredSections.items()	
        #sorting the dictionary in descending order based on the number of articles read in each section
        # Below line returns a list of list with each list representing key value pairs and sorting is based on value (descending)
        sortedSections = sorted(preferredSections.items(), key=operator.itemgetter(1), reverse=True)
	print sortedSections
        #looping through sections and print the articles from db in users order of preference
	#sectionData in the below for loop is a list of 2 values. First value is section Name, section value is weightage
        for sectionData in sortedSections :
            noOfArticlesPerSection = sectionData[1]*50/totalValue
	    print 'noOfArticlesPerSection' + sectionData[0] + '  ' + str(math.ceil(noOfArticlesPerSection))
	    predictedSection = sectionData[0]
	    sectionWeightageLeft = sectionData[1]
	    articlePercent = round(sectionData[1]*100/totalValue, 2)
	    if sectionData[0] in preferredSubSections.keys() :
		# Adding article details for section heading (for that which has subsectioins)
		articleList.append(['','','', '', str.upper(sectionData[0].encode('utf-8')), articlePercent])
		sortedSubSections = sorted(preferredSubSections[sectionData[0]].items(), key=operator.itemgetter(1), reverse=True)
		for subSectionData in sortedSubSections :
			print 'articleProduct' + str(noOfArticlesPerSection*subSectionData[1])
			noOfArticles = (noOfArticlesPerSection*subSectionData[1])/sectionData[1]
            		articlePercent = round(subSectionData[1]*100/totalValue, 2)
		        # subtracting subsection weight from total weight for a section
			sectionWeightageLeft =- subSectionData[1]
			predictedSection = subSectionData[0]
            		print predictedSection + "  " + str(math.ceil(noOfArticles))
			section, subsection = predictedSection.split(".")
            		for article in articles.objects(predictedSectionId=predictedSection)[:math.ceil(noOfArticles)]:
                	#passing sectionId only to the first article of each section
               			if( lastSection != article.predictedSectionId) :
                    			articleData = [article._id, article.webTitle, article.thumbNail,'subSection', subsection, articlePercent]
                    			lastSection = article.predictedSectionId
               			else :
                    			articleData = [article._id, article.webTitle, article.thumbNail,'subSection']
                			#  print article.date

               			articleList.append(articleData)
	    if sectionWeightageLeft > 0.0:
		        noOfArticlesPerSection = sectionWeightageLeft*50/totalValue
			print 'noOfArticles for categories without sub' + predictedSection + '  ' +  str(math.ceil(noOfArticlesPerSection))
            		articlePercent = round(sectionData[1]*100/totalValue, 2)
			for article in articles.objects(predictedSectionId=predictedSection)[:math.ceil(noOfArticlesPerSection)]:
                        #passing sectionId only to the first article of each section
                        	if( lastSection != article.predictedSectionId) :
                        		articleData = [article._id, article.webTitle, article.thumbNail, 'section',str.upper(article.predictedSectionId.encode('utf-8')), articlePercent]
                        		lastSection = article.predictedSectionId
                        	else :  
                                	articleData = [article._id, article.webTitle, article.thumbNail, 'section']
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
             articleData = [article.webTitle, article.body, article.thumbNail, article.predictedSectionId, article.expectedTime]
             _id = article._id
             section = article.sectionId

       updateUserProfile(idAndUser[2], section)
       similarArticlesData = None
       similarArticlesData = getDataFromSolr(_id)

       return render(request, 'article.html', {'articleData' : articleData, 'similarArticlesData' : similarArticlesData,'loginId' : idAndUser[2]  })





