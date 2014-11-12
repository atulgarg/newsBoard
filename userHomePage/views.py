from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django import forms
import json
import operator
import logging

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
    for u in loggedUser:
        logging.info("user logged in is : " + u._id)
        keys = u.categories.keys()
        totalCount = u.total
        for key in keys:
            data = u.categories[key]
            if (data[0] > 0):
                preferredSections[key] = data[0]
        #sorting the dictionary in descending order based on the number of articles read in each section
        sortedSections = sorted(preferredSections.items(), key=operator.itemgetter(1), reverse=True)

        #looping through sections and print the articles from db in users order of preference
        for sectionData in sortedSections :
            noOfArticles = sectionData[1]*30/totalCount
            articlePercent = sectionData[1]*100/totalCount
            print noOfArticles
            for article in articles.objects(sectionId=sectionData[0])[:noOfArticles]:
                #passing sectionId only to the first article of each section
                if( lastSection != article.sectionId) :
                    articleData = [article._id, article.webTitle, article.thumbNail, article.sectionId, articlePercent]
                    lastSection = article.sectionId
                else :
                    articleData = [article._id, article.webTitle, article.thumbNail]

                articleList.append(articleData)



    return render(request, 'news.html', {'loginId': loginId, 'user': loggedUser, 'articleList': articleList})





