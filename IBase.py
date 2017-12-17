#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" DriveIt Base Interface for Python"""

from abc import ABCMeta, abstractmethod
import re
import requests
from bs4 import BeautifulSoup

class IBase(metaclass=ABCMeta):
    """ Interface for DriveIt """

    def __init__(self, pageUrl):
        self.__agent_desktop__ = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        self
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
        self.__details__ = self.GetDetails()

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

    @abstractmethod
    def GetTitle(self):
        pass


