# coding: utf-8
from datetime import datetime as dt
import datetime
import dateutil.parser

def now_datetime():
    tdatetime = dt.now()
    tstr = tdatetime.strftime('%Y-%m-%d %H:%M:%S')
    return tstr

def now_date():
    tdatetime = dt.now()
    tstr = tdatetime.strftime('%Y-%m-%d')
    return tstr

def now_datefmt(fmt):
    tdatetime = dt.now()
    tstr = tdatetime.strftime(fmt)
    return tstr

def datefmt(fmt, day):
    d = datetime.datetime.now()
    d -= datetime.timedelta(days=day)
    tstr = d.strftime(fmt)
    return tstr

def str2dayfmt(tstr, fmt):
    tstr = dateutil.parser.parse(tstr)
    tstr = tstr.strftime(fmt)
    return tstr
