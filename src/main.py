# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 17:40:40 2016

@author: jmzhao
"""

import os
import sys
import random
import crawl

def main() :
    db_dirname = './data/'
    try :
        os.mkdir(db_dirname)
    except FileExistsError :
        pass
    get_web_req_gap = (eval('lambda : ' + sys.argv[1]) if len(sys.argv)>1 
        else lambda : random.uniform(1,3))

    try :
        crawl.init(db_dirname + 'db.tinydb', get_web_req_gap)
        crawl.authorize()
        crawl.crawl(seeds=crawl.url2json('https://api.github.com/users'))
    except Exception as e :
        crawl.cleanup()
        raise e

if __name__ == '__main__' :
    main()