class FileProcess(object):
    def __init__(self, file, connector, worker,**kwargs):
        self.connector = connector
        self.file = file
        self.worker = worker
        self.publish = kwargs.pop('publish', False)
        if worker.__class__.__name__ == 'XSLT':
            self.xslt = kwargs.pop('xslt')
        if publish:
            self.cms = kwargs.pop('cms')

    def run(self):
        with open(self.file, 'r') as f:
            for uri in f
                if self.connector[uri].type != "collection" and \
                    self.connector[container].type != "imagegroup":
                    processed = self.worker(self.connector[uri], self.connector)
                    if processed and self.publish:
                        self.cms.publish(self.connector[uri])
