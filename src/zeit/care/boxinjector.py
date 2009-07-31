# -*- coding: utf-8 -*-
import os
import StringIO
from optparse import OptionParser
from lxml import etree
from datetime import datetime
import zeit.care.crawl
import zeit.connector.connector
from zeit.connector.resource import Resource
import zope.authentication.interfaces

_NS_DOC = 'http://namespaces.zeit.de/CMS/document'
_PROP_RELEASED = ('date_first_released', _NS_DOC)
_PROP_GALLERY = ('artbox_gallery', _NS_DOC)
_PROP_PORTRAIT = ('artbox_portrait', _NS_DOC)
_PROP_INFO = ('artbox_info', _NS_DOC)
_PROP_POS = ('artbox_position', _NS_DOC)

class BoxInjector(object):

    def __init__(self, resource):
        self.resource = resource
        self.xml = resource.data.read()
        self.new_xml = ''
        self.tree = None
        self.art_boxes = {}

    def _get_doc_date(self):
        '''
        gets date first released
        '''        
        first_released = self.resource.properties.get(_PROP_RELEASED)
        if first_released:
            return datetime.strptime(first_released[0:19], '%Y-%m-%dT%H:%M:%S')
        return None

    def _get_artbox_info(self):
        '''
        gets infos about a possible infobox
        '''
        xml_id = self.resource.properties.get(_PROP_INFO)
        if xml_id and xml_id.startswith('http://xml.zeit.de'):
            first_released = self._get_doc_date()
            artbox_position = self.resource.properties.get(_PROP_POS)
            if first_released:
                if first_released > datetime(2009,4,21):
                    position = 5
                elif artbox_position > 0:
                    position = artbox_position
                else:
                    position = 3
            attrib = {'expires':'', 'href':xml_id, 'publication-date':''}
            self.art_boxes[_PROP_INFO] =    {
                'element': etree.Element("infobox", attrib=attrib),
                'position':position}

    def _get_artbox_gallery(self):
        '''
        gets infos about a possible gallery box
        '''
        xml_id = self.resource.properties.get(_PROP_GALLERY)
        if xml_id and xml_id.startswith('http://xml.zeit.de'):
            first_released = self._get_doc_date()
            if first_released:
                if first_released > datetime(2009,4,21):
                    position = 5
                elif first_released > datetime(2008,9,30):
                    position = 7
                else:
                    position = 3
            attrib = {'expires':'', 'href':xml_id, 'publication-date':''}
            self.art_boxes[_PROP_GALLERY] = {
                'element': etree.Element("gallery", attrib=attrib),
                'position': position}
    
    def _get_portait_box(self):
        '''
        gets infos about a possible portrait box
        '''
        portrait_file = self.resource.properties.get(_PROP_PORTRAIT)
        if portrait_file and portrait_file.startswith('http://xml.zeit.de'):
            first_released = self._get_doc_date()
            if first_released and first_released > datetime(2009,04,21):
                position = 7
            else:
                position = 5
            attrib= {'expires':'','href':portrait_file,'publication-date':'','layout':'short'}
            self.art_boxes[_PROP_PORTRAIT] = {
                'element': etree.Element("portraitbox",  attrib=attrib),
                'position': position}

    def _insert_box(self, box):
        '''
        inserts the box at the right position
        '''
        position = box.get('position')
        in_division = None
        for i in range(1,4):
            sum_paras = self.tree.xpath('count(//article/body/division[position()=%d]/p)' % i)
            if position < sum_paras:
                in_division = i
                break
            else:
                position = int(position - sum_paras)
        self.tree.xpath('//article/body/division')[in_division-1].insert(position,box.get('element'))

    def _remove_xml_attr(self, prop):
        '''
        removes obsolete head/attributes from the xml
        '''
        xpath_qry = '//article/head/attribute[@ns="%s" and @name="%s"]' % (prop[1], prop[0])
        prop_attr = self.tree.xpath(xpath_qry)
        self.tree.xpath('//article/head')[0].remove(prop_attr[0])

    def convert(self): 
        '''
        injects article boxes found in properties in the article
        '''
        self.tree = etree.parse(StringIO.StringIO(self.xml))
            
        # only articles
        if not self.tree.xpath('//article'):
            return self.xml

        self._get_portait_box()
        self._get_artbox_gallery()
        self._get_artbox_info()

        if self.art_boxes:
            # change the doc
            for prop in self.art_boxes:    
                self._insert_box(self.art_boxes[prop])
                self._remove_xml_attr(prop)
                del self.resource.properties[prop]
            self.new_xml = etree.tostring(self.tree, encoding="UTF-8", xml_declaration=True)

    def get_new_resource(self):
        '''
        returns a new resource with inline article boxes
        '''
        if self.new_xml:
            new_resource = Resource(self.resource.id, 
                self.resource.__name__, self.resource.type, 
                StringIO.StringIO(self.new_xml), self.resource.properties, 
                self.resource.contentType)
            return new_resource
        return None
        

def crawler_worker(resource, connector):
    if resource.type == "article":
        injector = BoxInjector(resource)
        injector.convert()
        new_resource = injector.get_new_resource()
        if new_resource:
            print resource.id            
            connector[resource.id] = new_resource

def dev():
    import zeit.connector.mock

    connector = zeit.connector.mock.Connector()
    coll_path = 'http://xml.zeit.de/testdocs/with_divisions/'
    col = Resource(coll_path,
                    'testdocs',
                    'collection',
                    StringIO.StringIO(''))
    connector.add(col)  

    testdir = os.path.dirname(__file__)+'/testdocs/with_divisions/'
    testdocs = [(f,testdir+f) for f in os.listdir(testdir) if \
    os.path.isfile(testdir+f)]

    for (filename, filepath) in testdocs[0:13]:
        res = Resource('http://xml.zeit.de/testdocs/with_divisions/'+filename,
                filename,
                'article',
                open(filepath),
                contentType = 'text/xml')
        connector.add(res)
        crawler_worker(connector[res.id], connector)
        #print connector[res.id].data.read()

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-m", "--mode", dest="mode",
                      help="dev for dev mode, live for live connector",
                      choices=['dev','live'])
    parser.add_option("-c", "--collection", dest="collection",
                      help="entry collection for starting the conversion")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                        help="no reinsurance question, for batch mode e.g.")
    #parser.add_option("-v", "--verbose",
                      #action="store_true", dest="verbose")
    #parser.add_option("-q", "--quiet",
                      #action="store_false", dest="verbose")

    (options, args) = parser.parse_args()

    if not options.mode:
        parser.error("missing mode")

    if options.mode == 'dev':
        dev()
    elif options.mode == 'live':
        if not options.collection:
            parser.error("missing entry point for conversion")

        if not options.webdav:
            parser.error("missing webdav uri")
           
        if not options.force:
            user_ok = raw_input('\nConversion will start at %s.\nAre you sure? [y|n]: ' \
                % options.collection)
        else: 
            user_ok = "y" 

        if user_ok == "y":
            connector = zeit.connector.connector.Connector(roots=dict(
                default=options.webdav))
            crawler = zeit.care.crawl.Crawler(connector, crawler_worker)
            crawler.run(options.collection)
    

