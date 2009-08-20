#!/usr/bin/python2.5
#
# Provides a WebFinger protocol lookup service.
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

import imports

import email.utils
import httplib2
import re
import sys
import urllib
import xrd

# A simplified version of RFC2822 addr-spec parsing
ATEXT = r'[\w\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~]'
ATOM = ''.join(['(?:', ATEXT, '+', ')'])
DOT_ATOM_TEXT = ''.join(['(?:', ATOM, '(?:', r'\.', ATOM, ')', '*', ')'])
DOT_ATOM = DOT_ATOM_TEXT
LOCAL_PART = DOT_ATOM
DOMAIN = DOT_ATOM
ADDR_SPEC = ''.join(['(', LOCAL_PART, ')', '@', '(', DOMAIN,  ')'])
ADDR_SPEC_RE = re.compile(ADDR_SPEC)

# The URL template for domain-level XRD documents
DOMAIN_LEVEL_XRD_TEMPLATE = 'http://%s/.well-known/host-meta'

# The rel value used to indicate a user lookup service
WEBFINGER_SERVICE_REL_VALUE = 'http://webfinger.info/rel/service'

class ParseError(Exception):
  """Raised in the event an id can not be parsed."""
  pass

class FetchError(Exception):
  """Raised in the event a URL can not be fetched."""
  pass

class UsageError(Exception):
  """Raised on command-line usage errors."""
  pass

class WebfingerError(Exception):
  """Raised if services found are not valid WebFinger documents."""
  pass


class Client(object):

  def __init__(self, http_client=None, xrd_parser=None):
    """Construct a new WebFinger client.

    Args:
      http_client: A httplib2-like instance [optional]
      xrd_parser: An XRD parser [optional]
    """
    if http_client:
      self._http_client = http_client
    else:
      self._http_client = httplib2.Http()
    if xrd_parser:
      self._xrd_parser = xrd_parser
    else:
      self._xrd_parser = xrd.Parser()

  def lookup(self, id, normalize=True):
    """Look up a webfinger resource by (email-like) id.

    Args:
      id: An (email-like) id
      normalize:
    Returns:
      Either a heterogeneous list of xrd_pb2.Xrd and/or xfn_pb2.Xfn
      instances (depending on the service response type), or
      a homogeneous list of html5_pb2.Link instances if normalize
      is True.
    Raises:
      FetchError if a URL can not be retrieved.
      WebfingerError if a resource can not be parsed as a WebFinger XRD.
    """
    addr_spec, local_part, domain = self._parse_id(id)
    domain_url = DOMAIN_LEVEL_XRD_TEMPLATE % domain
    response, content = self._http_client.request(domain_url)
    if response.status != 200:
      raise FetchError(
        'Could not fetch %s. Status %d.' % (domain_url, response.status))
    domain_xrd = self._xrd_parser.parse(content)
    webfinger_link = self._get_webfinger_service_link(domain_xrd)
    if not webfinger_link:
      raise WebfingerError(
        'Could not find webfinger service in %s' % domain_url)
    service_template = self._get_service_template(webfinger_link)
    if not service_template:
      raise WebfingerError(
        'Could not find webfinger service template in %s' % domain_url)
    service_url = self._interpolate_webfinger_template(service_template, id)
    response, content = self._http_client.request(service_url)
    if response.status != 200:
      raise FetchError(
        'Could not fetch %s. Status %d.' % (service_url, response.status))
    service_xrd = self._xrd_parser.parse(content)
    return service_xrd

  def _interpolate_webfinger_template(self, template, id):
    """Replaces occurances of {id} and {%id} within a webfinger template.

    Args:
      template: A webfinger URI template
      id: A identity string
    Returns:
      The template with {id} and {%id} replaced.
    """
    return template.replace('{id}', id).replace('{%id}', urllib.quote(id))

  def _get_service_template(self, webfinger_link):
    """Finds the best matching URI or URITemplate for a given webfinger service.

    Args:
      webfinger_link: An xrd_pb2.Link instance
    Returns:
      A string that can be treated as a webfinger service URI template, or None.
    """
    # TODO(dewitt): Sort by priority
    if len(webfinger_link.uri_templates) > 0:
      return webfinger_link.uri_templates[0].value
    if len(webfinger_link.uris) > 0:
      return webfinger_link.uris[0].value
    return None

  def _get_webfinger_service_link(self, description):
    """Finds a link matching the webfinger service rel value.

    Args:
      A xrd_pb2.Xrd protobuf
    Returns:
      A xrd_pb2.Link protobuf if found, otherwise None
    """
    # TODO(dewitt): Sort by priority
    for link in description.links:
      for relation in link.relations:
        if relation.value == WEBFINGER_SERVICE_REL_VALUE:
          return link
    return None

  def _parse_id(self, id):
    """Treats an identifier as a RFC2822 addr-spec and splits it.

    Args:
      id: An email-like identifier
    Returns:
      The tuple (addr_spec, local_part, domain) if it can be parsed.
    Raises:
      ParseError if the id can not be parsed.
    """
    realname, addr_spec = email.utils.parseaddr(id)
    if not addr_spec:
      raise ParseError('Could not parse %s for addr-spec' % id)
    match = ADDR_SPEC_RE.match(addr_spec)
    if not match:
      raise ParseError('Could not parse %s for local_part, domain' % id)
    return addr_spec, match.group(1), match.group(2)

  def _xrd_as_html5_links(self, xrd_description):
    """Converts a xrd_pb2.Xrd instance into a list of html5_pb2.Links.

    This denormalizes the Link element in the Xrd into a set of
    HTML5 link elements.

    Args:
      xrd_description: An xrd_pb2.Xrd instance
    Returns:
      A list of html5_pb2.Link instances
    """
    


def main(argv):
  if len(argv) < 2:
    raise UsageError('Usage webfinger.py id')
  client = Client()
  print client.lookup(argv[1])


if __name__ == "__main__":
  main(sys.argv)
