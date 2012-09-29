"""
DjangoTestClientXMLRPCTransport

from http://www.alittletooquiet.net/blog/2009/11/01/testing-django-xml-rpc-interfaces/
"""

import httplib
import xmlrpclib


class DjangoTestClientXMLRPCTransport(object):
    """Designed to be passed into the `transport` argument of
    `xmlrpclib.ServerProxy`, this class accepts a `django.test.TestClient`
    object and uses it as the transport.

    """

    client = None

    def __init__(self, client):
        self.client = client

    def request(self, host, handler, request_body, verbose = False):
        parser, unmarshaller = xmlrpclib.getparser()

        response = self.client.post(handler, request_body, 'text/xml')

        if response.status_code != 200:
            raise xmlrpclib.ProtocolError(
              '%s%s' % (host, handler),
              response.status_code,
              httplib.responses.get(response.status_code, ''),
              dict(response.items()),
            )

        parser.feed(response.content)

        return unmarshaller.close()
