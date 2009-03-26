At first, we need a connector for our beloved crawler.

>>> import zeit.connector.mock
>>> connector = zeit.connector.mock.Connector()
>>> connector
<zeit.connector.mock.Connector object at 0x...>


Then we define a simple worker which will be passed to the
instanciated crawler.

>>> def worker(resource, connector):
...     print resource.id

>>> import zeit.care.crawl
>>> crawler = zeit.care.crawl.Crawler(
...     connector, worker)
>>> crawler
<zeit.care.crawl.Crawler object at 0x...>


Start to crawl.

>>> crawler.run('http://xml.zeit.de/online/')
http://xml.zeit.de/online/
http://xml.zeit.de/online/2005
http://xml.zeit.de/online/2006
http://xml.zeit.de/online/2007
http://xml.zeit.de/online/2007/01
http://xml.zeit.de/online/2007/02
http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang
http://xml.zeit.de/online/2007/01/Arbeitsmarktzahlen
http://xml.zeit.de/online/2007/01/EU-Beitritt-rumaenien-bulgarien
http://xml.zeit.de/online/2007/01/Flugsicherheit
http://xml.zeit.de/online/2007/01/Ford-Beerdigung
http://xml.zeit.de/online/2007/01/Gesundheitsreform-Die
http://xml.zeit.de/online/2007/01/Guantanamo
...


Now we define a worker that sets a property on each resource.


>>> def worker(resource, connector):
...     connector.changeProperties(resource.id, {
... 		('bar', 'foo'): 'batz'})

>>> crawler = zeit.care.crawl.Crawler(
...     connector, worker)
>>> crawler
<zeit.care.crawl.Crawler object at 0x...>

>>> crawler.run('http://xml.zeit.de/online/')
>>> resource = connector[
... 	'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang']

>>> import pprint
>>> pprint.pprint(dict(resource.properties)[('bar', 'foo')])
'batz'
