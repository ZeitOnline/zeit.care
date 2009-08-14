# -*- coding: utf-8 -*-
import os
import logging 
import StringIO
from optparse import OptionParser
from lxml import etree
import zeit.care.crawl
from zeit.care import add_file_logging
import zeit.connector.connector
from zeit.connector.resource import Resource
import zope.authentication.interfaces

logger = logging.getLogger(__name__) 

_DAV_PROP_NAME_ = ('file-name', 'http://namespaces.zeit.de/CMS/document')
_PARAMS_PER_PAGE_ = 7

class Converter(object):

    def __init__(self, xml_str):
        self.xml = xml_str
        self.body_elems = ['title','subtitle','byline','supertitle','bu']
        self.div_elems = ['p','video','audio','raw','intertitle','article_extra']

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
            if e.tag in self.div_elems: xp += 1     

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
        try:
            new_xml = Converter(resource.data.read()).convert()
            new_resource = Resource(resource.id, 
                resource.__name__, 
                resource.type, 
                StringIO.StringIO(new_xml), 
                resource.properties, 
                resource.contentType)
            connector[resource.id] = new_resource
            logger.info(resource.id)
        except:
            logger.exception(resource.id)

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-c", "--collection", dest="collection",
                      help="entry collection for starting the conversion")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")
    parser.add_option("-l", "--log", dest="logfile",
                      help="logfile for errors")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                        help="no reinsurance question, for batch mode e.g.")

    (options, args) = parser.parse_args()

    if not options.collection:
        parser.error("missing entry point for conversion")

    if not options.webdav:
        parser.error("missing webdav uri")

    if options.logfile:
        add_file_logging(logger, options.logfile)

    if not options.force:
        user_ok = raw_input('\nConversion will start at %s.\nAre you sure? [y|n]: ' \
            % options.collection)
    else: 
        user_ok = "y" 

    if user_ok == "y":
        connector = zeit.connector.connector.Connector(roots=dict(
            default=options.webdav))
        crawler = zeit.care.crawl.Crawler(connector, division_worker)
        crawler.run(options.collection)