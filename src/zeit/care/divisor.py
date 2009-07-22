# -*- coding: utf-8 -*-
import os
import sys
import StringIO
from lxml import etree
import zeit.care.crawl
import zeit.connector.connector
from zeit.connector.resource import Resource
import zope.authentication.interfaces

_DAV_PROP_NAME_ = ('file-name', 'http://namespaces.zeit.de/CMS/document')
_PARAMS_PER_PAGE_ = 5

class Converter(object):

    def __init__(self, xml_str):
        self.xml = xml_str
        self.body_elems = ['title','subtitle','byline','supertitle']

    def _build_new_body(self, elements, divisons):
        '''builds a new body node with the standard elements and the dvisions'''
        body_elements = []
        for d in elements:
            body_elements.append(d)

        body_divisions = []
        for d in divisons:
            new_div = etree.Element("division", type="page")
            new_div.extend(d)
            body_divisions.append(new_div)

        new_body = etree.Element("body")
        new_body.extend(body_elements)
        new_body.extend(body_divisions)

        return new_body

    def _get_params_per_page(self, tree):
        p = tree.xpath("//head/attribute[@ns='http://namespaces.zeit.de/CMS/document' \
	and @name='paragraphsperpage']")
        if p: 
            paras_per_page = int(p[0].text)
        else: 
            paras_per_page = _PARAMS_PER_PAGE_
        return paras_per_page
                

    def convert(self):
        tree = etree.parse(StringIO.StringIO(self.xml))

        # only articles
        if not tree.xpath('//article'):
            return self.xml
        elif tree.xpath('//body/division'):
            return self.xml
	
        paras_per_page = self._get_params_per_page(tree)                    
        div_list = []
        xp = 0
        div = []
        body_children = []
        body = tree.xpath('//body')[0]
        for e in list(body):
            # some elements are not part of the continuous text (title, byline, etc)
            if e.tag in self.body_elems:
                body_children.append(e)
                continue

            div.append(e)
            if e.tag in ['p','video']: xp += 1     

            if paras_per_page == xp:
                div_list.append(div)
                div = []
                xp = 0

        # append remaining elements
        if div:
            div_list.append(div)

        # replace body
        new_body = self._build_new_body(body_children, div_list)
        tree.xpath('//article')[0].replace(body, new_body)
        return etree.tostring(tree, encoding="UTF-8", xml_declaration=True)


def division_worker(resource, connector):
    if resource.type == "article":
        new_xml = Converter(resource.data.read()).convert()
        new_resource = Resource(resource.id, 
            resource.__name__, 
            resource.type, 
            StringIO.StringIO(new_xml), 
            resource.properties, 
            resource.contentType)
        connector[resource.id] = new_resource


def dev_main():
    import zeit.connector.mock

    connector = zeit.connector.mock.Connector()
    coll_path = 'http://xml.zeit.de/testdocs/'
    col = Resource(coll_path,
                    'testdocs',
                    'collection',
                    StringIO.StringIO(''))
    connector.add(col)  

    testdir = os.path.dirname(__file__)+'/testdocs/'
    testdocs = [(f,testdir+f) for f in os.listdir(testdir) if \
	os.path.isfile(testdir+f)]

    for (filename, filepath) in testdocs[0:13]:
        res = Resource('http://xml.zeit.de/testdocs/'+filename,
                filename,
                'article',
                open(filepath),
                contentType = 'text/xml')
        connector.add(res)
        division_worker(connector[res.id], connector)
        print connector[res.id].data.read()

def main():

    if len(sys.argv) < 3:
        sys.exit('parameters missing')

    webdav_uri = sys.argv[1]
    start_container = sys.argv[2]
    connector = zeit.connector.connector.Connector(roots=dict(
        default=webdav_uri))

    crawler = zeit.care.crawl.Crawler(connector, division_worker)
    crawler.run(start_container)