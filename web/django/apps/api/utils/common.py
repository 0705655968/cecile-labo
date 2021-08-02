# -*- coding:utf-8 -*-
import os
import re
import sys
from .net import *

def replaces(text, c):
    if text:
        for k, v in c.items():
            text = text.replace(k, v)
    return text

def replaces_regex(text, c):
    if text:
        for k, v in c.items():
            wordList = re.findall(str(k)+"(.*?)" + str(v), text)
            for wd in wordList: text = text.replace(str(k) + wd + str(v), "")
        
    return text

def photo(url, local):
    rslt = {'rslt':False, 'msg':''}
    try:
        data = web.get(url)
        if data["src"]:
            r = save(fpath=local, data=data['src'])
            if r == 'ng':
                rslt['msg'] = 'already saved: ' + str(local)            
            else:
                rslt['rslt'] = True
                if r == 'exist':
                    rslt['msg'] = 'already saved: ' + str(local)
        else:
            rslt['msg'] = 'no data: ' + str(local)
    except Exception as e:
        rslt['msg'] = str(e) + ': ' + str(local)
    
    return rslt

def xml(url, local):
    rslt = {'rslt':False, 'msg':''}
    try:
        data = web.get(url)
        if data["src"]:
            xml = data["src"].decode('utf-8').replace('\r','').replace('Shift_JIS','UTF-8')
            r = save(fpath=local, data=xml.encode('utf-8'))
            if r == 'ng':
                rslt['msg'] = 'already saved: ' + str(local)            
            else:
                rslt['rslt'] = True
                if r == 'exist':
                    rslt['msg'] = 'already saved: ' + str(local)
        else:
            rslt['msg'] = 'no data: ' + str(local)
    except Exception as e:
        rslt['msg'] = str(e) + ': ' + str(local)
    
    return rslt

def save(fpath, data):
    rslt = 'ng'
    try:
        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        if not os.path.isfile(fpath) or os.path.getsize(fpath)==0:
            f = open(fpath, 'wb')
            f.write(data)
            f.close()
            rslt = "ok"
        else: rslt = "exist"
    except Exception as e:
        print(e)
        pass

    return rslt
