# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 18:26:48 2016

@author: jmzhao
"""

import random

class RandomDropList :
    def __init__(self, maxsize=100) :
        self._l = list()
        self.maxsize = maxsize
    def get(self) :
        return self._l.pop(0)
    def put(self, value) :
        length = len(self._l)
        if length < self.maxsize :
            self._l.append(value)
        else :
            self._l.pop(random.randrange(0, length))
            self._l.append(value)
            