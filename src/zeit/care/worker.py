import datetime
import pytz
import sys
import zeit.care.crawl
import zeit.connector.connector

def isofy_main():
    connector = zeit.connector.connector.Connector(roots=dict(
        default=sys.argv[1]))
    start_container = sys.argv[2]
    crawler = zeit.care.crawl.Crawler(connector, isofy_worker)
    crawler.run(start_container)


def isofy_worker(resource, connector):
    dlm = resource.properties.get((
         'date-last-modified',
         'http://namespaces.zeit.de/CMS/document'))
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
