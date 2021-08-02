# coding: utf-8

import re
import mojimoji as cnv

def join(str1,str2,split=" "):
    if str1:
        str1 += split
    str1 += str2
    
    return str1

def unicode(data):
    f = lambda d, enc: d.decode(enc)
    codecs = [
        'shift_jis','utf-8','euc_jp','cp932',
        'euc_jis_2004','euc_jisx0213','iso2022_jp','iso2022_jp_1',
        'iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext',
        'shift_jis_2004','shift_jisx0213','utf_16','utf_16_be',
        'utf_16_le','utf_7','utf_8_sig'
    ]
    for codec in codecs:
        try:
            return f(data, codec)
        except:
            continue
    return None

def utf8(data):
    data1 = to_unicode(data)
    data2 = ''
    for char in data1[:]:
        try:
            data2 += char.encode('utf-8')
        except:
            pass
    return data2

def h2z(str):
    try:
        return cnv.han_to_zen(v)
    except:
        return cnv.han_to_zen(unicode(v))

def h2z_kana(str):
    try:
        return cnv.han_to_zen(str, digit=False, ascii=False)
    except:
        return cnv.han_to_zen(unicode(str), digit=False, ascii=False)

def z2h(str):
    try:
        return cnv.zen_to_han(str)
    except:
        return cnv.zen_to_han(unicode(str))

def z2h_kana(str):
    return cnv.zen_to_han(unicode(str), digit=False, ascii=False)

def z2h_an(str):
    try:
        return cnv.zen_to_han(str, kana=False)
    except:
        return cnv.zen_to_han(unicode(str), kana=False)

def removes(chars, c):
    if chars:
        for k in c:
            chars = chars.replace(k, "")
    return chars

def changes(chars, c):
    if chars:
        for k, v in c.items():
            chars = chars.replace(k, v)
    return chars
