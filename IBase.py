#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" DriveIt Base Interface for Python"""

from abc import ABCMeta, abstractmethod
import re
import os
import requests
from bs4 import BeautifulSoup

class IBase(metaclass=ABCMeta):
    """ Interface for DriveIt """

    def __init__(self, pageUrl):
        self.__agent_desktop__ = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        self.__url__ = pageUrl
        if re.match(r'http://www.dmzj.com/info/.+?.html', pageUrl):
            self.__site__ = 'dmzj'
        if re.match(r'http://manhua.dmzj.com/[a-z]+?', pageUrl):
            self.__site__ = 'manhua_dmzj'
        else:
            self.__site__ = 'None'

        self.__page_source__ = self.GetData(pageUrl).decode("utf-8")
        self.__soup__ = BeautifulSoup(self.__page_source__, 'html.parser')
        self.__title__ = self.GetTitle()
        self.__chapters__ = self.GetChapters()
        self.__author__ = 'DriveIt'
        self.__summary__ = 'Downloaded by DriveIt\nhttps://github.com/Oyami-Srk/DriveIt'
        self.__details__ = {
            'Title': self.__title__,
            'Author': self.__author__,
            'Summary': self.__summary__,
            'Gropes': []
        }
        for chapters in self.__chapters__:
            chaps = []
            for chapter in chapters[1]:
                chaps.append({'Title': chapter[0], 'Link': chapter[1], 'Images': []})
            self.__details__['Gropes'].append({'Title': chapters[0], 'Chapters':chaps})
            self.Details = self.__details__

    def __str__(self):
        return '< manga \"%(title)s\" on %(site)s >' % \
            {'title': self.__title__, 'site': self.__site__ }

    def GetData(self, url, referrer='', platform='desktop'):
        header = {
            'User-Agent': '',
            'Referer': referrer,
            'Accept-Encoding': 'gzip, deflate, sdch'
        }
        if platform == 'desktop':
            header['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        elif platform == 'mobile':
            header['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'

        return requests.get(url, headers=header).content

    def RemoveChar(self, str, list=['\n', '\\', '*', '?', '<', '>', '|', ':', '"']):
        for c in list:
            str = str.replace(c, '')
        return str

    def MakeDir(self, path_set, parent = ''):
        if parent != '':
            Path = os.path.join(parent)
        else:
            Path = ''
        for dir in path_set:
            Path = os.path.join(Path, self.RemoveChar(dir))
        if not os.path.exists(Path):
            try:
                os.makedirs(Path)
            except FileExistsError as e:
                pass
        return Path

    @abstractmethod
    def GetTitle(self):
        pass

    @abstractmethod
    def GetChapters(self):
        pass

    @abstractmethod
    def GetChapterDetail(self, chapter):
        pass

    @abstractmethod
    def GetDetails(self, grope_id, chapter_id):
        pass

    @abstractmethod
    def DownloadImage(self, grope_id, chapter_id, image_id, parent=''):
        pass

    @abstractmethod
    def GetCover(self, path=''):
        pass


