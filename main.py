#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import re
import os
from multiprocessing.pool import ThreadPool

from IBase import IBase

class Downloader:

    def __init__(self, url, thread_limit = 1, path = '', chapter_ranges = []):
        if re.match(r'http://manhua.dmzj.com/[a-z]+?', url):
            from Base import manhua_dmzj
            self.manga = manhua_dmzj(url)
        else:
            raise Exception("Not yet supported!")

        self.limit = thread_limit
        if len(self.manga.Details['Gropes']) > len(chapter_ranges):
            current_len = len(chapter_ranges)
            for i in range(len(self.manga.Details['Gropes']) - current_len):
                chapter_ranges.append(len(self.manga.Details['Gropes'][current_len + i]['Chapters']) - 1)

        for i in range(len(self.manga.Details['Gropes'])):
            if chapter_ranges[i] <= 0 or chapter_ranges[i] >= len(self.manga.Details['Gropes'][i]['Chapters']):
                chapter_ranges[i] = self.manga.Details['Gropes'][i]['Chapters'] - 1

        count = 0
        for grope in self.manga.Details['Gropes']:
            print('漫画 %s 的 %s 部分的章节数为 %d' % \
                  (self.manga.Details['Title'], grope['Title'], chapter_ranges[count] + 1))
            count = count + 1

        print('开始按照设定的线程数获取图片链接...')

        jobs = []
        for grope_id in range(len(self.manga.Details['Gropes'])):
            for chapter_id in range(len(self.manga.Details['Gropes'][grope_id]['Chapters'])):
                jobs.append((grope_id, chapter_id))

        pool = ThreadPool(processes=thread_limit)
        pool.map(self.fetch_imagelink, jobs)
        pool.close()
        pool.join()

    def fetch_imagelink(self, args):
        grope_id, chapter_id = args
        self.manga.GetDetails(grope_id, chapter_id)
        print('[%s] 已获取 %s : %s 的图片链接(%d)' %
              (self.manga.Details['Title'],
               self.manga.Details['Gropes'][grope_id]['Title'],
               self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Title'],
               len(self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Images']) + 1)
        )



if __name__ == '__main__':
    Downloader('http://manhua.dmzj.com/kuangduzhiyuan')
