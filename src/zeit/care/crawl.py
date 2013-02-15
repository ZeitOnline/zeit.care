class Crawler(object):

    def __init__(self, connector, worker):
        self.connector = connector
        self.worker = worker

    def run(self, start_container):
        stack = [start_container]
        while stack:
            container = stack.pop(0)
            self.worker(self.connector[container], self.connector)
            if self.connector[container].type == "collection" or \
                self.connector[container].type == "imagegroup": 
                    stack.extend(r[1] for r in self.connector.listCollection(container))

class FileProcess(object):
    def __publish__ (self):
        pass

    def __init__(self, file, connector, worker,**kwargs):
        self.connector = connector
        self.file = file
        self.worker = worker
        self.publish = kwargs.pop('publish',self.__publish__)
        self.params = kwargs

    def run(self):
        with open(self.file, 'r') as f:
            for uri in f:
                uri = uri.rstrip("\n")
                if self.connector[uri].type != "collection" and \
                    self.connector[uri].type != "imagegroup": 
                    processed = self.worker(self.connector[uri],
                                            self.connector,
                                            *self.params)
                    if processed:
                        self.publish(uri)
