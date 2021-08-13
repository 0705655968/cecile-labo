# -*- coding:utf-8 -*-
import os
import shutil
import imagehash
import xmltodict
from PIL import Image
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import connections
from django.db.models import Q
from api.models import *
from api.utils.net import *
from . import common
from . import date

# 定数
IMGSEARCH_DIR = '/opt/app/cecile/data/imgsearch/'
HASH_DIR = IMGSEARCH_DIR+'hash/'
CATALOG_HASH_DIR = HASH_DIR+'catalog/'
PAGE_HASH_DIR = HASH_DIR+'page/'

# image hashの対象となる画像データを作成
def updates_image_hash():

  # カタログ表紙
  # カタログマスターから対象データを取得
  '''
  MAX_ROWS = 1000
  max_pages = CatalogMaster.objects.filter(status='1').count()
  # ディレクトリの初期化
  shutil.rmtree(CATALOG_HASH_DIR)
  os.mkdir(CATALOG_HASH_DIR)
  for offset in range(0, max_pages, MAX_ROWS):
    limit = offset + MAX_ROWS
    item_lists = CatalogMaster.objects.filter(status='1').order_by("-id")[offset:limit]
    for data in item_lists:
      if os.path.isfile(data.local):
        copy = CATALOG_HASH_DIR + os.path.basename(data.local)
        shutil.copyfile(data.local, copy)
  '''
  # 画像処理
  target = '/opt/app/cecile/data/media/20210811103723_scaled_3bc3c96d-0ebe-4aa9-aaa1-9d20748ba5245034203735463070405.jpg'
  target_hash = imagehash.phash(Image.open(target))
        
  userpath = '/opt/app/cecile/data/imgsearch/hash/catalog/'
  image_files = []
  f = [os.path.join(userpath, path) for path in os.listdir(userpath)]
  for i in f:
    image_files.append(i)
        
  idx = {'haming':1000, 'path':''}
  for img in image_files:
    hash = imagehash.phash(Image.open(img))
    haming = target_hash - hash
    if idx['haming'] > haming:
      idx['path'] = img
      idx['haming'] = haming
  
  if idx['haming'] < 40:
    code = idx['path'].replace('/opt/app/cecile/data/imgsearch/hash/catalog/','').replace('.jpg','')
    data = CatalogMaster.objects.get(catalog=code)
    genre = CatalogGenreLink.objects.get(catalog=code)

    catalog_data = '<div class="title"><i class="material-icons submit">manage_search</i>検索されたカタログ</div>'
    catalog_data += '<ol class="search_result">'
    catalog_data += '<li>'
    catalog_data += '<a href="https://cecile-dev.prm.bz/viewer/'+str(code)+'/">'
    catalog_data += '<img src="https://cecile-dev.prm.bz/static/images/s.gif" style="background-image:url('+str(data.image)+')">'
    catalog_data += '<div>'
    catalog_data += '<p class="title">'+str(data.name)+'</p>'
    catalog_data += '<p><span>'+str(genre.genre)+'</span></p>'
    catalog_data += '</div>'
    catalog_data += '</a>'
    catalog_data += '</ol>'

    context = {
      'code': code,
      'name': data.name,
    }
    print(context)
    