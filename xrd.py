#!/usr/bin/python2.5
#
# Parses XRD documents.
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
import xrd_pb2

# As specified in:
#   http://www.oasis-open.org/committees/download.php/33772/xrd-1.0-wd04.html
XRD_NAMESPACE = 'http://docs.oasis-open.org/ns/xri/xrd-1.0'

# The etree syntax for qualified element names
XRD_QNAME              = '{%s}%s' % (XRD_NAMESPACE, 'XRD')
EXPIRES_QNAME          = '{%s}%s' % (XRD_NAMESPACE, 'Expires')
SUBJECT_QNAME          = '{%s}%s' % (XRD_NAMESPACE, 'Subject')
ALIAS_QNAME            = '{%s}%s' % (XRD_NAMESPACE, 'Alias')
TYPE_QNAME             = '{%s}%s' % (XRD_NAMESPACE, 'Type')
LINK_QNAME             = '{%s}%s' % (XRD_NAMESPACE, 'Link')
REL_QNAME              = '{%s}%s' % (XRD_NAMESPACE, 'Rel')
MEDIA_TYPE_QNAME       = '{%s}%s' % (XRD_NAMESPACE, 'MediaType')
URI_QNAME              = '{%s}%s' % (XRD_NAMESPACE, 'URI')
URI_TEMPLATE_QNAME     = '{%s}%s' % (XRD_NAMESPACE, 'URITemplate')


class ParseError(Exception):
  """Raised in the event an XRD document can not be parsed."""
  pass


class Parser(object):
  """Converts XML documents into xrd_pb2.Xrd instances."""

  def __init__(self, etree=None):
    """Constructs a new XRD parser.

    Args:
      etree: The etree module to use [optional]
    """
    if etree:
      self._etree = etree
    else:
      import xml.etree.cElementTree
      self._etree = xml.etree.cElementTree

  def parse(self, string):
    """Converts XML strings into an xrd_pb2.Xrd instances

    Args:
      string: A string containing an XML XRD document.
    Returns:
      A xrd_pb2.Xrd instance.
    Raises:
      ParseError if the element can not be parsed
    """
    if not string:
      raise ParseError('Empty input string.')
    try:
      document = self._etree.fromstring(string)
    except SyntaxError:
      raise ParseError('Could not parse %s' % string)
    if document.tag != XRD_QNAME:
      raise ParseError('Root is not an <XRD/> element: %s' % document)
    description = xrd_pb2.Xrd()
    self._parse_expires(document, description)
    self._parse_subject(document, description)
    self._parse_aliases(document, description)
    self._parse_types(document, description)
    self._parse_links(document, description)
    return description

  def _parse_expires(self, xrd_element, description):
    """Finds an Expires element and adds it to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    expires_element = xrd_element.find(EXPIRES_QNAME)
    if expires_element is not None:
      description.expires.value = expires_element.text

  def _parse_subject(self, xrd_element, description):
    """Finds an Subject element and adds it to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    subject_element = xrd_element.find(SUBJECT_QNAME)
    if subject_element is not None:
      description.subject.value = subject_element.text

  def _parse_aliases(self, xrd_element, description):
    """Finds Alias elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance added to
    """
    for alias_element in xrd_element.findall(ALIAS_QNAME):
      description.aliases.add().value = alias_element.text

  def _parse_types(self, xrd_element, description):
    """Finds Type elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    for type_element in xrd_element.findall(TYPE_QNAME):
      type_pb = description.types.add()
      type_pb.value = type_element.text
      type_pb.required = type_element.get('required') in ['true', '1']

  def _parse_links(self, xrd_element, description):
    """Finds Link elements and adds them to the Xrd proto.

    Args:
      xrd_element: An XRD Element
      description: The xrd_pb2.Xrd instance to be added to
    """
    for link_element in xrd_element.findall(LINK_QNAME):
      link = description.links.add()
      if link_element.get('priority') is not None:
        link.priority = long(link_element.get('priority'))
      self._parse_subject(link_element, link)
      self._parse_relations(link_element, link)
      self._parse_media_types(link_element, link)
      self._parse_uris(link_element, link)
      self._parse_uri_templates(link_element, link)

  def _parse_relations(self, link_element, link):
    """Finds Rel elements and adds them to the Link proto.

    Args:
      link_element: A Link Element
      link: The xrd_pb2.Link instance to be added to
    """
    for relation_element in link_element.findall(REL_QNAME):
      link.relations.add().value = relation_element.text

  def _parse_media_types(self, link_element, link):
    """Finds MediaType elements and adds them to the Link proto.

    Args:
      link_element: A Link Element
      link: The xrd_pb2.Link instance to be added to
    """
    for media_type_element in link_element.findall(MEDIA_TYPE_QNAME):
      link.media_types.add().value = media_type_element.text

  def _parse_uris(self, link_element, link):
    """Finds URI elements and adds them to the Link proto.

    Args:
      link_element: A Link Element
      link: The xrd_pb2.Link instance to be added to
    """
    for uri_element in link_element.findall(URI_QNAME):
      uri = link.uris.add()
      if uri_element.get('priority') is not None:
        uri.priority = long(uri_element.get('priority'))
      uri.value = uri_element.text

  def _parse_uri_templates(self, link_element, link):
    """Finds MediaType elements and adds them to the Link proto.

    Args:
      link_element: A Link Element
      link: The xrd_pb2.Link instance to be added to
    """
    for uri_template_element in link_element.findall(URI_TEMPLATE_QNAME):
      uri_template = link.uri_templates.add()
      if uri_template_element.get('priority') is not None:
        uri_template.priority = long(uri_template_element.get('priority'))
      uri_template.value = uri_template_element.text
