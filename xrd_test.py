#!/usr/bin/python2.5
#
# Tests the XRD parser.
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

  def testParseWithId(self):
    parser = xrd.Parser()
    description = parser.parse(
        '<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0" xml:id="foo"/>')
    self.assertEquals('foo', description.id)

  def testParseWithExpires(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Expires>1970-01-01T00:00:00Z</Expires>
           </XRD>''')
    self.assertEquals('1970-01-01T00:00:00Z', description.expires)

  def testParseWithSubject(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Subject>acct://bradfitz@gmail.com</Subject>
           </XRD>''')
    self.assertEquals('acct://bradfitz@gmail.com', description.subject)


  def testParseWithAliases(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
             <Alias>http://www.google.com/profiles/bradfitz</Alias>
             <Alias>http://www.google.com/profiles/brad.fitz</Alias>
           </XRD>''')
    self.assertEquals(2, len(description.aliases))
    self.assertEquals('http://www.google.com/profiles/bradfitz',
                      description.aliases[0])
    self.assertEquals('http://www.google.com/profiles/brad.fitz',
                      description.aliases[1])

  def testParseAll(self):
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xml:id="foo">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>http://example.com/gpburdell</Subject>
             <Property type="http://spec.example.net/type/person"
                 xsi:nil="true" />
             <Alias>http://people.example.com/gpburdell</Alias>
             <Alias>acct:gpburdell@example.com</Alias>
             <Link rel="http://spec.example.net/auth/1.0"
                 href="http://services.example.com/auth" />
             <Link rel="http://spec.example.net/photo/1.0" type="image/jpeg"
                 href="http://photos.example.com/gpburdell.jpg">
               <Title xml:lang="en">User Photo</Title>
             </Link>
           </XRD>''')
    self.assertEquals('foo', description.id)
    self.assertEquals('1970-01-01T00:00:00Z', description.expires)
    self.assertEquals('http://example.com/gpburdell', description.subject)
    self.assertEquals('http://spec.example.net/type/person',
                      description.properties[0].type)
    self.assertEquals(True, description.properties[0].nil)
    self.assertEquals(2, len(description.aliases))
    self.assertEquals('http://people.example.com/gpburdell',
                      description.aliases[0])
    self.assertEquals('acct:gpburdell@example.com',
                      description.aliases[1])
    self.assertEquals(2, len(description.links))
    self.assertEquals('http://spec.example.net/auth/1.0',
                      description.links[0].rel)
    self.assertEquals('http://services.example.com/auth',
                      description.links[0].href)
    self.assertEquals('http://spec.example.net/photo/1.0',
                      description.links[1].rel)
    self.assertEquals('image/jpeg',
                      description.links[1].type)
    self.assertEquals('http://photos.example.com/gpburdell.jpg',
                      description.links[1].href)
    self.assertEquals(1, len(description.links[1].titles))
    self.assertEquals('User Photo', description.links[1].titles[0].value)
    self.assertEquals('en', description.links[1].titles[0].lang)

class ParserTest(unittest.TestCase):

  def _init_json(self):
    try:
      import simplejson as json
    except ImportError:
      import json
    self._json = json

  def testJsonConversion(self):
    self._init_json()
    parser = xrd.Parser()
    description = parser.parse(
        '''<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xml:id="foo">
             <Expires>1970-01-01T00:00:00Z</Expires>
             <Subject>http://example.com/gpburdell</Subject>
             <Alias>http://people.example.com/gpburdell</Alias>
             <Alias>acct:gpburdell@example.com</Alias>
             <Property type="http://spec.example.net/version">1.0</Property>
             <Property type="http://spec.example.net/version">2.0</Property>
             <Property type="http://spec.example.net/type/person" xsi:nil="true" />
             <Link rel="http://spec.example.net/auth/1.0"
               href="http://services.example.com/auth" />
             <Link rel="http://spec.example.net/photo/1.0" type="image/jpeg"
               href="http://photos.example.com/gpburdell.jpg">
               <Title xml:lang="en">User Photo</Title>
               <Title xml:lang="de">Benutzerfoto</Title>
               <Property type="http://spec.example.net/created/1.0">1970-01-01</Property>
             </Link>
             <Link rel="http://fake.com/moo" template="http://fake.com/tpl/{$id}" />
           </XRD>''')
    expected_xrd_json = self._json.loads(
        '''{
             "links": [
               {
                 "href": "http:\u002f\u002fservices.example.com\u002fauth",
                 "rel": "http:\u002f\u002fspec.example.net\u002fauth\u002f1.0"
               },
               {
                 "titles": {
                   "de": "Benutzerfoto",
                   "en": "User Photo"
                 },
                 "href": "http:\u002f\u002fphotos.example.com\u002fgpburdell.jpg",
                 "type": "image\u002fjpeg",
                 "rel": "http:\u002f\u002fspec.example.net\u002fphoto\u002f1.0"
               },
               {
                 "template": "http:\u002f\u002ffake.com\u002ftpl\u002f{$id}",
                 "rel": "http:\u002f\u002ffake.com\u002fmoo"
               }
             ],
             "expires": "1970-01-01T00:00:00Z",
             "id": "foo",
             "subject": "http:\u002f\u002fexample.com\u002fgpburdell",
             "properties": [
               {
                 "type": "http:\u002f\u002fspec.example.net\u002fversion",
                 "value": "1.0"
               },
               {
                 "type": "http:\u002f\u002fspec.example.net\u002fversion",
                 "value": "2.0"
               },
               {
                 "type": "http:\u002f\u002fspec.example.net\u002ftype\u002fperson"
               }
             ],
             "aliases": [
               "http:\u002f\u002fpeople.example.com\u002fgpburdell",
               "acct:gpburdell@example.com"
             ]
           }''')
    marshaller = xrd.JsonMarshaller()
    xrd_json = self._json.loads(marshaller.to_json(description))
    self.assertEquals(expected_xrd_json, xrd_json)


def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(ParserTest))
  suite.addTests(unittest.makeSuite(JsonTest))
  return suite

if __name__ == '__main__':
  unittest.main()
