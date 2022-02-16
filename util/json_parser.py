import json
from datetime import datetime
from datetime import date

def time2str(time:datetime):
    return time.strftime('%Y-%m-%d %H:%M:%S')

def str2time(tstr:str):
    return datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')

def date2str(_date:date):
    return _date.strftime('%Y-%m-%d')

def str2date(dstr:str):
    return datetime.strptime(dstr, '%Y-%m-%d').date()