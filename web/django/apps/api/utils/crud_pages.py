# -*- coding:utf-8 -*-
import os
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import connections
from django.db.models import Q
from api.models import *
from api.utils.net import *
from . import common
from . import date

# 定数
TEMPLATE_DIR = '/opt/app/cecile/front/templates/front/'
NEWS_PAGE = TEMPLATE_DIR+'news.html'
HOME_PAGE = TEMPLATE_DIR+'home.html'
WHATS_NEW = 'https://www.cecile.co.jp/component/app/xml/whatsnew.xml'
CECILE_TOP = 'https://www.cecile.co.jp/'
CECILE_HOME = 'https://www.cecile.co.jp'

# 新着情報ページの更新
def updates_news_page():

  # 新着情報の取得
  data = web.get(WHATS_NEW)
  xml_org = data["src"].decode('shift_jis')
  xml = parser.xml(xml_org)
  news = ''
  tmp = ''
  nowdate = int(date.now_datefmt('%Y%m%d%H%M%S'))
  for data in xml['sdAppHome']['whatsnew']['topic']:
    link = str(data['link']).replace('http:', 'https:')
    img = str(data['img']).replace('http:', 'https:')
    title = data['title']
    open_date = int(date.str2dayfmt(data['startdate'], '%Y%m%d%H%M%S'))
    close_date = int(date.str2dayfmt(data['enddate'], '%Y%m%d%H%M%S'))
    news_date = data['startdate'][0:10]
    if nowdate > open_date and close_date > nowdate:
      setsuzoku = '&' if '?' in link else '?'
      tmp += '<li><a href="'+link+setsuzoku+'L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">'
      tmp += '<img src="'+img+'"><div><p>'+title+'</p>'
      tmp += '<p><span>'+news_date+'</span></p>'
      tmp += '</div></a>'
    if tmp:
      news = '<ul class="news">'+tmp+'</ul>'
  
  # 作成したデータを保存
  save_news_page(news=news)


# 新着情報ページを保存
def save_news_page(news):
  html = '''<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>新着情報</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="author" content="Cecile Inc">
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
  <link rel="stylesheet" href="/static/css/common.css?v=0002">
  <script src="/static/js/common.js"></script>
</head>
<body>
  <div id="contents">
    <header>
      <div class="settings">
        <a href="settings"><i class="material-icons submit">settings</i></a>
      </div>
      <img src="/static/images/logo.gif">
      <h3>新着情報</h3>
    </header>'''
  html += news
  html += '''
  </div>
</body>
</html>
'''
  content_save(fpath=NEWS_PAGE, data=str(html))


# HOMEページの更新
def updates_home_page():

  data = web.get(CECILE_TOP)
  html = parser.content(data["src"])
  # データの初期化
  pickup = ''
  keyvisual = ''
  feature = ''
  banner = ''
  buyer = ''
  coordinate = ''
  ranking = ''
  param = 'L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app'
  rankings = [
    'lady','inner','men','living','beauty','kids','uniform','big'
  ]

  # キービジュアル
  block = parser.attr(html, "div", ["id", "mod-top-keyvisual"])
  items = parser.attr(block, "div", ["class", "box-container"],1)
  tmp = ''
  for item in items:
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    image = ''
    try:
      image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
      if image_src:
        image = CECILE_HOME+image_src
        setsuzoku = '&' if '?' in uri else '?'
        tmp += '<div class="swiper-slide"><a href="'+uri + setsuzoku + param+'"><img src="'+image+'" alt=""></a></div>'
    except: pass

  if tmp:
    keyvisual = '''
      <div class="swiper-container key-visual-slider">
        <div class="swiper-wrapper">
'''
    keyvisual += tmp
    keyvisual += '''
        </div>
      </div>
'''

  # 特集
  block = parser.attr(html, "div", ["id", "feature"])
  items = parser.tag(block, "li",1)
  tmp = ''
  for item in items:
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    image = ''
    try:
      image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
      if image_src:
        image = CECILE_HOME+image_src
        setsuzoku = '&' if '?' in uri else '?'
        tmp += '<li><a href="'+uri+setsuzoku+param+'"><figure class="feature-image"><img src="'+image+'" width="383" height="383" decoding="async"></figure></a></li>'
    except: pass

  if tmp:
    feature = '''
      <div class="feature">
        <div id="feature" class="featurebox sliderwrap">
          <ul class="feature-slider"> 
'''
    feature += tmp
    feature += '''
          </ul>
          <div class="custom-control">
            <div class="btn-prev-feature" tabindex="0" role="button" aria-label="Previous slide" aria-disabled="true"></div>
            <div class="btn-next-feature" tabindex="0" role="button" aria-label="Next slide" aria-disabled="false"></div>
          </div>
        </div>
      </div>
'''
  
  # トップバナー
  block = parser.attr(html, "figure", ["class", "topbanner-image"])
  if block:
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    try:
      image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src")).replace('383_383','1200_480')
      if image_src:
        image = CECILE_HOME+image_src
        setsuzoku = '&' if '?' in uri else '?'
        banner = '<div class="top_banner"><a href="'+uri+setsuzoku+param+'"><img src="'+image+'"></a></div>'
    except: pass
  
  # ピックアップ情報
  block = parser.attr(html, "section", ["id", "rt_conomi_special_top"])
  items = parser.tag(block, "li", 1)
  tmp = ''
  for item in items:
    title = ''
    try:
      title = parser.string(parser.tag(item, "span"))
    except: pass
    image = ''
    try:
      image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
      if image_src:
        image = CECILE_HOME+image_src
    except: pass
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.attr(item, "a", ["class", "card-inner"]), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    genre = ''
    try:
      genre = parser.string(parser.tag(parser.attr(item, "p", ["class", "text-category"]), "a"))
    except: pass

    if uri:
      setsuzoku = '&' if '?' in uri else '?'
      tmp += '<li><a href="'+uri+setsuzoku+param+'">'
      if image:
        tmp += '<img src="'+image+'">'
      tmp += '<p>'+title+'</p>'
      tmp += '<p><span>'+genre+'</span></p></a>'
 
  if tmp:
    pickup = '''
      <div class="title">ピックアップ特集</div>
      <ul class="grid">
'''
    pickup += tmp
    pickup += '''
      </ul>
      <div class="allview">
'''
    pickup += '<a href="https://www.cecile.co.jp/sc/?'+param+'">'
    pickup += '''
          <div>すべての特集を見る</div>
          <div class="icon"><i class="material-icons">chevron_right</i></div>
        </a>
      </div>
'''

  # バイヤー厳選
  block = parser.attr(html, "section", ["id", "atrec_pickupcmdty1_top"])
  if block:
    title = ''
    try:
      title = parser.string(parser.attr(block, "h3", ["class", "title"]))
    except: pass
    try:
      detail = parser.string(parser.attr(block, "p", ["class", "text-info"]))
    except: pass
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.tag(block, "a"), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    try:
      image_src = parser.string(parser.attribute(parser.tag(block, "img"), "src"))
      if image_src:
        image = CECILE_HOME+image_src
        buyer = '<div class="buyer">'
        setsuzoku = '&' if '?' in uri else '?'
        buyer += '<a href="'+uri+setsuzoku+param+'"><img src="'+image+'">'
        buyer += '<p class="icon"><span>バイヤー厳選</span></p>'
        if title:
          buyer += '<p>'+title+'</p>'
        if detail:
          buyer += '<p class="sub">'+detail+'</p>'
        buyer += '</a></div>'
    except: pass
    
  # コーディネート
  try:
    items = parser.attr(html, "h2", ["class", "ttl-cmn-02"],1)
    for item in items:
      tmp = parser.string(item)
      if 'コーディネート' in tmp:
        coordinate = '<div class="title">'+tmp+'</div>'
        break 
  except: pass
  
  block = parser.attr(html, "div", ["id", "mod-trend-coordinate"])
  items = parser.attr(block, "div", ["class", "box-trend-content"],1)
  num = 0
  tmp = ''
  for item in items:
    uri = ''
    try:
      href = parser.string(parser.attribute(parser.tag(parser.attr(item, "div", ["class", "trigger"]), "a"), "href"))
      if href:
        uri = CECILE_HOME+href
    except: pass
    try:
      image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
      title = parser.string(parser.attribute(parser.tag(item, "img"), "alt"))
      if image_src:
        image = CECILE_HOME+image_src
        if num == 0:
          setsuzoku = '&' if '?' in uri else '?'
          coordinate += '<div class="trend"><a href="'+uri+setsuzoku+param+'"><img src="'+image+'"><p>'+title+'</p></a></div>'
        else:
          setsuzoku = '&' if '?' in uri else '?'
          tmp += '<li><a href="'+uri+setsuzoku+param+'"><img src="'+image+'"><p>'+title+'</p></a>'
      num += 1
    except: pass
    if num > 3: break

  if tmp:
    coordinate += '''
      <ul class="grid trend">
'''
    coordinate += tmp
    coordinate += '''
      </ul>
      <div class="allview">
'''
    coordinate += '<a href="https://www.cecile.co.jp/sc/style/?'+param+'">'
    coordinate += '''
          <div>すべてのコーディネートを見る</div>
          <div class="icon"><i class="material-icons">chevron_right</i></div>
        </a>
      </div>
'''
  
  # ランキング
  box = 0
  ranking = ''
  active = ' is-active'

  block = parser.attr(html, "div", ["class", "js-box-ranking-content"])
  ranking_blocks = parser.attr(block, "div", ["class", "box-ranking-content-in"],1)
  for ranking_block in ranking_blocks:
    items = parser.attr(ranking_block, "div", ["class", "item-slider"],1)
    ranking += '<ul class="grid ranking box-'+str(box)+active+'">'
    active = ''
    rank = 1
    genre = rankings[box]
    for item in items:
      price = ''
      try:
        price = parser.html_string(parser.attr(item, "p", ["class", "text-price"]))
      except: pass
      uri = ''
      try:
        href = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
        if href:
          uri = CECILE_HOME+href
      except: pass
      try:
        image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
        title = parser.string(parser.attribute(parser.tag(item, "img"), "alt"))
        if image_src:
          image = CECILE_HOME+image_src
          ranking += '<li><p class="rank">'+str(rank)+'</p>'
          setsuzoku = '&' if '?' in uri else '?'
          ranking += '<a href="'+uri+setsuzoku+param+'"><img src="'+image+'">'
          ranking += '<p>'+title+'</p><p><span>'+price+'</span></p></a>'
      except: pass
      rank += 1
      if rank > 6: break
    ranking += '</ul>'
    ranking += '<div class="allview ranking ranking-'+str(box)+'">'
    box += 1
    ranking += '<a href="https://www.cecile.co.jp/sc/ranking/'+genre+'/?'+param+'">'
    ranking += '''
          <div>人気ランキングの続きはこちら</div>
          <div class="icon"><i class="material-icons">chevron_right</i></div>
        </a>
      </div>
'''
  """
  for genre in rankings:
    data_rank = web.get('https://www.cecile.co.jp/sc/ranking/'+genre+'/')
    html_rank = parser.content(data_rank["src"])
    block = parser.attr(html_rank, "ol", ["class", "ranking-list"])
    items = parser.attr(block, "li", ["class", "ranking-list-item"],1)

    ranking += '<ul class="grid ranking box-'+str(box)+active+'">'
    active = ''
    rank = 1
    for item in items:
      price = ''
      try:
        price = parser.html_string(parser.attr(item, "p", ["class", "price"]))
      except: pass
      uri = ''
      try:
        href = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
        if href:
          uri = CECILE_HOME+href
      except: pass
      try:
        image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
        title = parser.string(parser.attribute(parser.tag(item, "img"), "alt"))
        if image_src:
          image = CECILE_HOME+image_src
          ranking += '<li><p class="rank">'+str(rank)+'</p>'
          setsuzoku = '&' if '?' in uri else '?'
          ranking += '<a href="'+uri+setsuzoku+param+'"><img src="'+image+'">'
          ranking += '<p>'+title+'</p><p><span>'+price+'</span></p></a>'
      except: pass
      rank += 1
      if rank > 6: break
    ranking += '</ul>'
    ranking += '<div class="allview ranking ranking-'+str(box)+'">'
    box += 1
    ranking += '<a href="https://www.cecile.co.jp/sc/ranking/'+genre+'/?'+param+'">'
    ranking += '''
          <div>人気ランキングの続きはこちら</div>
          <div class="icon"><i class="material-icons">chevron_right</i></div>
        </a>
      </div>
  """
  save_home_page(keyvisual, feature, banner, pickup, buyer, coordinate, ranking, param)

# HOMEページを保存
def save_home_page(keyvisual, feature, banner, pickup, buyer, coordinate, ranking, param):
  html = '''<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>お買い物アプリ|セシール</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="author" content="Cecile Inc">
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
  <link rel="stylesheet" href="/static/css/common.css?v=0003">
  <script src="/static/js/common.js?v=0001"></script>
</head>
<body>
  <div class="dammy"></div>
  <div id="contents">
    <div class="popup"></div>
    <header>
      <div class="settings">
        <a href="settings"><i class="material-icons submit">settings</i></a>
      </div>
      <img src="/static/images/logo.gif">
      <div class="searchbox">
        <div class="searcharea">
          <form method="get" id="frmEnterKeyForHeader" action="https://www.cecile.co.jp/search-results/go">
            <div class="searchitem search-cat">
              <select name="af">
                <option value="">すべての商品から</option>
                <option value="cat1:0ld">レディースファッション</option>
                <option value="cat1:0in">女性下着</option>
                <option value="cat1:0mn">メンズファッション</option>
                <option value="cat1:0un">メンズ下着</option>
                <option value="cat1:0uf">事務服・作業服・白衣</option>
                <option value="cat1:0sc">制服・学生服</option>
                <option value="cat1:0fs">ファッション・下着すべて</option>
                <option value="cat1:0fn">家具・収納</option>
                <option value="cat1:0bd">寝具・ベッド</option>
                <option value="cat1:0ct">カーテン・ラグ・ファブリック</option>
                <option value="cat1:0lf">キッチン・雑貨・日用品</option>
                <option value="cat1:0bt">美容・健康・サプリメント</option>
              </select>
            </div>
            <div class="searchitem search-txt">
              <input name="w" id="q" type="text" value="" maxlength="130" autocomplete="off" data-provide="rac" onkeydown="" placeholder="キーワードを入力" >
              <input type="hidden" name="L" value="cecileapp">
              <input type="hidden" name="utm_source" value="cecile_dinos_apps">
              <input type="hidden" name="utm_medium" value="app">
            </div>
            <div class="searchitem btn">
              <i class="material-icons submit">search</i>
            </div>
          </form>
        </div>
      </div>
    </header>
    <div class="container">
'''
  html += keyvisual
  html += feature
  html += banner
  html += '''
      <div class="title nb">人気ランキング</div>
      <div class="swiper-container js-swiper-category">
        <div class="swiper-wrapper">
          <div class="swiper-slide item-slider"> <span class="btn-category">
            レディース</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            インナー・下着</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            メンズ</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            寝具・インテリア・雑貨</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            美容・健康</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            制服・スクール</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            事務服・白衣</span> </div>
          <div class="swiper-slide item-slider"> <span class="btn-category">
            大きいサイズ</span> </div>
        </div>
        <div class="swiper-ranking-button-prev"></div>
        <div class="swiper-ranking-button-next"></div>
      </div>
'''
  html += ranking
#  html += buyer
  html += pickup
  html += coordinate

  genres = [
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/LD/','レディースファッション'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/LD/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g3-1-LD-TS-1I/','Tシャツ'],
        ['https://www.cecile.co.jp/genre/g3-1-LD-TS-BR/','ブラウス'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-TS/','トップス'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-OP/','ワンピース'],
        ['https://www.cecile.co.jp/genre/g3-1-LD-TS-TN/','チュニック'],
        ['https://www.cecile.co.jp/genre/g3-1-LD-TS-1G/','ニット・セーター'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-PN/','パンツ'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-SK/','スカート'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-FR/','スーツ'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-BA/','バッグ'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-SB/','シューズ'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-FG/','ファッション小物'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-AC/','アクセサリー'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-RN/','レインウェア'],
        ['https://www.cecile.co.jp/genre/g2-1-LD-SW/','水着'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/IN/','女性下着'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/IN/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-BS/','ブラジャー'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-SU/','ブラ＆ショーツセット'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-SH/','ショーツ'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-IN/','肌着・インナー'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-BD/','補整下着'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-LN/','ランジェリー'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-IN/','ジュニア・ティーンズ下着'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-PJ/','パジャマ・ルームウェア'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-ST/','ストッキング・タイツ'],
        ['https://www.cecile.co.jp/genre/g2-1-IN-SC/','靴下・ソックス'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/MN/','メンズファッション'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/MN/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g3-1-MN-TS-1I/','Tシャツ'],
        ['https://www.cecile.co.jp/genre/g3-1-MN-TS-1E/','ポロシャツ'],
        ['https://www.cecile.co.jp/genre/g3-1-MN-CT-JK/','ジャケット'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-TS/','トップス'],
        ['https://www.cecile.co.jp/genre/g3-1-MN-TS-1G/','ニット・セーター'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-FR/','スーツ'],
        ['https://www.cecile.co.jp/genre/g3-1-MN-TS-YS/','ワイシャツ・カッターシャツ'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-PN/','パンツ'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-BA/','バッグ'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-SB/','シューズ'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-FG/','ファッション小物'],
        ['https://www.cecile.co.jp/genre/g2-1-MN-RN/','レインウェア'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/UN/','メンズ下着'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/UN/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-UN-IN/','肌着・インナー'],
        ['https://www.cecile.co.jp/genre/g2-1-UN-SH/','トランクス・ブリーフ'],
        ['https://www.cecile.co.jp/genre/g2-1-UN-PJ/','パジャマ・ルームウェア'],
        ['https://www.cecile.co.jp/genre/g2-1-UN-SC/','靴下・ソックス'],
        ['https://www.cecile.co.jp/genre/g2-1-UN-ST/','タイツ・レギンス'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/UF/','事務服・作業服・白衣'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/UF/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-UF-OF/','事務服・OL制服'],
        ['https://www.cecile.co.jp/genre/g2-1-UF-NS/','ナース服・白衣'],
        ['https://www.cecile.co.jp/genre/g2-1-UF-WW/','作業着・ワークウェア'],
        ['https://www.cecile.co.jp/genre/g2-1-UF-FU/','飲食店ユニフォーム'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/SC/','制服・学生服'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/SC/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-HS/','高校制服'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-JH/','中学校制服'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-PS/','小学校制服'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-GL/','女子制服'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-BY/','男子制服'],
        ['https://www.cecile.co.jp/genre/g2-1-SC-IN/','ジュニア・ティーンズ下着'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/s/big/','大きいサイズ'
      ],
      'sub': [
        ['https://www.cecile.co.jp/s/big/','すべてのアイテム'],
        ['/feature/lsize/lady/','大きいサイズ レディース服'],
        ['/feature/lsize/inner/','大きいサイズ レディース下着'],
        ['/feature/lsize/men/','大きいサイズ メンズ'],
        ['/feature/lsize/office/','大きいサイズ 事務服・制服'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/FS/','ファッション・下着すべて'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/FS/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g3-1-FS-TS-1I/','Tシャツ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-TS/','トップス'],
        ['https://www.cecile.co.jp/genre/g3-1-FS-CT-JK/','ジャケット'],
        ['https://www.cecile.co.jp/genre/g3-1-FS-TS-1G/','ニット・セーター'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-OP/','ワンピース'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-PN/','パンツ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-SK/','スカート'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-FR/','スーツ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-BS/','ブラジャー'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-SU/','ブラ＆ショーツセット'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-SH/','ショーツ・トランクス'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-IN/','肌着・インナー'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-BD/','補整下着'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-LN/','ランジェリー'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-PJ/','パジャマ・ルームウェア'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-ST/','ストッキング・タイツ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-SC/','靴下・ソックス'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-BA/','バッグ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-SB/','シューズ'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-AC/','アクセサリー'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-FG/','ファッション小物'],
        ['https://www.cecile.co.jp/genre/g2-1-FS-RN/','レインウェア'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/FN/','家具・収納'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/FN/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-KT/','キッチン収納・食器棚'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-CL/','衣類収納'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-CO/','クローゼット・押入れ収納'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-OT/','収納家具・収納 その他'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-EN/','玄関収納・屋外収納'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-CH/','チェスト・キャビネット'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-LC/','ラック'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-BK/','本棚'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-TB/','テーブル・机'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-SF/','ソファー・チェアー'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-TV/','テレビ台'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-KO/','こたつ・こたつ布団'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-KD/','学習机･子供部屋'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-DR/','ドレッサー・ミラー'],
        ['https://www.cecile.co.jp/genre/g2-1-FN-BU/','仏壇・仏具'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/BD/','寝具・ベッド'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/BD/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-CV/','布団カバー・シーツ'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-CL/','布団・枕'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-BL/','毛布・タオルケット'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-BD/','ベッド'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-MT/','マットレス'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-BS/','ベッドサイド家具・小物'],
        ['https://www.cecile.co.jp/genre/g2-1-BD-CF/','安眠・快眠グッズ'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/FN/','カーテン・ラグ・ファブリック'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/FN/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-CT/','カーテン'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-BL/','ブラインド・ロールスクリーン'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-CP/','カーペット'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-MT/','ラグ・マット類'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-CV/','カバー類'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-TW/','タオル'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-CS/','クッション・座布団'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-TL/','トイレタリー'],
        ['https://www.cecile.co.jp/genre/g2-1-CT-SP/','スリッパ'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/LF/','キッチン・雑貨・日用品'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/LF/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g3-1-LF-EL-1D/','扇風機'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-KT/','キッチン用品'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-LG/','生活雑貨'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-BT/','バス用品・ランドリー'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-EL/','家電・AV機器'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-TL/','トイレ用品'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-LN/','洗濯用品・掃除道具'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-IN/','インテリア雑貨・小物'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-HG/','趣味雑貨'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-FL/','花・ガーデニング'],
        ['https://www.cecile.co.jp/genre/g2-1-LF-GF/','ギフト'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/genre/g1/1/BT/','美容・健康・サプリメント'
      ],
      'sub': [
        ['https://www.cecile.co.jp/genre/g1/1/BT/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-HC/','ヘアケア・ボディケア'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-PF/','コスメ・ネイル・香水'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-CS/','スキンケア化粧品'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-BR/','ブランドで選ぶ'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-ES/','ホームエステ'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-HF/','ダイエット・健康食品'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-SP/','サプリメント'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-SN/','衛生用品'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-HG/','健康器具'],
        ['https://www.cecile.co.jp/genre/g2-1-BT-NC/','シニア・介護用品'],
      ],
    },
    {
      'main':[
        'https://www.cecile.co.jp/bargain/','バーゲン'
      ],
      'sub': [
        ['https://www.cecile.co.jp/bargain/','すべてのアイテム'],
        ['https://www.cecile.co.jp/genre/g1/1/LD/bargain/','レディースファッション'],
        ['https://www.cecile.co.jp/genre/g1/1/IN/bargain/','女性下着'],
        ['https://www.cecile.co.jp/genre/g1/1/MN/bargain/','メンズファッション'],
        ['https://www.cecile.co.jp/genre/g1/1/UN/bargain/','メンズ下着'],
        ['https://www.cecile.co.jp/genre/g1/1/UF/bargain/','事務服・作業服・白衣'],
        ['https://www.cecile.co.jp/genre/g1/1/SC/bargain/','制服・学生服'],
        ['https://www.cecile.co.jp/genre/g1/1/FS/bargain/','ファッション・下着すべて'],
        ['https://www.cecile.co.jp/genre/g1/1/FN/bargain/','家具・収納'],
        ['https://www.cecile.co.jp/genre/g1/1/BD/bargain/','寝具・ベッド'],
        ['https://www.cecile.co.jp/genre/g1/1/CT/bargain/','カーテン・ラグ・ファブリック'],
        ['https://www.cecile.co.jp/genre/g1/1/LF/bargain/','キッチン・雑貨・日用品'],
        ['https://www.cecile.co.jp/genre/g1/1/BT/bargain/','美容・健康・サプリメント'],
      ],
    },
  ]

  html += '''
      <div class="title">カテゴリから探す</div>
      <nav class="mod-side-category">
        <ol id="nav-side-category-sp" class="list-category">
'''
  for genre in genres:
    html += '<li><a href="'+genre['main'][0]+'?'+param+'" class="link-main"><span class="text">'+genre['main'][1]+'</span></a>'
    html += '<div class="box-nav-sub"><ol class="list-sub-category">'
    for v in genre['sub']:
      html += '<li><a class="link-sub" href="'+v[0]+'?'+param+'">'+v[1]+'</a></li>'
    html += '</ol></div></li>'

  html += '''
        </ol>
      </nav>

      <div class="catalog_info">
        <img src="/static/images/catalog.png">
        <ol>
          <li class="multi">
            <a href="https://www.cecile.co.jp/site/order/sheet/ConfSrv.jsp?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
              <div class="label">カタログ・チラシをお持ちの方<span>申込番号でご注文</span></div>
              <div class="icon"><i class="material-icons">chevron_right</i></div>
            </a>
          <li>
            <a href="https://www.cecile.co.jp/site/inquiry/catalog/SelectSrv.jsp?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
              <div>カタログ無料プレゼント</div>
              <div class="icon"><i class="material-icons">chevron_right</i></div>
            </a>
        </ol>
      </div>
      <ul class="grid footer">
        <li>
          <a href="https://www.cecile.co.jp/present/game/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
            <img src="/static/images/present2.png">
          </a>
        <li>
          <a href="https://www.cecile.co.jp/present/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
            <img src="/static/images/present1.png" class="hosei">
          </a>
      </ul>
    </div>
  </div>
</body>
</html>
'''
  content_save(fpath=HOME_PAGE, data=str(html))

def content_save(fpath, data):
    try:
        dpath = os.path.dirname(fpath)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        f = open(fpath, 'w')
        f.write(data)
        f.close()
    except Exception as e:
        pass
