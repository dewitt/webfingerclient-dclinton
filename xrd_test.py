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

import unittest

import xrd

class ParserTest(unittest.TestCase):

  def testParseEmptyString(self):
    parser = xrd.Parser()
    try:
      parser.parse('')
      self.fail('ParseError expected.')
    except xrd.ParseError:
      pass  # expected

  def testParse(self):
    parser = xrd.Parser()
    description = parser.parse(
        '<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"/>')

  def testParseWithExpires(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
           </XRD>''')
    self.assertEquals('1970-01-01T00:00:00Z', description.expires.value)

  def testParseWithSubject(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>acct://bradfitz@gmail.com</Subject>
           </XRD>''')
    self.assertEquals('acct://bradfitz@gmail.com', description.subject.value)

  def testParseWithSubject(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>acct://bradfitz@gmail.com</Subject>
           </XRD>''')
    self.assertEquals('acct://bradfitz@gmail.com', description.subject.value)

  def testParseWithAliases(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>acct://bradfitz@gmail.com</Subject>
             <Alias>http://www.google.com/profiles/bradfitz</Alias>
             <Alias>http://www.google.com/profiles/brad.fitz</Alias>
           </XRD>''')
    self.assertEquals(2, len(description.aliases))
    self.assertEquals('http://www.google.com/profiles/bradfitz',
                      description.aliases[0].value)
    self.assertEquals('http://www.google.com/profiles/brad.fitz',
                      description.aliases[1].value)

  def testParseWithTypes(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>acct://bradfitz@gmail.com</Subject>
             <Alias>http://www.google.com/profiles/bradfitz</Alias>
             <Alias>http://www.google.com/profiles/brad.fitz</Alias>
             <Type required="true">http://blgx.example.net/ns/version/1.2</Type>
             <Type required="0">http://blgx.example.net/ns/version/1.1</Type>
             <Type>http://blgx.example.net/ns/ext/language</Type>
           </XRD>''')
    self.assertEquals(3, len(description.types))
    self.assertEquals('http://blgx.example.net/ns/version/1.2',
                      description.types[0].value)
    self.assertEquals(True, description.types[0].required)
    self.assertEquals('http://blgx.example.net/ns/version/1.1',
                      description.types[1].value)
    self.assertEquals(False, description.types[1].required)
    self.assertEquals('http://blgx.example.net/ns/ext/language',
                      description.types[2].value)
    self.assertEquals(False, description.types[2].required)


  def testParseWithLinks(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>acct://bradfitz@gmail.com</Subject>
             <Alias>http://www.google.com/profiles/bradfitz</Alias>
             <Alias>http://www.google.com/profiles/brad.fitz</Alias>
             <Type required="true">http://blgx.example.net/ns/version/1.2</Type>
             <Type required="0">http://blgx.example.net/ns/version/1.1</Type>
             <Type>http://blgx.example.net/ns/ext/language</Type>
             <Link>
               <Rel>http://portablecontacts.net/spec/1.0</Rel>
               <URI>http://www-opensocial.googleusercontent.com/api/people/</URI>
             </Link>
             <Link>
               <Rel>http://webfinger.info/rel/profile-page</Rel>
               <Rel>describedby</Rel>
               <MediaType>text/html</MediaType>
               <MediaType>text/xhtml</MediaType>
               <URI>http://www.google.com/profiles/bradfitz</URI>
             </Link>
             <Link priority="10">
               <Rel>describedby</Rel>
               <MediaType>text/x-foo</MediaType>
               <URI priority="0">
                 http://s2.googleusercontent.com/webfinger/?q=bradfitz%40gmail.com&amp;fmt=foo
               </URI>
               <URI priority="10">
                 http://s2.googleusercontent.com/webfinger/?q=bradfitz%40gmail.com&amp;fmt=foo
               </URI>
             </Link>
             <Link>
               <Rel>describedby</Rel>
               <MediaType>application/rdf+xml</MediaType>
               <URITemplate>
                 http://s2.googleusercontent.com/webfinger/?q=bradfitz%40gmail.com&amp;fmt=foaf
               </URITemplate>
             </Link>
           </XRD>''')
    self.assertEquals(4, len(description.links))
    self.assertEquals(1, len(description.links[0].relations))
    self.assertEquals(1, len(description.links[0].uris))
    self.assertEquals(2, len(description.links[1].relations))
    self.assertEquals(1, len(description.links[1].uris))
    self.assertEquals(2, len(description.links[1].media_types))
    self.assertEquals(10, description.links[2].priority)
    self.assertEquals(1, len(description.links[2].relations))
    self.assertEquals(2, len(description.links[2].uris))
    self.assertEquals(1, len(description.links[2].media_types))
    self.assertEquals(0, description.links[2].uris[0].priority)
    self.assertEquals(10, description.links[2].uris[1].priority)
    self.assertEquals(1, len(description.links[3].relations))
    self.assertEquals(1, len(description.links[3].uri_templates))
    self.assertEquals(1, len(description.links[3].media_types))


def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(ParserTest))
  return suite

if __name__ == '__main__':
  unittest.main()
