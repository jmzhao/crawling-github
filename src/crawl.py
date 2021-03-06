# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 17:50:50 2016

@author: jmzhao
"""

import json
import tinydb
import myqueue
import random
import time
import requests
import getpass


user_interested_keys = ('id', 'login', 'url', 'repos_url')
repo_interested_keys = ('id', 'name', 'full_name', 'url', 'contributors_url')

username = None
password = None
db = None
db_filename = './data/db.tinydb'
get_web_req_gap = (lambda : random.uniform(1,3))
Queue = myqueue.RandomDropList

def authorize() :
    global username, password
    while True :
        try :
            username = input("GitHub username:")
            password = getpass.getpass()
            res = requests.get("https://api.github.com/users/" + username, 
                auth=(username, password))
        except Exception as e :
            print(e)
            continue
        print(res)
        if res.ok :
            break
        
def init(ndb_filename, nget_web_req_gap, nQueue=myqueue.RandomDropList) :
    global db, db_filename, get_web_req_gap, Queue
    db_filename = ndb_filename
    get_web_req_gap = nget_web_req_gap
    db = tinydb.database.TinyDB(db_filename)
    Queue = nQueue

def user_node_for_store(node) :
    return dict((k, node.get(k)) for k in user_interested_keys)
def repo_node_for_store(node) :
    return dict((k, node.get(k)) for k in repo_interested_keys)

def url2json(url) :
    print('requerying:', url)
    t = get_web_req_gap()
    print('hold for %fs...'%t, end=' ', flush=True)
    time.sleep(t)
    print('hold cleared.', end=' ', flush=True)
    res = requests.get(url, auth=(username, password))
#   res = urllib.request.urlopen(url)
    print('done.', end=' ', flush=True)
    print('Remaining/Limit=%s/%s'%(
        res.headers.get('X-RateLimit-Remaining'), 
        res.headers.get('X-RateLimit-Limit')))
    obj = json.loads(res.text)
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
    try :
        j = url2json(repo["contributors_url"])
        return j if type(j) == list else []
    except Exception as e :
        print(e)
        rest(10)
        return []

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

def rest(t) :
    print(time.ctime() + ':', 'now rest for %ds'%t, flush=True)
#    db.close()
    time.sleep(t)
    print(time.ctime() + ':', 'resumed', flush=True)
    

def crawl(seeds, max_queue_size=100) :
    q = Queue(maxsize=max_queue_size)
    for seed in seeds :
        q.put(seed2node(seed))
    while not is_enough() :
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

def cleanup() :
    db.close()