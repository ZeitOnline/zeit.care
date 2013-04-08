# -*- coding: utf-8 -*-
from optparse import OptionParser
import logging
import os
import sys
import zeit.care.crawl
import zeit.connector.connector
from zeit.connector.resource import Resource

logger = logging.getLogger(__name__)

def commentthread_worker(resource, connector):
    properties = resource.properties
    comments = properties.get(
        ('comments', 'http://namespaces.zeit.de/CMS/document'))

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


