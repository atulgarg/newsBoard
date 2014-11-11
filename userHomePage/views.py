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
    for u in loggedUser:
        keys = u.categories.keys()
        for key in keys:
            data = u.categories[key]
            if (data[0] > 5):
                print key
                for article in articles.objects(sectionId=key)[:2]:
                    articleList.append(article._id)
                    print article._id


    return render(request, 'news.html', {'loginId': loginId, 'user': loggedUser, 'articleList': articleList})


