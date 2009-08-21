#!/usr/bin/python2.5
#
# Implements a simple web-based WebFinger client.
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

import html5lib
import html5lib.treebuilders
import httplib2
import logging
import os
import re
import sys
import urllib
import webfinger

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api.memcache import Client
from xml.etree import cElementTree as etree

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# Enable a caching HTTP client
MEMCACHE_CLIENT = Client()
HTTP_CLIENT = httplib2.Http(MEMCACHE_CLIENT)

# Create a reusable HTML5 parser
ETREE_BUILDER = html5lib.treebuilders.getTreeBuilder("etree", etree)
HTML_PARSER = html5lib.HTMLParser(ETREE_BUILDER)

def sanitize(string):
  """Allow only very safe chars through."""
  return re.sub(r'[^\w\,\.\s\']', '', string)


# Abstract base class for all page view classes
class AbstractPage(webapp.RequestHandler):

  def _render_template(self, template_name, template_values={}):
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    self.response.out.write(template.render(template_path, template_values))

  def _error(self, message):
    self.redirect("/?error=%s" % urllib.quote(sanitize(message)))


# Renders the main page of the site at '/'
class MainPage(AbstractPage):

  def get(self):
    error = self.request.get('error')
    return self._render_template('main.tmpl', {'error': sanitize(error)})


# Renders the results of the lookup page
class LookupPage(AbstractPage):

  def get(self):
    identifier = self.request.get('identifier')
    client = webfinger.Client(http_client=HTTP_CLIENT)
    try:
      descriptions = client.lookup(identifier)
    except Exception, e:
      return self._error(str(e))
    template_values = dict()
    template_values['identifier'] = identifier
    template_values['descriptions'] = descriptions
    self._render_template('lookup.tmpl', template_values)


# Global application dispatcher
application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/lookup', LookupPage)],
  debug=True)


def main():
  logging.debug('Initializing.')
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  # run once
