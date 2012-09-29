import os
import unittest
import xmlrpclib
import StringIO
#from djangopypi.views import parse_distutils_request, simple
import django.test
from djangopypi.models import Package, Classifier, Release, PackageInfoField, Distribution
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpRequest

def create_post_data(action):
    data = {
            ":action": action,
            "metadata_version": "1.0",
            "name": "foo",
            "version": "0.1.0-pre2",
            "summary": "The quick brown fox jumps over the lazy dog.",
            "home_page": "http://example.com",
            "author": "Foo Bar Baz",
            "author_email": "foobarbaz@example.com",
            "license": "Apache",
            "keywords": "foo bar baz",
            "platform": "UNKNOWN",
            "classifiers": [
                "Development Status :: 3 - Alpha",
                "Environment :: Web Environment",
                "Framework :: Django",
                "Operating System :: OS Independent",
                "Intended Audience :: Developers",
                "Intended Audience :: System Administrators",
                "License :: OSI Approved :: BSD License",
                "Topic :: System :: Software Distribution",
                "Programming Language :: Python",
            ],
            "download_url": "",
            "provides": "",
            "requires": "",
            "obsoletes": "",
            "description": """
=========
FOOBARBAZ
=========

Introduction
------------
    ``foo`` :class:`bar`
    *baz*
    [foaoa]
            """,
    }
    return data

def create_request(data):
    boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
    sep_boundary = '\n--' + boundary
    end_boundary = sep_boundary + '--'
    body = StringIO.StringIO()
    for key, value in data.items():
        # handle multiple entries for the same name
        if type(value) not in (type([]), type( () )):
            value = [value]
        for value in value:
            value = unicode(value).encode("utf-8")
            body.write(sep_boundary)
            body.write('\nContent-Disposition: form-data; name="%s"'%key)
            body.write("\n\n")
            body.write(value)
            if value and value[-1] == '\r':
                body.write('\n')  # write an extra newline (lurve Macs)
    body.write(end_boundary)
    body.write("\n")

    return body.getvalue()


# class MockRequest(object):
# 
#     def __init__(self, raw_post_data):
#         self.raw_post_data = raw_post_data
#         self.META = {}
# 
# 
# class TestParseWeirdPostData(unittest.TestCase):
# 
#     def test_weird_post_data(self):
#         data = create_post_data("submit")
#         raw_post_data = create_request(data)
#         post, files = parse_distutils_request(MockRequest(raw_post_data))
#         self.assertTrue(post)
# 
#         for key in post.keys():
#             if isinstance(data[key], list):
#                 self.assertEquals(data[key], post.getlist(key))
#             elif data[key] == "UNKNOWN":
#                 self.assertTrue(post[key] is None)
#             else:
#                 self.assertEquals(post[key], data[key])

client = Client()

class TestSearch(unittest.TestCase):
    
    def setUp(self):
        self.dummy_user = User.objects.create(username='krill', password='12345',
                                 email='krill@opera.com')
        self.pkg = Package.objects.create(name='foo')
        self.pkg.owners.add(self.dummy_user)
    
    def tearDown(self):
        self.pkg.delete()
        self.dummy_user.delete()
    
    def test_search_for_package(self):
        response = client.post(reverse('djangopypi-search'), {'search_term': 'foo'})
        self.assertTrue("""<a href="/pypi/pypi/foo/">foo</a>""" in response.content)
        
class TestSimpleView(unittest.TestCase):
    
    def create_distutils_httprequest(self, user_data={}):
        self.post_data = create_post_data(action='user')        
        self.post_data.update(user_data)
        self.raw_post_data = create_request(self.post_data)
        request = HttpRequest()
        request.POST = self.post_data
        request.method = "POST"
        request.raw_post_data = self.raw_post_data
        return request      
        
    # def test_user_registration(self):        
    #     request = self.create_distutils_httprequest({'name': 'peter_parker', 'email':'parker@dailybugle.com',
    #                                                 'password':'spiderman'})
    #     response = simple(request)
    #     self.assertEquals(200, response.status_code)
    #     
    # def test_user_registration_with_wrong_data(self):
    #     request = self.create_distutils_httprequest({'name': 'peter_parker', 'email':'parker@dailybugle.com',
    #                                                  'password':'',})
    #     response = simple(request)
    #     self.assertEquals(400, response.status_code)


from djangotestclientxmlrpctransport import DjangoTestClientXMLRPCTransport


class TestXmlRpc(django.test.TestCase):
    """
    Test that the server responds to xmlrpc requests
    """
    def setUp(self):
        from django.core.files.base import ContentFile
        
        self.dummy_file = ContentFile("gibberish")
        self.dummy_user = User.objects.create(username='bobby', password='tables',
                                 email='bobby@tables.com')
        self.pkg = Package.objects.create(name='foo')
        self.pkg.owners.add(self.dummy_user)
        self.release = Release.objects.create(package=self.pkg, version="1.0")
    
    def tearDown(self):
        self.release.delete()
        self.pkg.delete()
        self.dummy_user.delete()
    
    def test_list_package(self):
        pypi = xmlrpclib.ServerProxy("http://localhost/pypi/", transport=DjangoTestClientXMLRPCTransport(self.client))
        pypi_hits = pypi.list_packages()
        expected = ['foo']
        self.assertEqual(pypi_hits, expected)
    
    def test_package_releases(self):
        pypi = xmlrpclib.ServerProxy("http://localhost/pypi/", transport=DjangoTestClientXMLRPCTransport(self.client))
        pypi_hits = pypi.package_releases('foo')
        expected = ['1.0']
        self.assertEqual(pypi_hits, expected)
    
        
