#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" DriveIt Base Class for Python"""

from IBase import IBase

import requests

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

    def GetDetails(self):
        pass

