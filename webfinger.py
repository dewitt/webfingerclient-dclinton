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

import httplib2

class Client(object):

  def __init__(self, http_client=None):
    """Construct a new WebFinger client.

    Args:
      http_client: A httplib2-like instance [optional]
    """
    if http_client:
      self._http_client = http_client
    else:
      self._http_client = httplib2.Http()

  def lookup(self, id):
    """Look up a webfinger resource by (email-like) id.

    Args:
      id: An (email-like) id
    Returns:
      A xrd_pb2.Xrd instance.
    """
    pass
