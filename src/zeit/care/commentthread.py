# -*- coding: utf-8 -*-
from lxml import etree
from optparse import OptionParser
from zeit.care import add_file_logging
import logging
import urllib
import zeit.care.crawl
import zeit.connector.connector

logger = logging.getLogger(__name__)

def commentthread_worker(resource, connector):
    if resource.type != 'article' and resource.type != 'gallery':
        return
    properties = resource.properties
    cprop = properties.get(
        ('comments', 'http://namespaces.zeit.de/CMS/document'))
    if cprop and cprop == 'no':
        logger.info(resource.id)
        return
    agatho_url = resource.id.replace(
        'http://xml.zeit.de/', 'http://www.zeit.de/agatho/thread/')
    try:
        fh = urllib.urlopen(agatho_url)
    except UnicodeError:
        return
    if fh.getcode() == 404:
        logger.info(resource.id)
        return
    tree = etree.XML(fh.read())
    ccount = tree.xpath('/comments/comment_count')[0]
    if ccount.text == '0':
        logger.info(resource.id)
        return


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-c", "--collection", dest="collection",
                      help="entry collection for starting the conversion")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")
    parser.add_option("-l", "--log", dest="logfile",
                      help="logfile for errors")

    (options, args) = parser.parse_args()

    if not options.collection:
        parser.error("missing entry point")

    if not options.webdav:
        parser.error("missing webdav uri")

    if options.logfile:
        add_file_logging(logger, options.logfile)

    connector = zeit.connector.connector.Connector(roots=dict(
        default=options.webdav))
    crawler = zeit.care.crawl.Crawler(connector, commentthread_worker)
    crawler.run(options.collection)


