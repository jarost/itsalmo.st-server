#! /usr/bin/env python2.7

import sys
import os
import datetime
import hashlib
import time
from datetime import datetime
import json
import logging
import argparse

sys.path.append("./lib")
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import pymongo
from pymongo import Connection
from pymongo import json_util

parser = argparse.ArgumentParser(description='itsAlmo.st Server.')
parser.add_argument('--port', dest='port', help='port for server to run on', default=8000)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

connection = Connection('localhost', 27017)
db = connection.its_almost
timers = db['timers']

class ItsAlmost(tornado.web.RequestHandler):
  
  def get(self,id):
    out = []
    #timer = timers.find_one({"id": id,'expires':{'$gte':datetime.now()}}, sort={'expires':-1})
    timer = timers.find_one({"id": id}, sort=[('expires',-1)])
    if timer is not None:
      timer[u'expired'] = False
      if datetime.now() > timer[u'expires']:
        timer[u'expired'] = True
      timer[u'expires'] = (time.mktime(timer[u'expires'].timetuple()) * 1000)
      out.append(timer)
    out = json.dumps(out,default=json_util.default)
    logging.info("----FETCHED " + str(id) + " : " + str(out))
    return self.write(out);
    
  def post(self,id):
    out = []
    timer = timers.find_one({"id": id,'expires':{'$gte':datetime.now()}})
    if timer is not None:
        raise tornado.web.HTTPError(400)
    print (float(self.get_argument('expires'))/1000)
    timer_id = timers.insert({
      'id':id,
      'name':self.get_argument('name'),
      'expires':datetime.fromtimestamp(float(self.get_argument('expires'))/1000)
    });
    
    new_timer = timers.find_one({"_id": timer_id})
    if new_timer is not None:
      new_timer[u'expired'] = False
      new_timer[u'expires'] = (time.mktime(new_timer[u'expires'].timetuple()) * 1000)
      out.append(new_timer)
    out = json.dumps(out,default=json_util.default)
    logging.info("++++CREATED " + str(id) + " : " + str(out))
    return self.write(out);

application = tornado.web.Application([
  (r"/timer/(.*)", ItsAlmost)
])

if __name__ == "__main__":
  application.listen(args.port)
  tornado.ioloop.IOLoop.instance().start()