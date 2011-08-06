#! /usr/bin/env python

import sys
import os
import datetime
import hashlib

sys.path.append("lib")
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import pymongo
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection.its_almost
timers = db['timers']

class ItsAlmost(tornado.web.RequestHandler):
  def get(self,id):
    timer = timers.find_one({"id": id})
    if timer is not None:
      return self.write(tornado.escape.json_encode(timer));
    raise tornado.web.HTTPError(404)
    
  def post(self):
    print(self)
    self.write("Thanx")

application = tornado.web.Application([
  (r"/timer", ItsAlmost),
  (r"/timer/(.*)", ItsAlmost)
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()