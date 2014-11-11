from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django import forms
import json

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
    for u in loggedUser:
        keys = u.categories.keys()
        for key in keys:
            data = u.categories[key]
            if (data[0] > 5):
                print key
                for article in articles.objects(sectionId=key)[:2]:
                    #passing sectionId only to the first article of each section
                    if( lastSection != article.sectionId) :
                        articleData = [article._id, article.webTitle, article.thumbNail, article.sectionId]
                        lastSection = article.sectionId
                    else :
                        articleData = [article._id, article.webTitle, article.thumbNail]

                    articleList.append(articleData)


    return render(request, 'news.html', {'loginId': loginId, 'user': loggedUser, 'articleList': articleList})





