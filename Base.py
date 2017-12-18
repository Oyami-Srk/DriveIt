#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" DriveIt Base Class for Python"""

from IBase import IBase

import requests
import os
import re
from bs4 import BeautifulSoup
import execjs
import json

class manhua_dmzj(IBase):
    """ Base Class for DriveIt to manhua_dmzj """

    def __init__(self, pageUrl):
        IBase.__init__(self, pageUrl)
        #

    def GetTitle(self):
        soup_box = self.__soup__.findAll('h1')
        for border in soup_box:
            Title = border.text
        return Title

    def GetChapters(self):
        Chapters = []
        soup_box = self.__soup__.findAll('div', class_=re.compile('cartoon_online_border.*'))
        for border in soup_box:
            Details = []
            for li in border.findAll('li'):
                link = li.a['href']
                title = self.RemoveChar(li.text)
                Details.append((title, link))
            Chapters.append((Details))
            soup_box = self.__soup__.findAll('div', class_=re.compile('middleright_mr.*'))[0] \
                                    .findAll('div', class_=re.compile('photo_part.*'))
        ChaptersDetails = []
        count = 0
        for border in soup_box:
            ChaptersDetails.append((self.RemoveChar(border.h2.text, [' 漫画其它版本', ' 在线漫画全集']),
                                    Chapters[count]))
            count = count + 1
        return ChaptersDetails

    def GetChapterDetail(self, chapter):
        ChapterPage = self.GetData('http://manhua.dmzj.com%s' % chapter[1]).decode('utf-8')
        ChapterSoup = BeautifulSoup(ChapterPage, 'html.parser')
        ChapterScript = ChapterSoup.find('script', {'type': 'text/javascript'}).text \
                                                                               .split('\n')[3] \
                                                                               .strip().replace('eval(', '')[:-1]
        result = execjs.eval(ChapterScript)
        return json.loads(result.replace('var pages=pages=\'', '').rstrip('\';'))

    def GetDetails(self, grope_id, chapter_id):
        self.__details__['Gropes'][grope_id]['Chapters'][chapter_id]['Images'] = self.GetChapterDetail(self.__chapters__[grope_id][1][chapter_id])

    def DownloadImage(self, grope_id, chapter_id, image_id, parent=''):
        url = 'http://images.dmzj.com/' + \
              self.__details__['Gropes'][grope_id]['Chapters'][chapter_id]['Images'][image_id]
        filename = self.MakeDir((self.__details__['Title'],
                                 self.__details__['Gropes'][grope_id]['Title'],
                                 self.__details__['Gropes'][grope_id]['Chapters'][chapter_id]['Title']), parent) +\
                                 '/' + str(image_id) + '.' + url.split('.')[-1]
        if os.path.exists(filename):
            return False
        img = self.GetData(url, 'http://manhua.dmzj.com' + self.__details__['Gropes'][grope_id]['Chapters'][chapter_id]['Link'])
        with open(filename, 'wb+') as file:
            file.write(img)
        return True

    def GetCover(self, path=''):
        img_link = self.__soup__.findAll('div', class_=re.compile('anim_intro_ptext.*'))[0].img['src']
        img = self.GetData(img_link, 'http://manhua.dmzj.com/')
        with open(self.MakeDir((self.__details__['Title'], ''), path) + 'cover' + '.' + img_link.split('.')[-1], 'wb+') as file:
            file.write(img)

