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
HOME_PAGE = TEMPLATE_DIR+'home2.html'
WHATS_NEW = 'http://special.cecile.co.jp/app/xml/apphome.xml'
CECILE_TOP = 'https://www.cecile.co.jp/'
CECILE_HOME = 'https://www.cecile.co.jp'

# 新着情報ページの更新
def updates_news_page():

  # 新着情報の取得
  data = web.get(WHATS_NEW)
  xml_org = data["src"].decode('shift_jis')
  xml = parser.xml(xml_org)
  keyvisual = ''
  news = ''
  if xml['sdAppHome']['keyvisual']:
    tmp = xml['sdAppHome']['keyvisual']
    keyvisual = '<div class="keyvisual">'
    keyvisual += '<a href="'+str(tmp['url'])+'?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">'
    keyvisual += '<img src="'+str(tmp['img']['sp'])+'"></a></div>'
  
  tmp = ''
  for data in xml['sdAppHome']['whatsnew']['topic']:
    link = str(data['link']).replace('http:', 'https:')
    img = str(data['img']).replace('http:', 'https:')
    title = data['title']
    news_date = data['date']
    tmp += '<li><a href="'+link+'?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">'
    tmp += '<img src="'+img+'"><div><p>'+title+'</p>'
    tmp += '<p><span>'+news_date+'</span></p>'
    tmp += '</div></a>'
  if tmp:
    news = '<ul class="news">'+tmp+'</ul>'
  
  # 作成したデータを保存
  save_news_page(keyvisual=keyvisual, news=news)


# 新着情報ページを保存
def save_news_page(keyvisual, news):
  html = '''<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>新着情報</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="author" content="Cecile Inc">
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
  <link rel="stylesheet" href="/static/css/common.css?v=0001">
  <script src="/static/js/common.js"></script>
</head>
<body>
  <div id="contents">
    <header>
      <h3>新着情報</h3>
      <div class="settings">
        <a href="settings"><i class="material-icons submit">settings</i></a>
      </div>
    </header>'''
  html += keyvisual
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

  # ピックアップ情報
  block = parser.attr(html, "section", ["id", "rt_conomi_special_top"])
  items = parser.tag(block, "li", 1)
  tmp = ''
  for item in items:
    title = parser.string(parser.tag(item, "span"))

    image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
    image = ''
    if image_src:
      image = CECILE_HOME+image_src
    
    href = parser.string(parser.attribute(parser.attr(item, "a", ["class", "card-inner"]), "href"))
    uri = ''
    if href:
      uri = CECILE_HOME+href
    
    genre = parser.string(parser.tag(parser.attr(item, "p", ["class", "text-category"]), "a"))

    tmp += '<li><a href="'+uri+'?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">'
    if image:
      tmp += '<img src="'+image+'">'
    tmp += '<p>'+title+'</p>'
    tmp += '<p><span>'+genre+'</span></p></a>'

  if tmp:
    html = '''
      <div class="title">ピックアップ特集</div>
      <ul class="grid">
'''


    html += '''
      </ul>
      <div class="allview">
        <a href="https://www.cecile.co.jp/sc/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
          <div>すべての特集を見る</div>
          <div class="icon"><i class="material-icons">chevron_right</i></div>
        </a>
      </div>
'''

# HOMEページを保存
def save_home_page(key_visual_slider, ranking, trend):
  html = '''<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>お買い物アプリ|セシール</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="author" content="Cecile Inc">
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
  <link rel="stylesheet" href="/static/css/common.css?v=0001">
  <script src="/static/js/common.js"></script>
</head>
<body>
  <div id="contents">
    <header>
      <div class="searcharea">
        <form method="get" id="frmEnterKeyForHeader" action="https://www.cecile.co.jp/search-results/go">
          <div class="searchitem">
            <select name="af">
              <option value="">全ての商品</option>
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
      <div class="settings">
        <a href="settings"><i class="material-icons submit">settings</i></a>
      </div>
    </header>
    <div class="container">'''
  html += key_visual_slider
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
  html += trend
  html += '''
      <div class="title">カテゴリから探す</div>
      <nav class="mod-side-category">
        <ol id="nav-side-category-sp" class="list-category">
          <li><a href="https://www.cecile.co.jp/genre/g1/1/LD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">レディースファッション</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-LD-TS-1I/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">Tシャツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-LD-TS-BR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラウス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-TS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トップス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-OP/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ワンピース</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-LD-TS-TN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">チュニック</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-LD-TS-1G/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ニット・セーター</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-PN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パンツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-SK/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スカート</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-FR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スーツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-BA/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">バッグ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-SB/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">シューズ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-FG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ファッション小物</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-AC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">アクセサリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-RN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">レインウェア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LD-SW/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">水着</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">女性下着</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-BS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラジャー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-SU/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラ＆ショーツセット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-SH/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ショーツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">肌着・インナー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-BD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">補整下着</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-LN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ランジェリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ジュニア・ティーンズ下着</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-PJ/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パジャマ・ルームウェア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-ST/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ストッキング・タイツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-IN-SC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">靴下・ソックス</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/MN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">メンズファッション</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-MN-TS-1I/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">Tシャツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-MN-TS-1E/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ポロシャツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-MN-CT-JK/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ジャケット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-TS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トップス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-MN-TS-1G/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ニット・セーター</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-FR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スーツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-MN-TS-YS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ワイシャツ・カッターシャツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-PN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パンツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-BA/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">バッグ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-SB/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">シューズ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-FG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ファッション小物</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-MN-RN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">レインウェア</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/UN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">メンズ下着</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UN-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">肌着・インナー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UN-SH/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トランクス・ブリーフ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UN-PJ/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パジャマ・ルームウェア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UN-SC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">靴下・ソックス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UN-ST/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">タイツ・レギンス</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/UF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">事務服・作業服・白衣</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UF-OF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">事務服・OL制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UF-NS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ナース服・白衣</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UF-WW/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">作業着・ワークウェア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-UF-FU/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">飲食店ユニフォーム</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/SC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">制服・学生服</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-HS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">高校制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-JH/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">中学校制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-PS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">小学校制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-GL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">女子制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-BY/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">男子制服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-SC-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ジュニア・ティーンズ下着</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/s/big/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">大きいサイズ</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="/feature/lsize/lady/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">大きいサイズ レディース服</a></li>
                <li><a class="link-sub" href="/feature/lsize/inner/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">大きいサイズ レディース下着</a></li>
                <li><a class="link-sub" href="/feature/lsize/men/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">大きいサイズ メンズ</a></li>
                <li><a class="link-sub" href="/feature/lsize/office/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">大きいサイズ 事務服・制服</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/FS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">ファッション・下着すべて</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-FS-TS-1I?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">Tシャツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-TS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トップス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-FS-CT-JK/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ジャケット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-FS-TS-1G/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ニット・セーター</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-OP/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ワンピース</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-PN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パンツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-SK/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スカート</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-FR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スーツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-BS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラジャー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-SU/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラ＆ショーツセット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-SH/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ショーツ・トランクス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">肌着・インナー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-BD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">補整下着</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-LN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ランジェリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-PJ/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">パジャマ・ルームウェア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-ST/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ストッキング・タイツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-SC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">靴下・ソックス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-BA/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">バッグ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-SB/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">シューズ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-AC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">アクセサリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-FG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=appv">ファッション小物</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FS-RN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">レインウェア</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/FN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">家具・収納</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-KT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">キッチン収納・食器棚</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-CL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">衣類収納</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-CO/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">クローゼット・押入れ収納</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-OT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">収納家具・収納 その他</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-EN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">玄関収納・屋外収納</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-CH/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">チェスト・キャビネット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-LC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ラック</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-BK/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">本棚</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-TB/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">テーブル・机</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-SF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ソファー・チェアー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-TV/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">テレビ台</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-KO/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">こたつ・こたつ布団</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-KD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">学習机･子供部屋</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-DR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ドレッサー・ミラー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-FN-BU/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">仏壇・仏具</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/BD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">寝具・ベッド</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-CV/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">布団カバー・シーツ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-CL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">布団・枕</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-BL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">毛布・タオルケット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-BD/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ベッド</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-MT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">マットレス</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-BS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ベッドサイド家具・小物</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BD-CF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">安眠・快眠グッズ</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/CT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">カーテン・ラグ・ファブリック</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-CT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">カーテン</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-BL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブラインド・ロールスクリーン</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-CP/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">カーペット</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-MT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ラグ・マット類</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-CV/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">カバー類</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-TW/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">タオル</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-CS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">クッション・座布団</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-TL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トイレタリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-CT-SP/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スリッパ</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/LF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">キッチン・雑貨・日用品</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g3-1-LF-EL-1D/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">扇風機</a></li>		
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-KT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">キッチン用品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-LG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">生活雑貨</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-BT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">バス用品・ランドリー</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-EL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">家電・AV機器</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-TL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">トイレ用品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-LN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">洗濯用品・掃除道具</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-IN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">インテリア雑貨・小物</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-HG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">趣味雑貨</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-FL/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">花・ガーデニング</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-LF-GF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ギフト</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/genre/g1/1/BT/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">美容・健康・サプリメント</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-HC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ヘアケア・ボディケア</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-PF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">コスメ・ネイル・香水</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-CS/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">スキンケア化粧品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-BR/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ブランドで選ぶ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-ES/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ホームエステ</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-HF/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ダイエット・健康食品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-SP/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">サプリメント</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-SN/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">衛生用品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-HG/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">健康器具</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g2-1-BT-NC/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">シニア・介護用品</a></li>
              </ol>
            </div>
          </li>
          <li><a href="https://www.cecile.co.jp/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app" class="link-main"><span class="text">バーゲン</span></a>
            <div class="box-nav-sub">
              <ol class="list-sub-category">
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/LD/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">レディースファッション</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/IN/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">女性下着</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/MN/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">メンズファッション</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/UN/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">メンズ下着</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/UF/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">事務服・作業服・白衣</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/SC/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">制服・学生服</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/FS/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">ファッション・下着すべて</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/FN/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">家具・収納</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/BD/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">寝具・ベッド</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/CT/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">カーテン・ラグ・ファブリック</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/LF/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">キッチン・雑貨・日用品</a></li>
                <li><a class="link-sub" href="https://www.cecile.co.jp/genre/g1/1/BT/bargain/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">美容・健康・サプリメント</a></li>
              </ol>
            </div>
          </li>
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
          <a href="https://www.cecile.co.jp/card/?L=cecileapp&utm_source=cecile_dinos_apps&utm_medium=app">
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
