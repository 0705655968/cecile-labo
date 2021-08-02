# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from apps.api.views.cmdty_api_view import *

app_name = 'api'
urlpatterns = [
    path('related_cmdty', CmdtyApiView.related_cmdty, name="api_related_cmdty"),
]
