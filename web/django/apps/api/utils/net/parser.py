# coding: utf-8
import re
import json as jsn
import xmltodict
import cgi
import urllib.parse
from bs4 import BeautifulSoup

def content(data):
    
    return BeautifulSoup(data, "html.parser")

def text_only(data, stoptag=["script", "style", "head", "footer"]):
    for s in data(stoptag):
        s.decompose()
    text = "\n".join(data.stripped_strings)
    return text

def json(data):
    return jsn.loads(data)

def xml(data):
    return xmltodict.parse(data)

def text(data, tag, txt):
    try:
        res = data.find(tag, text=txt)
    except:
        res = ''
    return res

def tag(data,tag,md=0):
    try:
        if md:
            res = data.findAll(tag)
        else:
            res = data.find(tag)
    except:
        res = ''
    return res
    
def attr(data, tag, atr, md=0):
    try:
        if md:
            res = data.findAll(tag,attrs={atr[0]:atr[1]})
        else:
            res = data.find(tag,attrs={atr[0]:atr[1]})
    except Exception as e:
        res = ''
    return res
    
def attr_regex(data, tag, atr, md=0):
    try:
        if md:
            res = data.findAll(tag, attrs={atr[0]:re.compile(atr[1])})
        else:
            res = data.find(tag, attrs={atr[0]:re.compile(atr[1])})
    except Exception as e:
        res = ''
    return res

def attrs(data, atrs, md=0):
    try:
        for tag,atr in atrs.items():
            try:
                if md:
                    res = data.findAll(tag, attrs={atr[0]:atr[1]})
                else:
                    res = data.find(tag, attrs={atr[0]:atr[1]})
            except:
                res = ''
            
            if res:
                break
    except:
        res = ''
    return res

def attribute(obj, attr):
    str = ''
    try:
        str = obj.attrs[attr]
    except:
        pass
    return str

def string(obj):
    txt = ''
    try:
        txt = obj.string
        if isinstance(txt, bytes):
            txt = txt.encode('utf8').strip()
    except:
        try:
            max = len(obj.contents)
            for v in range(max):
                txt += str(obj.contents[v]).strip()
        except:
            try:
                txt = re.sub("<.*?>", "", obj)
                txt = txt.replace('\t', '')
                txt = txt.replace('\n', '')
                txt = txt.replace(' ', '')
            except:
                pass
    return txt

def html_string(html, tag_only=True, brnl=False):
    text = str(html)
    if isinstance(text, bytes):
        text = text.decode("utf8")
    
    if brnl:
        p = re.compile(r"<br.*?>")
        text = p.sub("\n", text)

    if tag_only:
        p = re.compile(r"<[^>]*?>")
    else:
        p = re.compile(r"<.*?>.*?<\/.*?>")
    return p.sub("", text)

def query(url):
    params = urllib.parse.parse_qs(url)
    
    return params
