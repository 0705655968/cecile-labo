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
LOCAL_IMAGE_PATH = '/opt/app/cecile/data'
CECILE_HOST = 'https://www.cecile.co.jp'
CATALOG_HOME = CECILE_HOST + '/digicata/'
DEGITAL_CATALOG_HOME = CECILE_HOST + '/fst/digicata/'
MAX_ROWS = 1000

# コーディネート例商品一覧データの作成
def update_coordinate_photo_master():
    max_pages = ItemImages.objects.filter(introduction__contains='コーディネート例').count()
    for offset in range(0, max_pages, MAX_ROWS):
        limit = offset + MAX_ROWS
        item_lists = ItemImages.objects.filter(introduction__contains="コーディネート例").order_by("-id")[offset:limit]
        for data in item_lists:
            try:
                content = web.get('https://www.cecile.co.jp/detail/'+data.item+'/')
                html = parser.content(content["src"])
                item_name = parser.string(parser.attr(html, "h1", ["class", "title"]))
                if item_name:
                    CoordinatePhotoMaster(
                        item = data.item,
                        name = str(item_name),
                        image = data.image,
                        local = data.local,
                        ).save()
                web.stop(1)
#                break
            except: pass
#            break


# カタログページの商品データの作成
def create_catalog_Page_items():
    max_pages = CatalogPages.objects.filter(status='1').count()
    for offset in range(0, max_pages, MAX_ROWS):
        limit = offset + MAX_ROWS
        catlg_pages = CatalogPages.objects.filter(status='1').order_by("-id")[offset:limit]
        for data in catlg_pages:
            # 既にページ情報を取得している場合は処理しない
            print(data.catalog, ' > ', data.page)
            if CatalogPageItems.objects.filter(catalog = data.catalog, page = data.page).count() == 0:
                content = web.get(data.url)
                html = parser.content(content["src"])
                block = parser.attr(html, "ul", ["class", "itemlist"])
                items = parser.tag(block, "li", 1)
                for item in items:
                    # 商品の基礎情報
                    url = parser.string(parser.attribute(parser.tag(item, "a"), "href"))
                    name = parser.string(parser.attribute(parser.tag(item, "img"), "alt"))
                    temp = parser.string(parser.attr(item, "p", ["class", "item-code"])).strip().split('-')
                    code = temp[0]
                    try:
                        prm = parser.query(str(url))
                        order = prm['appno'][0]
                        temp = url.split('/')
                        itemcd = temp[4]
                    except:
                        # 商品ページURLが無いケースがある
                        temp_order = temp[1].split('(')
                        order = temp_order[0].strip()
                        temp = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
                        itemcd = os.path.splitext(os.path.basename(temp))[0]
                        url = 'https://www.cecile.co.jp/detail/'+ itemcd +'/'
                    # 商品ページから、商品画像一覧とコーディネート情報を取得する
                    cmdty = web.get(url)
                    item_html = parser.content(cmdty["src"])
                    coordinatelist = parser.attr(item_html, "ul", ["class", "coordinatelist"])
                    coordinate = 0
                    if coordinatelist:
                        coordinate = 1
                        # コーディネート情報を取得
                        corde_list = parser.tag(coordinatelist, "li", 1)
                        for corde in corde_list:
                            corde_img = parser.tag(corde, "img")
                            corde_url = parser.string(parser.attribute(parser.tag(corde, "a"), "href"))
                            corde_image = parser.string(parser.attribute(corde_img, "src"))
                            corde_local = corde_image.replace(CECILE_HOST, LOCAL_IMAGE_PATH)
                            corde_name = parser.string(parser.attribute(corde_img, "alt"))
                            corde_id = os.path.splitext(os.path.basename(corde_local))[0]
                            # 特集名の取得
                            styles = {'style1':'', 'style2':'', 'style3':''}
                            scdata = web.get(corde_url)
                            sc_html = parser.content(scdata["src"])
                            sc_block = parser.attr(sc_html, "div", ["id", "breadclumb"])
                            breadclumb_lists = parser.tag(sc_block, "li", 1)
                            n = 0
                            for breadclumb in breadclumb_lists:
                                if n > 1:
                                    try:
                                        anker = parser.tag(breadclumb, "a")
                                        if anker:
                                            styles['style' + str(n - 1)] = parser.html_string(html=anker)
                                            # コーディネートスタイルをマスタに登録
                                            if CoordinateStyle.objects.filter(style = styles['style' + str(n - 1)]).count() == 0:
                                                CoordinateStyle(style = styles['style' + str(n - 1)]).save()
                                    except: pass
                                n += 1
                            # コーディネートマスタに登録
                            if CoordinateMaster.objects.filter(coordinate = corde_id).count() == 0:
                                r = common.photo(url=corde_image, local=corde_local)
                                if r['rslt']:
                                    CoordinateMaster(
                                            coordinate = corde_id,
                                            name = corde_name,
                                            image = corde_image,
                                            local = corde_local,
                                            url = corde_url,
                                            style1 = styles['style1'],
                                            style2 = styles['style2'],
                                            style3 = styles['style3'],
                                        ).save()
                            # コーディネートと商品のリンクテーブルの作成
                            items_block = parser.attr(sc_html, "div", ["class", "detail"])
                            corde_block = parser.tag(items_block, "ul")
                            corde_lists = parser.tag(corde_block, "li", 1)
                            for detail in corde_lists:
                                temp = parser.string(parser.attribute(parser.tag(detail, "a"), "href")).split('/')
                                item_code = temp[2]
                                # データを登録する
                                if CoordinateItemLink.objects.filter(coordinate = corde_id, item = item_code).count() == 0:
                                    CoordinateItemLink(
                                            coordinate = corde_id,
                                            item = item_code,
                                        ).save()
                    
                    if CatalogPageItems.objects.filter(catalog = data.catalog, page = data.page, item = str(itemcd)).count() == 0:
                        CatalogPageItems(
                                catalog = data.catalog,
                                page = data.page,
                                item = str(itemcd),
                                code = code,
                                order = order,
                                name = name,
                                url = url,
                                coordinate = coordinate,
                            ).save()
                        
                        # 商品情報に画像が登録されている場合は処理しない
                        if ItemImages.objects.filter(item = str(itemcd)).count() == 0:
                            # 画像データの取得
                            image_blocks = parser.attr(item_html, "ul", ["class", "sliderthumbs"])
                            images = parser.tag(image_blocks, "img", 1)
                            for img in images:
                                try:
                                    introduction = parser.string(parser.attribute(img, "alt"))
                                except:
                                    introduction = ''
                                img_src = parser.string(parser.attribute(img, "src"))
                                img_url = CECILE_HOST + img_src
                                img_local = LOCAL_IMAGE_PATH + img_src
                                r = common.photo(url=img_url, local=img_local)
                                if r['rslt']:
                                    ItemImages(
                                            item = str(itemcd),
                                            image = img_url,
                                            local = img_local,
                                            introduction = introduction,
                                        ).save()
                    web.stop(1)
                web.stop(1)

# カタログデータの作成
def create_catalog_data():
    catlg = CatalogMaster.objects.filter(status='1').order_by("-id")
    for data in catlg:
        # カタログページのデータが登録されていない場合のみ処理
        if CatalogPages.objects.filter(catalog = data.catalog).count() == 0:
            # データの取得
            content = web.get(DEGITAL_CATALOG_HOME + data.catalog +'/index/contents.xml')
            xml = parser.xml(content['src'].decode('utf-8'))
            total_pages = int(xml['libook']['configration']['totalPages'])
            # ページ単位での処理
            for page in range(0, total_pages):
                page_zero = str(page).zfill(4)
                page_url = CECILE_HOST + '/site/cmdtyinfo/digicata/ListSrv.jsp?micd='+ data.catalog +'&pgno=' + str(page)
                images = {'rslt':True, 'image1':'', 'image2':'', 'local1':'', 'local2':''}
                for num in range(0, 2):
                    clmn = str(num + 1)
                    images['image' + clmn] = 'https://dc.cecile.co.jp/'+ data.catalog +'/img/'+ page_zero +'/200_'+ str(num) +'.jpg'
                    images['local' + clmn] = LOCAL_IMAGE_PATH + '/catalog/'+ data.catalog +'/img/'+ page_zero +'/200_'+ str(num) +'.jpg'
                    r = common.photo(url=images['image' + clmn], local=images['local' + clmn])
                    if not r['rslt']:
                        images['rslt'] = False
                    web.stop(0.5)

                # DBに登録が無ければ処理
                if CatalogPages.objects.filter(catalog = data.catalog, page = str(page)).count() == 0:
                    if images['rslt']:
                        CatalogPages(
                                catalog = data.catalog,
                                page = str(page),
                                image1 = images['image1'],
                                image2 = images['image2'],
                                local1 = images['local1'],
                                local2 = images['local2'],
                                url = page_url,
                            ).save()
                web.stop(1)
        web.stop(1)

# カタログデータの取得
def create_catalog_from_bat():

    # カタログ一覧の取得
    # セシールサイトからカタログ一覧の取得と、カタログ表紙の画像を取得
    # カタログジャンルマスタの作成とリンクテーブルのデータ作成も行う
    data = web.get(CATALOG_HOME)
    html = parser.content(data["src"])
    blocks = parser.attr(html, "div", ["class", "catalog"], 1)
    try:
        for block in blocks:
            try:
                title = parser.string(parser.tag(block, "h2"))
                items = parser.tag(block, "li", 1)
                for item in items:
                    name = parser.string(parser.tag(item, "span"))
                    image = parser.tag(item, "img")
                    image_src = parser.string(parser.attribute(parser.tag(item, "img"), "src"))
                    code = os.path.splitext(os.path.basename(image_src))[0]
                    introduction = parser.html_string(html=parser.tag(item, "dd"), brnl=True)
#                    print(' ', code, name, image_src)
                    catalog_url = 'https://www.cecile.co.jp/fst/digicata/'+code+'/index/contents.xml'
                    xml_path = '/opt/app/cecile/data/xml/'+code+'.xml'
                    r = common.xml(url=catalog_url, local=xml_path)
                    web.stop(0.5)

                    if CatalogMaster.objects.filter(catalog = code).count():
                        catalog_master = CatalogMaster.objects.get(catalog = code)
                        catalog_master.name = name
                        catalog_master.genre = title
                        catalog_master.introduction = introduction
                    else:
                        image_url = CECILE_HOST + image_src
                        local_path = LOCAL_IMAGE_PATH + date.now_datefmt('/%Y/%m/%d') + image_src
                        print(image_url)
                        r = common.photo(url=image_url, local=local_path)
                        if r['rslt']:
                            catalog_master = CatalogMaster(
                                                catalog = code,
                                                name = name,
                                                introduction = introduction,
                                                image = image_url,
                                                local = local_path,
                                                url = DEGITAL_CATALOG_HOME + code +'/',
                                                )
                            catalog_master.save(using='default')
                            if CatalogGenre.objects.filter(name = title).count() == 0:
                                CatalogGenre(name = title).save()
                            if CatalogGenreLink.objects.filter(genre = title, catalog = code).count() == 0:
                                CatalogGenreLink(genre = title, catalog = code).save()
            except: pass
    except: pass
