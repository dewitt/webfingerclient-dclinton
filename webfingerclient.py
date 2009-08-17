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

import email.utils
import html5lib
import html5lib.treebuilders
import httplib2
import logging
import os
import re
import sys
import urllib

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api.memcache import Client
from xml.etree import cElementTree as etree

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# A simplified version of RFC2822 addr-spec parsing
ATEXT = r'[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~]'
ATOM = ''.join(['(?:', ATEXT, '+', ')'])
DOT_ATOM_TEXT = ''.join(['(?:', ATOM, '(?:', r'\.', ATOM, ')', '*', ')'])
DOT_ATOM = DOT_ATOM_TEXT
LOCAL_PART = DOT_ATOM
DOMAIN = DOT_ATOM
ADDR_SPEC = ''.join(['(', LOCAL_PART, ')', '@', '(', DOMAIN,  ')'])
ADDR_SPEC_RE = re.compile(ADDR_SPEC)

# Enable a caching HTTP client
MEMCACHE_CLIENT = Client()
HTTP_CLIENT = httplib2.Http(MEMCACHE_CLIENT)  

# Create a reusable HTML5 parser
ETREE_BUILDER = html5lib.treebuilders.getTreeBuilder("etree", etree)
HTML_PARSER = html5lib.HTMLParser(ETREE_BUILDER)

# Add a couple of guessable finger templates for sites that don't provide them
HARDCODED_FINGER_TEMPLATES = {
  'gmail.com': 'http://profiles.google.com/{local-part}',
  'friendfeed.com': 'http://friendfeed.com/{local-part}/services'
}

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

  def _parse_identifier(self, identifier):
    """Treats an identifier as a RFC2822 addr-spec and splits it.
    
    Args:
      identifier: An email-like identifier
    Returns:
      The tuple (addr_spec, local_part, domain) if it can be parsed.
    """
    realname, addr_spec = email.utils.parseaddr(identifier)
    match = ADDR_SPEC_RE.match(addr_spec)
    if not match:
      return (None, None, None)
    local_part = match.group(1)
    domain = match.group(2)
    return addr_spec, local_part, domain

  def _get_finger_templates(self, domain):
    """Find the link rel=finger for a given domain."""
    url = 'http://' + domain
    logging.debug('Finding finger templates at %s' % url)
    response, content = HTTP_CLIENT.request(url)
    if response.status != 200:
      return None
    document = HTML_PARSER.parse(content)
    if not document:
      return None
    links = document.findall('.//link')
    finger_templates = list()
    for link in links:
      href = link.get('href')
      rels = link.get('rel', '').split()
      type = link.get('type', 'text/html') 
      if href and 'finger' in rels:
        if type in ['text/html', 'text/xhtml']:
          finger_templates.append(href)
    if not finger_templates:
      try:
        finger_templates.append(HARDCODED_FINGER_TEMPLATES[domain])
      except KeyError:
        pass  # no templates were hardcoded
    return finger_templates

  def _get_me_links(self, url):
    """Get the rel="me" links for a given URL.

    Args:
      url: The page that might contain rel="me" links
    Returns:
      A list of {href: ..., title: ...} dicts representing the rel="me" links
    """
    logging.debug('Finding me links at %s' % url)
    response, content = HTTP_CLIENT.request(url)
    if response.status != 200:
      return list()
    document = HTML_PARSER.parse(content)
    if not document:
      return list()
    me_links = list()
    anchors = document.findall('.//a')
    for a in anchors:
      href = a.get('href')
      rels = a.get('rel', '').split()
      title = a.text
      if href and 'me' in rels:
        me_links.append({'href': href, 'title': title})
    links = document.findall('.//link')
    for link in links:
      href = link.get('href')
      rels = link.get('rel', '').split()
      title = link.get('title')
      if href and 'me' in rels:
        me_links.append({'href': href, 'title': title})
    return me_links

  def _get_services(self, finger_templates, addr_spec, local_part):
    """Use the finger templates to fetch associated services.
    
    Args:
      finger_templates: A list of rel="finger" templates
      addr_spec: An addr-spec string (e.g., "dewitt@unto.net")
      local_part: A local-part string (e.g., "dewitt")
    Returns:
      A set of {href: ..., title: ...} dicts representing associated services
    """
    services = list()
    seen = set()
    for finger_template in finger_templates:
      url = finger_template.replace('{addr-spec}', addr_spec)
      url = url.replace('{local-part}', local_part)
      for me_link in self._get_me_links(url):
        if not me_link['href'] in seen:
          services.append(me_link)
          seen.add(me_link['href'])
    return services

  def get(self):
    identifier = self.request.get('identifier')

    addr_spec, local_part, domain = self._parse_identifier(identifier)
    if not addr_spec:
      return self._error('Couldn\'t find addr_spec in %s' % identifier)
    if not domain:
      return self._error('Couldn\'t find domain in %s' % identifier)
    if not local_part:
      return self._error('Couldn\'t find local-part in %s' % identifier)

    try:
      finger_templates = self._get_finger_templates(domain)
    except Exception:
      return self._error('Couldn\'t load from domain %s' % domain)
    if not finger_templates:
      return self._error('Couldn\'t find finger template for %s' % domain)

    services = self._get_services(finger_templates, addr_spec, local_part)
    
    template_values = dict()
    template_values['identifier'] = identifier
    template_values['addr_spec'] = addr_spec
    template_values['local_part'] = local_part
    template_values['domain'] = domain
    template_values['finger_templates'] = finger_templates
    template_values['services'] = services

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
