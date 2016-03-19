# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 17:40:40 2016

@author: jzhao
"""

import urllib.request
import json
import tinydb
import queue
import random
import time
import os


user_interested_keys = ('id', 'login', 'url', 'repos_url')
repo_interested_keys = ('id', 'name', 'full_name', 'url', 'contributors_url')


try :
    os.mkdir('../data/')
except FileExistsError :
    pass
db = tinydb.database.TinyDB('../data/db.tinydb')

def user_node_for_store(node) :
    return dict((k, node.get(k)) for k in user_interested_keys)
def repo_node_for_store(node) :
    return dict((k, node.get(k)) for k in repo_interested_keys)

def url2json(url) :
    print('requerying:', url)
    t = random.random() * 10
    print('hold for %fs...'%t, end=' ', flush=True)
    time.sleep(t)
    print('hold cleared.', end=' ', flush=True)
    res = urllib.request.urlopen(url)
    print('done.')
    obj = json.loads(res.read().decode('utf-8'))
    return obj

def seed2node(seed) :
    node = url2json('https://api.github.com/users/' + seed['login'])
    return node

def generate_next_nodes(node) :
    ''' generate a sequence of reachable nodes
    
    raises: 
      random.choice - IndexError('Cannot choose from an empty sequence')
    '''
    repo_node_list = url2json(node['repos_url'])
    repo = random.choice(repo_node_list)
    return url2json(repo["contributors_url"])

def store(node) :
    print('storing:', 'User:' + node.get('login'))
    db.table('User').insert(user_node_for_store(node))
    repo_node_list = url2json(node['repos_url'])
    print('storing:', 'Repo:' + node.get('login') + '/*', 
        '(%d repos in total)'%(len(repo_node_list)))
    db.table('Repo').insert_multiple([repo_node_for_store(n) for n in repo_node_list])
    
def is_visited(node) :
    return db.table('User').contains(tinydb.Query().id == node.get('id'))

def is_enough() :
    return False
#    return len(db.table('Repo'))>1000

def rest() :
    t = random.randrange(60, 100)
    print(time.ctime() + ':', 'now rest for %ds'%t, flush=True)
#    db.close()
    time.sleep(t)
    print(time.ctime() + ':', 'resumed', flush=True)
    

def crawl(seeds=url2json('https://api.github.com/users'), max_queue_size=100) :
    q = queue.Queue(maxsize=max_queue_size)
    for seed in seeds :
        q.put(seed2node(seed))
    while not is_enough() :
        rest()
        node = q.get()
        print('crawling:', 'User:' + node.get('login'))
        if not is_visited(node) :
            store(node)
        try :
            nnode = random.choice(generate_next_nodes(node)) 
        except IndexError :
            continue
        if not is_visited(nnode) :
            q.put(nnode)
            
if __name__ == '__main__' :
    try :
        crawl()
    except Exception as e :
        db.close()
        raise e
