#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import os.path
import re
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.web
import tornado.websocket
import unicodedata
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

LISTENERS = []
# This defines the applications routes
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
			(r"/", IndexHandler),
            (r"/websocket", RealtimeHandler),
        ]
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": "True",
            }
        tornado.web.Application.__init__(self, handlers, **settings)

class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        LISTENERS.append(self)

    def on_message(self, message):
       JSONDict = tornado.escape.json_decode(message)
       if(JSONDict['type']==u'message'):
           for waiter in LISTENERS:
               waiter.write_message(JSONDict)
       elif(JSONDict['type']==u'color'):
           for waiter in LISTENERS:
               waiter.write_message(JSONDict)

    def on_close(self):
        LISTENERS.remove(self)

# Redirects to the Cappuccino app
class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect("/static/index.html")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

