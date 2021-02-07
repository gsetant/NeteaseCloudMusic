import base64
import json
import re
from io import BytesIO

import requests
from PIL import Image

from app.core.model.meta_data import MetaData
from app.core.model.Artist import Artist
from app.core.model.Album import Album
from app.plugins.NeteaseCloudMusic import config
from app.plugins.NeteaseCloudMusic.config import get_info
from app.tools.cache_tools import check_cache
from app.tools.log_tools import log
import urllib
import datetime

# 需要使用一下地址的项目作为API服务 https://github.com/Binaryify/NeteaseCloudMusicApi
# API address
url = 'http://127.0.0.1:3000'

MATCH_NAME = 3
MATCH_ARTIST = 2
MATCH_ALBUM = 1
MATCH_SCORE = 4


def search(meta_info, user_setting):
    score = MATCH_SCORE
    plugin_name = config.get_info('en').get('name')
    meta_data_list = []
    if meta_info.get('media_type') == 'album':
        if meta_info.get('name'):
            file_name = meta_info.get('name')
            score = MATCH_ALBUM
        else:
            file_name = clear_file_name(meta_info.get('file_name'))
    elif meta_info.get('media_type') == 'artist':
        if meta_info.get('file_name'):
            file_name = clear_file_name(meta_info.get('file_name'))
        else:
            file_name = ''
            score = MATCH_ARTIST
    else:
        return meta_data_list

    log('info', 'title:%s' % file_name, plugin_name)
    code = get_code(file_name, meta_info)
    result = None
    cache_data = check_cache(code, get_info('en').get('name'))
    if cache_data:
        return cache_data
    else:
        # search for meta data from internet
        results = search_song_by_code(code)
        sort_result(results, code)
        highest_result = get_highest_result(results)
        if not highest_result:
            return meta_data_list
        if highest_result.get('score') >= score:
            result = highest_result
    if not result:
        return meta_data_list
    get_artist_info(result)
    get_album_info(result)
    meta_data = MetaData()

    # Album
    album = Album()
    album.title = result.get('album').get('name')
    album.summary = result.get('album').get('description')
    album.studio = result.get('album').get('company')
    album.tags = result.get('album').get('tags')
    album.collections = result.get('album').get('subType')
    album.poster = get_picture_base64(result.get('album').get('picUrl'))
    album.originally_available_at = datetime.datetime.fromtimestamp(
        result.get('album').get('publishTime') / 1000).strftime('%Y-%m-%d')
    meta_data.album = album

    # Artist
    for result_artist in result.get('artists'):
        artist = Artist()
        artist.poster = get_picture_base64(result_artist.get('cover'))
        artist.art = get_picture_base64(result_artist.get('cover'))
        title = result_artist.get('name')
        if title == 'Various Artists' or title == '[Unknown Artist]':
            title = '未知艺术家'
        artist.title = title
        if result_artist.get('identifyTag'):
            artist.tags = ','.join(result_artist.get('identifyTag'))
        artist.summary = ''
        if result_artist.get('briefDesc'):
            artist.summary = result_artist.get('briefDesc')
        if result_artist.get('rank'):
            rank = result_artist.get('rank')
            rank_type = ['', '华语', '欧美', '韩国', '日本']
            rank_string = '\n歌手排行：' + str(rank_type[rank.get('type')]) + '地区：' + str(rank.get('rank'))
            artist.summary += rank_string
        if result_artist.get('albumSize'):
            artist.summary += '\n歌手专辑数：' + str(result_artist.get('albumSize'))
        if result_artist.get('musicSize'):
            artist.summary += '\n歌手音乐数：' + str(result_artist.get('musicSize'))
        if result_artist.get('mvSize'):
            artist.summary += '\n歌手MV数：' + str(result_artist.get('mvSize'))
        meta_data.artist.append(artist)
    meta_data.code = code
    meta_data_list.append(meta_data)
    return meta_data_list


def get_picture_base64(pic_url):
    if not pic_url:
        return config.get_info('en').get('icon')
    response = requests.get(pic_url)
    img = Image.open(BytesIO(response.content))
    output_buffer = BytesIO()
    img = img.convert('RGB')
    img.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str.decode("utf-8")


def clear_file_name(file_name):
    name = urllib.parse.unquote(file_name).split('/')[-1]
    if 'Various Artists' in name:
        name = name.replace('Various Artists', '')
    if '[Unknown Artist]' in name:
        name = name.replace('[Unknown Artist]', '')
    extend = name.split('.')[-1]
    name = name.replace('.' + extend, '')
    return name


def get_code(name, meta_info):
    code = name + ' '
    a = re.findall(r'[^.-]', code, re.S)
    code = "".join(a)
    if meta_info.get('index'):
        index = int(meta_info.get('index'))
        if index < 10:
            if '0' + str(index) in code:
                code = code.replace('0' + str(index), '')
        else:
            code = code.replace(str(index), '')
    if meta_info.get('artist') and meta_info.get('artist') != 'Various Artists' and meta_info.get(
            'artist') != '[Unknown Artist]':
        code += meta_info.get('artist') + " "
    if meta_info.get('album') and meta_info.get('album') != '[Unknown Album]':
        code += meta_info.get('album') + " "
    if meta_info.get('track'):
        code += meta_info.get('track') + " "
    return code


def search_song_by_code(code):
    uri = '/search?keywords=' + code
    return netease_api(uri).get('result').get('songs')


def sort_result(results, code):
    for result in results:
        score = 0
        if result.get('name') in code:
            score += MATCH_NAME
        if result.get('album').get('name') in code:
            score += MATCH_ALBUM
        artists = result.get('artists')
        for artist in artists:
            if artist.get('name') in code:
                score += MATCH_ARTIST
        result['score'] = score


def get_highest_result(results):
    highest_result = None
    score = 0
    for result in results:
        if result.get('score') > score:
            highest_result = result
            score = result.get('score')
    return highest_result


def get_artist_info(result):
    artists = []
    for artist in result.get('artists'):
        uri = '/artist/detail?id=' + str(artist.get('id'))
        artist_info = netease_api(uri).get('data')
        if artist_info:
            artists.append(artist_info.get('artist'))
    result['artists'] = artists


def get_album_info(result):
    uri = '/album?id=' + str(result.get('album').get('id'))
    result['album'] = netease_api(uri).get('album')


def netease_api(uri):
    query_url = url + uri
    try:
        respond = requests.post(query_url)
        meta_data_list = json.loads(respond.content)
        return meta_data_list
    except Exception:
        return []
