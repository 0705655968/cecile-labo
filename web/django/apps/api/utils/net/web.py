# coding: utf-8

import time
import random
import urllib.request
import urllib.parse
import http.cookiejar

from . import wait

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; ja-jp) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.52.7 (KHTML, like Gecko) Version/5.1.2 Safari/534.52.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Win64; x64; Trident/6.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/6.2.8 Safari/537.85.17',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.98 Safari/537.36 Vivaldi/1.6.689.40',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]

RETRY = 1

def get(url, nh=False, param=""):
    
    global RETRY
    data = {'src':'', 'cookie':''}
    ckdata = {}
    try:
        p = urllib.urlparse(url)
        query = urllib.quote_plus(p.query, safe='=&')
        url = '{}://{}{}{}{}{}{}{}{}'.format(p.scheme, p.netloc, p.path,';' if p.params else '', p.params,'?' if p.query else '', query,'#' if p.fragment else '', p.fragment)
    except: pass
    
    if nh==False:
        headers = {'Accept-Language':'ja', 'User-Agent':user_agent()}
    
    nodata = True
    for u in range(RETRY):
        if nodata:
            try:
                if nh:
                    req = urllib.request.Request(url)
                    res = urllib.request.urlopen(req)
                    data['src'] = res.read()
                else:
                    if param:
                        req = urllib.request.Request(url, urllib.urlencode(param), headers)
                    else:
                        req = urllib.request.Request(url, None, headers)
                    
                    cj = http.cookiejar.CookieJar()
                    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
                    res = opener.open(req)
                    data['src'] = res.read()
                    
                    for cookie in cj:
                        ckdata[cookie.name] = cookie.value
                    data["cookie"] = ckdata
                
                nodata = False
                break
            except Exception as e:
                if str(e) == "HTTP Error 404: Not Found": time.sleep(1)
                else: time.sleep(45)
        else:
            if nodata:
                return data
    return data

def user_agent():
    
    global USER_AGENT
    max = len(USER_AGENT)-1

    return USER_AGENT[random.randint(0,max)]

def ispage(url):
    status = True
    try:
        f = urllib.request.urlopen(url) 
    except urllib.request.HTTPError:
        status = False
    return status	

def url_encode(txt):
    return urllib.quote(txt.encode("utf-8"))

def url_decode(txt):
    if isinstance(txt, str):
        value = txt.encode()
    else:
        value = txt
    return urllib.unquote(value)

def stop(seconds):
    wait.stop(seconds)

def stop_random(min, max):
    wait.stop_random(min, max)
