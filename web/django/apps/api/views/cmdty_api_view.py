from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import generic
import json
import MySQLdb
import MySQLdb.cursors

from django.core.files import File
import environ

import logging
from collections import OrderedDict
from datetime import datetime, date, timedelta
from django.db.models import Q

class CmdtyApiView(generic.ListView):
    
    def related_cmdty(request):
        logger = logging.getLogger('web')
        env = environ.Env()
