from bottle import default_app, route, request, response, redirect, template
import requests
import pickle
from json import dumps

from bottle import run

def video_is_exist(permalink):

    try:
        with open ('history.pickle', 'rb') as f:
            data = pickle.load(f)
    except Exception:
        return False

    return permalink in data

def add_video_into_history(permalink):
    with open ('history.pickle', 'rb') as f:
        data = pickle.load(f)

    data.append(permalink)

    with open('history.pickle', 'wb') as f:
        pickle.dump(data, f)


def getByDuration(req, duration, proxies):
    page = 1
    per_page = 25
    curr_duration = 0
    permalinks = []

    while curr_duration < duration:
        if proxies:
            r = requests.get(req, data={ 'page': page, 'per_page': per_page }, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}, proxies=proxies)
        else:
            r = requests.get(req, data={ 'page': page, 'per_page': per_page }, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        
        for v in r.json()['coubs']:
            if v['duration'] > 3.5 and not video_is_exist(v['permalink']):
                permalinks.append(v['permalink'])
                add_video_into_history(v['permalink'])
                curr_duration+=v['duration']
                if curr_duration >= duration:
                    break
        page += 1

    return {
            'permalinks': permalinks,
            'duration': int(curr_duration),
            'count': len(permalinks)
        }


def getByCount(req, count, proxies):
    page = 1
    per_page = 25
    curr_duration = 0
    data = []

    while 1:
        if proxies:
            r = requests.get(req, data={ 'page': page, 'per_page': per_page },  
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'},
                proxies=proxies)
        
        else:
            r = requests.get(req, data={ 'page': page, 'per_page': per_page },  
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})

        for v in r.json()['coubs']:
            if v['duration'] > 3.5 and not video_is_exist(v['permalink']):
                data.append(v['permalink'])
                add_video_into_history(v['permalink'])
                curr_duration+=v['duration']
                if len(data)>=count:
                    return {
                        'permalinks': data,
                        'duration': int(curr_duration),
                        'count': len(data)
                    }
        page+=1






def getData(category, duration, count, period, proxies):
    req = 'http://coub.com/api/v2/timeline/hot/'

    if category != 'all':
        req += category + '/'

    if period:
        req += period + '/'

    if duration:
        count = 0

    if not duration and not count:
        duration = 610

    if duration:
        data = getByDuration(req, float(duration), proxies)
        data['period'] = period
        data['category'] = category
        return data

    if count:
        data = getByCount(req, int(count), proxies)
        data['period'] = period
        data['category'] = category
        return data

    return []




@route('/hot/<category>')
@route('/hot/<category>/')
def getHot(category):
    response.content_type = 'application/json'

    duration = request.query.duration
    count = request.query.count
    period = request.query.period

    proxies = ""

    praddress = request.query.proxy
    if praddress:
        proxies = {
            'http': 'http://'+praddress,
        }   

    data = getData(category, duration, count, period, proxies)
    return dumps(data)


@route('/')
def index():
    return template('index')

@route('/hot')
@route('/hot/')
def redirectToDefaultSearch():
    redirect("/hot/all")


application = default_app()

run(application, host='localhost', port=8000)

