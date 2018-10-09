# -*- coding: utf-8 -*-
from urllib import parse
from bwg360.controllers.dlFiles.youtubeDL import YoutubeDL
from bwg360.controllers.dlFiles.yunfileDL import YunfileDL
from bwg360.controllers.dlFiles.youtubeDL import YoutubeDL


_support_urls = {'page2.dfpan.com': YunfileDL}


def make_file_dl(file_url,  test_support=True):
    url = parse.urlparse(file_url)
    base_dl = _support_urls.get(url.netloc)
    if base_dl:
        return base_dl(file_url, url.netloc)
    else:
        ydl = YoutubeDL(file_url)                  # 除指定的DL外，其他默由youtube-dl负责
        if test_support:                           # 是否测试youtube-dl支持与否
            if ydl.is_support():                   # will block，fetch video information
                return ydl
            return None
        else:
            return ydl


def list_custom_support_site():
    return _support_urls.keys()
