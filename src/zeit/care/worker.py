import datetime
import pytz
import sys
import zeit.care.crawl
import zeit.care.publish
import zeit.connector.connector
import lxml
import StringIO
from optparse import OptionParser
from zeit.connector.resource import Resource


def isofy_main():
    connector = zeit.connector.connector.Connector(roots=dict(
        default=sys.argv[1]))
    start_container = sys.argv[2]
    crawler = zeit.care.crawl.Crawler(connector, isofy_worker)
    crawler.run(start_container)


def isofy_worker(resource, connector):
    dlm = resource.properties.get((
        'date-last-modified', 'http://namespaces.zeit.de/CMS/document'))
    if dlm is not None:
        dt = isofy_date_last_modified(dlm)
        if dt is not None:
            print resource.id
            connector.changeProperties(resource.id, {(
                'date-last-modified',
                'http://namespaces.zeit.de/CMS/document'): dt})


def isofy_date_last_modified(date):
    try:
        dt = datetime.datetime.strptime(date, "%d.%m.%Y - %H:%M")
    except ValueError:
        return None
    dt = pytz.timezone("Europe/Berlin").localize(dt).astimezone(pytz.UTC)
    return dt.isoformat()


def xslt_main():
    connector = zeit.connector.connector.Connector(roots=dict(
        default=sys.argv[1]))
    file = sys.argv[2]
    xslt = sys.argv[3]
    publish = zeit.care.publish.publish_xmlrpc
    crawler = zeit.care.crawl.FileProcess(file, connector, xslt_worker,
                                          xslt=xslt, publish=publish)
    crawler.run()


def xslt_worker(resource, connector, **kwargs):
    xslt = kwargs.pop('xslt')
    xml = _xslt_transform(xslt, resource)

    new_resource = Resource(resource.id,
                            resource.__name__,
                            resource.type,
                            StringIO.StringIO(xml),
                            contentType=resource.contentType)
    connector[resource.id] = new_resource
    return True


def _xslt_transform(xslt, resource):
    transform = lxml.etree.XSLT(lxml.etree.parse(xslt))
    return transform(lxml.etree.XML(resource.data.read()))


def property_main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="file",
                      help="file, containing a list of resources")
    parser.add_option("-n", "--propname", dest="collection",
                      help="file, containing a list of resources")
    parser.add_option("-N", "--namespace", dest="collection",
                      help="file, containing a list of resources")
    parser.add_option("-v", "--propvalue", dest="collection",
                      help="file, containing a list of resources")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")

    (options, args) = parser.parse_args()

    if not options.file:
        parser.error("missing file to read resources from")

    if not options.propname:
        parser.error("missing propname")

    if not options.namespace:
        parser.error("missing property namespace")

    if not options.propvalue:
        parser.error("missing propvalue")

    if not options.webdav:
        parser.error("missing webdav uri")

    connector = zeit.connector.connector.Connector(roots=dict(
        default=options.webdav))
    publish = zeit.care.publish.publish_xmlrpc
    crawler = zeit.care.crawl.FileProcess(options.file,
                                          connector,
                                          property_worker,
                                          publish=publish,
                                          propname=options.propname,
                                          propvalue=options.propvalue,
                                          namespace=options.namespace)
    crawler.run()


def property_worker(uri, connector, **kwargs):
    properties = kwargs.pop('properties')
    connector.changeProperties(uri, properties)
    return True


def get_property(resource, property, namespace):
    value = resource.properties.get((property, namespace))
    return value
