#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import os
import sys
from multiprocessing.pool import ThreadPool

from IBase import IBase

class Downloader:

    def __init__(self, url, thread_limit = 1, path = '', chapter_ranges = [], disp=True):
        if re.match(r'http://manhua.dmzj.com/[a-z]+?', url):
            from Base import manhua_dmzj
            self.manga = manhua_dmzj(url)
        else:
            raise Exception("Not yet supported!")

        self.limit = thread_limit
        if len(self.manga.Details['Gropes']) > len(chapter_ranges):
            current_len = len(chapter_ranges)
            for i in range(len(self.manga.Details['Gropes']) - current_len):
                chapter_ranges.append(len(self.manga.Details['Gropes'][current_len + i]['Chapters']))
        self.skip = []
        for i in range(len(self.manga.Details['Gropes'])):
            if chapter_ranges[i] == 0 or chapter_ranges[i] > len(self.manga.Details['Gropes'][i]['Chapters']):
                chapter_ranges[i] = len(self.manga.Details['Gropes'][i]['Chapters'])
            elif chapter_ranges[i] < 0:
                self.skip.append(i)
                chapter_ranges[i] = 0

        if disp:
            count = 0
            for grope in self.manga.Details['Gropes']:
                print('漫画 %s 的 %s 部分将要获取的章节数为 %d' % \
                  (self.manga.Details['Title'], grope['Title'], chapter_ranges[count]))
                count = count + 1
        self.ranges = chapter_ranges
        self.disp = disp
        self.parent = path

    def Fetch_Details(self):
        if self.disp:
            print('开始按照设定的线程数获取图片链接...')
        jobs = []
        for grope_id in range(len(self.manga.Details['Gropes'])):
            if self.skip != []:
                if grope_id in self.skip:
                    continue;
            chapter_count = len(self.manga.Details['Gropes'][grope_id]['Chapters'])
            for chapter_id in range(chapter_count - self.ranges[grope_id], chapter_count):
                jobs.append((grope_id, chapter_id))

        pool = ThreadPool(processes=self.limit)
        pool.map(self.fetch_imagelink, jobs)
        pool.close()
        pool.join()
        if self.disp:
            print('图片链接已获取')

    def Download(self):
        if self.disp:
            print('下载开始...')
        jobs = []
        for grope_id in range(len(self.manga.Details['Gropes'])):
            if self.skip != []:
                if grope_id in self.skip:
                    continue;
            chapter_count = len(self.manga.Details['Gropes'][grope_id]['Chapters'])
            for chapter_id in range(chapter_count - self.ranges[grope_id], chapter_count):
                for image_id in range(len(self.manga.Details['Gropes'][grope_id]\
                                          ['Chapters'][chapter_id]['Images'])):
                    jobs.append((grope_id, chapter_id, image_id))
        pool = ThreadPool(processes=self.limit)
        pool.map(self.fetch_image, jobs)
        pool.close()
        pool.join()
        if self.disp:
            print('下载完成')

    def DownloadCover(self):
        self.manga.GetCover(self.parent)

    def fetch_image(self, args):
        grope_id, chapter_id, image_id = args
        if self.manga.DownloadImage(grope_id, chapter_id, image_id, self.parent):
            if self.disp:
                print('[%s] (%s) 已获取 %s 的第 %d 张图片' %
                      (self.manga.Details['Title'],
                       self.manga.Details['Gropes'][grope_id]['Title'],
                       self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Title'],
                       image_id + 1)
                )
        elif self.disp:
            print('[%s] (%s) 已存在 %s 的第 %d 张图片 - 跳过下载' %
                  (self.manga.Details['Title'],
                   self.manga.Details['Gropes'][grope_id]['Title'],
                   self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Title'],
                   image_id + 1)
            )

    def fetch_imagelink(self, args):
        grope_id, chapter_id = args
        self.manga.GetDetails(grope_id, chapter_id)
        if self.disp:
            print('[%s] (%s) 已获取 %s 的图片链接(%d)' %
                  (self.manga.Details['Title'],
                   self.manga.Details['Gropes'][grope_id]['Title'],
                   self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Title'],
                   len(self.manga.Details['Gropes'][grope_id]['Chapters'][chapter_id]['Images']) + 1)
            )


def argparser():
    parser = argparse.ArgumentParser(description='A multithreading comic crawler.')
    parser.add_argument('url', help='URL of the comic\'s cover page', nargs='?', default = '')
    parser.add_argument('-l', '--latest', help='Download latest x chapters to each grope from origin.\n0 means all chapters, -1 means ignore this grope. \nDefault to be a list filled with 0.', nargs='*', type=int, default = [])
    parser.add_argument('-t', '--thread', help='Number of threads. Default to be 1', type=int, default=1)
    parser.add_argument('-p', '--path', help='Path of saving comic', type=str, default='')
    parser.add_argument('-d', '--details', help='Output Details in json', action="store_true", default=False)
    parser.add_argument('-x', '--suicide', help='Delete this script', action="store_true", default=False)
    parser.add_argument('-s', '--silent', help='Do not display output', action="store_true", default=False)
    return parser


if __name__ == '__main__':
    import argparse
    parser = argparser()
    args = parser.parse_args()
    isdisp = True
    if args.suicide:
        import shutil
        shutil.rmtree(os.getcwd())
        sys.exit(0)

    if args.details or args.silent:
        isdisp = False

    if args.url == '':
        print('Url is required!')
        sys.exit(0)
    a = Downloader(args.url, chapter_ranges=args.latest, path=args.path, thread_limit=args.thread, disp=isdisp)
    a.Fetch_Details()

    if args.details:
        import json
        details = a.manga.Details
        print(json.dumps(details, indent=4))
        sys.exit(0)

    a.Download()
    a.DownloadCover()

