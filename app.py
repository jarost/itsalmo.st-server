#! /usr/bin/env python

import sys
import os
import datetime
import hashlib
import time
from datetime import datetime
import json

sys.path.append("lib")
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import pymongo
from pymongo import Connection
from pymongo import json_util

connection = Connection('localhost', 27017)
db = connection.its_almost
timers = db['timers']

class ItsAlmost(tornado.web.RequestHandler):
  def get(self,id):
    timer = timers.find_one({"id": id,'expires':{'$gte':datetime.now()}})
    if timer is not None:
      timer[u'expires'] = (time.mktime(timer[u'expires'].timetuple()) * 1000)
      return self.write(json.dumps([timer],default=json_util.default));
    return self.write(json.dumps([],default=json_util.default));
    
  def post(self,id):
    timer_id = timers.insert({
      'id':id,
      'name':self.get_argument('name'),
      'expires':datetime.fromtimestamp(float(self.get_argument('expires'))/1000)
    });
    
    timer = timers.find_one({"_id": timer_id})
    if timer is not None:
      timer[u'expires'] = (time.mktime(timer[u'expires'].timetuple()) * 1000)
      return self.write(json.dumps([timer],default=json_util.default));
    return self.write(json.dumps([],default=json_util.default));

application = tornado.web.Application([
  (r"/timer/(.*)", ItsAlmost)
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()