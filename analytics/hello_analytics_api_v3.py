#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# import the Auth Helper class
import hello_analytics_api_v3_auth
import HTMLParser
import logging
from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from pymongo import MongoClient


def main(argv):
    # Step 1. Get an analytics service object.
    print "inside main"
    service = hello_analytics_api_v3_auth.initialize_service()
    print service
    try:
        # Step 2. Get the user's first profile ID.
        profile_id = get_first_profile_id(service)

        if profile_id:
            # Step 3. Query the Core Reporting API.
            results = get_results(service, profile_id)

            print profile_id
            # Step 4. Output the results.
            process_results(results)

    except TypeError, error:
        # Handle errors in constructing a query.
        print ('There was an error in constructing your query : %s' % error)

    except HttpError, error:
        # Handle API errors.
        print ('Arg, there was an API error : %s : %s' %
               (error.resp.status, error._get_reason()))

    except AccessTokenRefreshError:
        # Handle Auth errors.
        print ('The credentials have been revoked or expired, please re-run '
               'the application to re-authorize')


def get_first_profile_id(service):
    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account
        firstAccountId = accounts.get('items')[0].get('id')

        # Get a list of all the Web Properties for the first account
        webproperties = service.management().webproperties().list(accountId=firstAccountId).execute()

        if webproperties.get('items'):
            # Get the first Web Property ID
            firstWebpropertyId = webproperties.get('items')[0].get('id')

            # Get a list of all Views (Profiles) for the first Web Property of the first Account
            profiles = service.management().profiles().list(
                accountId=firstAccountId,
                webPropertyId=firstWebpropertyId).execute()

            if profiles.get('items'):
                # return the first View (Profile) ID
                return profiles.get('items')[0].get('id')

    return None


def get_results(service, profile_id):
    # Use the Analytics Service Object to query the Core Reporting API
    return service.data().ga().get(
        ids='ga:' + profile_id,
        dimensions='ga:eventCategory,ga:eventAction,ga:eventLabel',
        metrics='ga:totalEvents',
        start_date='2014-12-04',
        end_date='2014-12-05').execute()


def print_results(results):
    # Print data table.
    print results
    if results.get('rows', []):
        for row in results.get('rows'):
            output = []
            for cell in row:
                output.append('%30s' % cell)
            print ''.join(output)

    else:
        print 'No Rows Found'


def process_results(results):
    # used to removed special characters from the article name such as &#39(')
    parser = HTMLParser.HTMLParser()
    userDataMap = {}
    if results.get('rows', []):
        for row in results.get('rows'):
            # splitting the lable on ? and then on &s
            time, userReadData = row[2].split('?')
            time = time.strip()
            userReadData = parser.unescape(userReadData)
            if userReadData:
                try:
                    article = userReadData.split('&')[0].split('=')[1]
                    section = userReadData.split('&')[1].split('=')[1]
                    userId = userReadData.split('&')[2].split('=')[1].encode('utf-8')
                except (ValueError, IndexError) as e:
                    print "invalid label "  #+ row[2]
                    continue

            #Finding maximum time spent on each article and saving the corresponding time and section
            if userDataMap.get(userId, {}).has_key(article):
                oldData = userDataMap[userId][article]
                if (int(oldData[0]) < int(time)):
                    userDataMap[userId][article] = [int(time), section]
            else:
                userDataMap.setdefault(userId, {})[article] = [int(time), section]

        print userDataMap.items()
    else:
        print 'No Rows Found'

    createUserProfileUpdateData(userDataMap)


def createUserProfileUpdateData(userDataMap):
    # clubbing time for each section for each user
    userProfileMap = {}
    for user in userDataMap:
        for article in userDataMap[user]:
            time, section = userDataMap[user][article]
            if userProfileMap.get(user, {}).has_key(section):
                userProfileMap[user][section] = userProfileMap[user][section] + time
            else:
                userProfileMap.setdefault(user, {})[section] = time
    logging.info(userProfileMap.items())

    updateUserDatabase(userProfileMap)


def updateUserDatabase(userProfileMap):
    client = MongoClient()
    db = client.newsBoard
    users = db.users
    for user in userProfileMap:
        u = users.find_one({"_id": user})
        totalTime = 0
        for section in userProfileMap[user]:
            clicks, time = u['categories'][section]
            print "clicks " + str(clicks) + "time " + str(time)
            users.update({'_id': user},
                         {'$set': {'categories.' + section: [clicks, time + userProfileMap[user][section]]}})
            totalTime = totalTime + userProfileMap[user][section]
        users.update({'_id': user}, {'$inc': {'totalTime': totalTime}})


if __name__ == '__main__':
    main(sys.argv)


