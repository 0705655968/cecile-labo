# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import connection
from ...models import *
from apps.api.utils.crud_pages import *
import os
from django.utils import timezone
from datetime import datetime
import io
from pytz import timezone
import re
import subprocess

class Command(BaseCommand):

    def handle(self, *args, **options):

        file_name, ext = os.path.splitext(os.path.basename(__file__))
        p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", file_name], stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, stdout=subprocess.PIPE)
        p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        p2.stdout.close()
        p3.stdout.close()
        output = p4.communicate()[0].decode("utf8").replace('\n','')

        if int(output) != 1:
            print("Error:多重起動エラー")
            #logger.debug("Error:多重起動エラー")
            exit()

        # 新着情報ページの作成
        updates_news_page()
