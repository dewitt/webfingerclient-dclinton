#!/usr/bin/python2.5
#
# Implements a simple web-based WebFinger client for the dclinton strawman.
#
# Copyright 2009 DeWitt Clinton
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import imports  # Must be imported first to fix the third_party path

import logging
import os
import sys

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Hello, webapp World!')

# Global application dispatcher
application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
  logging.debug('Initializing.')
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  # run once
