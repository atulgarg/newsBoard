'''
Created on Oct 3, 2014
 
@author: Anil
'''
 
import json
import urllib2
import datetime
import re
import os
 
'''
 
http://content.guardianapis.com/search?q=occupy+wall+street&from-date=2011-09-01&to-date=2012-02-14&page=2
 
&page-size=3&format=json&show-fields=all&use-date=newspaper-edition&api-key=key
'''
basePath = os.path.dirname(__file__)

def fetchNYTimesData():
    try :
        today = datetime.date.today()
        today = today.strftime("%Y%m%d")
        apiUrl = ' http://api.nytimes.com/svc/search/v2/articlesearch.json?'
        #apiDate = 'begin_date=20131128&end_date=20131128'
        apiDate = 'begin_date=' + today + '&end_date=' + today
        page = '2'
        fields = 'fl=web_url%2Csnippet%2Cabstract%2Cheadline%2C_id%2Csection_name%2Cpub_date%2Cmultimedia'
        apiKey = 'api-Key=4c125135dd6a165bf26f28a8457a9d79:15:69911619'
        link = [apiDate, page, fields, apiKey]
        reqURL = '&' .join (link)
        reqURL = apiUrl + reqURL
        print reqURL
        jstr =  urllib2.urlopen (reqURL).read()
        articles =  json.loads(jstr.decode('utf-8'))
        if (articles['status'] == 'OK' and len(articles['response']['docs']) >= 1):
            totalPages = articles['response']['meta']['hits']
            print  totalPages
            seq = range (100)
            #print seq
            for i in seq:
                nums = str(i)
                apiPages = ''.join(['page=', nums])
                links = [apiDate, apiPages, fields, apiKey]
                reqURL = '&' .join (links)
                reqURL = apiUrl + reqURL
                print reqURL
                jstrs =  urllib2.urlopen(reqURL).read()
                articles = json.loads(jstr.decode('utf-8'))
                result = articles['response']['docs']
                JSONDict = {}
                
                for ob in result:
                    if not ob['abstract']:
                        continue
                    body = ob['abstract'].encode('utf-8')
                    JSONDict['webTitle'] = ob['headline']['main'].encode('utf-8')
                    articleId = ob['_id'].encode('utf-8')
                    JSONDict['id'] = articleId
#                     TAG_RE = re.compile(r'<[^>]+>')
#                     JSONDict['body'] = TAG_RE.sub('', body)
                    JSONDict['body'] = body
                    JSONDict['sectionId'] = ob["section_name"].encode('utf-8')
                    webUrl = ob['web_url'].encode('utf-8')
                    JSONDict['webUrl'] = webUrl.replace('\\','')
                    JSONDict['date'] = ob['pub_date'].encode('utf-8')
                    thumbNail = ""
                    if not len(ob['multimedia']) == 0:
                        thumbNail = ob['multimedia'][0]
                        thumbNail = thumbNail['url'].encode('utf-8')
                        thumbNail = "http://www.nytimes.com/" + thumbNail.replace('\\','')
                    JSONDict['thumbNail'] = thumbNail
                    makeJSON(JSONDict, articleId)             
            
    except:
        traceback.print_exc()


def makeJSON(data, fileName):
    try:
        jsonData = json.dumps(data, indent = 4)
        #print (os.path.abspath(os.path.join(basePath), "..", "jsonData", fileName))
        #filePath = os.path.abspath(os.path.join(basePath), "..", "jsonData", fileName)
        filePath = "../jsonData/" + fileName.replace('/','-') + ".json"
        fd = open(filePath, 'w')
        fd.write("[\n")
        fd.write(jsonData)
        fd.write("\n]")
        fd.close()
    except:
        print 'Error in writing file: ', fileName

def main():
    fetchData()
    
def fetchData():
    apiUrl = 'http://content.guardianapis.com/search?'
    #apiDate = 'from-date=2004-01-01&to-date=2004-12-31'
    date1 = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1))
    date2 = str(datetime.date.fromordinal(datetime.date.today().toordinal()-1))
    apiDate = 'from-date=' + date1 + '&to-date=' + date2
    apiPage = 'page=2'
    apiNum = 100  #number of articles in one page
    apiPageSize = ''.join(['page-size=', str(apiNum)])
    fields = 'show-fields=body,thumbnail'
    key = 'api-key=hz84tx36z2k9qmuf5jwjfnyx'
    
    # make the link and get data
    link = [key, fields, apiPage, apiPageSize, apiDate]
    ReqUrl = '&'.join(link)
    ReqUrl = apiUrl + ReqUrl
    print ReqUrl
    jstr = urllib2.urlopen(ReqUrl).read()
    ts = json.loads(jstr.decode('utf-8'))
    if (ts['response']['status'] == 'ok' and len(ts['response']['results']) > 0) :
        number = ts['response']['total']
        print (number)
        seq = range(int((number-1) / (apiNum) + 1))
        print (seq)
    
        for i in seq:
            nums = str(i + 1)
            apiPages = ''.join(['page=', nums])
            links = [apiDate, apiPages, apiPageSize, fields, key]
            ReqUrls = '&'.join(links)
            ReqUrls = apiUrl + ReqUrls
            print ReqUrls
            jstrs = urllib2.urlopen(ReqUrls).read()
            #t = jstrs.strip('()'.encode())
            tss = json.loads(jstrs.decode('utf-8'))
            result = tss['response']['results']
            JSONDict = {}
            for ob in result:
                try :
                    JSONDict['webTitle'] = ob['webTitle'].encode('utf-8')
                    articleId = ob['id'].encode('utf-8')
                    JSONDict['id'] = articleId.replace('/','-')
                    
                    body = ob['fields']['body'].encode('utf-8') # have to clean the body from slash and other special chars
                    TAG_RE = re.compile(r'<[^>]+>')
                    JSONDict['body'] = TAG_RE.sub('', body)
                    
                    JSONDict['sectionId'] = ob["sectionId"].encode('utf-8')
                    JSONDict['webUrl'] = ob['webUrl'].encode('utf-8')
                    JSONDict['date'] = ob['webPublicationDate'].encode('utf-8')
                    JSONDict['thumbNail'] = ob['fields']['thumbnail'].encode('utf-8')
                except KeyError as e:
                    if (e.args[0] == "body"):
                        continue
                makeJSON(JSONDict, articleId)

if __name__ == '__main__':
    main()   
    
