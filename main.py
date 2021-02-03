from app.core.model.meta_data import MetaData
from app.plugins.plugin_demo import config
from app.plugins.plugin_demo.config import get_info
from app.tools.cache_tools import check_cache
from app.tools.log_tools import log


def search(meta_info, user_setting):
    plugin_name = config.get_info('en').get('name')
    meta_data_list = []
    video_title = meta_info.get('video_title')
    part_file = meta_info.get('part_file')
    movie_type = ''
    title_style = ''
    log('info', 'title:%s' % video_title, plugin_name)

    # code is the formatted media name which is used to check if it is already in cache
    code = 'formatted file name'
    cache_data = check_cache(code, get_info('en').get('name'))
    if cache_data:
        meta_data_list.append(cache_data)
    else:
        # search for meta data from internet
        meta_data = MetaData()
        meta_data_list.append(meta_data)
    return meta_data_list
