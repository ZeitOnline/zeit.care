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


Lets try the file crawler. It takes a list of webdav-resources.
As above these resources can be manipulated by a worker.
There is also an option to define a publisher and pass it as keyword-argument.

>>> def worker(resource, connector):
...     print resource.id
>>> import os
>>> path = os.path.dirname(__file__)+'/resources.list'
>>> crawler = zeit.care.crawl.FileProcess(
...     path, connector, worker)
>>> crawler
<zeit.care.crawl.FileProcess object at ...>

Lets try if the worker is working. Its supposed to just output any url it is
getting
>>> crawler.run()
http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang
http://xml.zeit.de/online/2007/01/Arbeitsmarktzahlen
http://xml.zeit.de/online/2007/01/EU-Beitritt-rumaenien-bulgarien
http://xml.zeit.de/online/2007/01/Flugsicherheit
http://xml.zeit.de/online/2007/01/Ford-Beerdigung
http://xml.zeit.de/online/2007/01/Gesundheitsreform-Die
http://xml.zeit.de/online/2007/01/Guantanamo

We define a publisher, which will be executed, if the worker did its job
>>> def worker(resource, connector):
...     return True
>>> def publisher(url):
...   print "publish "+url
>>> crawler = zeit.care.crawl.FileProcess(
...     path, connector, worker,publish=publisher)
>>> crawler.run()
publish http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang
publish http://xml.zeit.de/online/2007/01/Arbeitsmarktzahlen
publish http://xml.zeit.de/online/2007/01/EU-Beitritt-rumaenien-bulgarien
publish http://xml.zeit.de/online/2007/01/Flugsicherheit
publish http://xml.zeit.de/online/2007/01/Ford-Beerdigung
publish http://xml.zeit.de/online/2007/01/Gesundheitsreform-Die
publish http://xml.zeit.de/online/2007/01/Guantanamo

We want a XSLT based worker. It takes a file-location.
>>> import zeit.care.worker
>>> zeit.care.worker.xslt_worker
<function xslt_worker at ...>
>>> arg = {'xslt':os.path.dirname(__file__)+'/test.xslt'}
>>> resource = connector['http://xml.zeit.de/online/2007/01/Flugsicherheit'] 

Lets see if transformation is working
>>> str(zeit.care.worker._xslt_transform(arg['xslt'],resource))
'<?xml version="1.0"?>\n<foo>ba</foo>\n'

>>> resource = connector['http://xml.zeit.de/online/2007/01/Flugsicherheit'] 
>>> processed = zeit.care.worker.xslt_worker(resource,connector,**arg)
>>> resource = connector['http://xml.zeit.de/online/2007/01/Flugsicherheit'] 
>>> resource.data.read()
'<?xml version="1.0"?>\n<foo>ba</foo>\n'


The ResourceProcess is the same as file crawler, but it takes just one webdav-resource.
As above these resources can be manipulated by a worker.
There is also an option to define a publisher and pass it as keyword-argument.

>>> import zeit.care.publish
>>> def worker(resource, connector):
...     return True
>>> publish = zeit.care.publish.publish_xmlrpc
>>> crawler = zeit.care.crawl.ResourceProcess(
...     'http://xml.zeit.de/feuilleton/osbournes', connector, worker,publish=publish)
>>> crawler.run()
cannot publish http://xml.zeit.de/feuilleton/osbournes




