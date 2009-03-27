class Crawler(object):

    def __init__(self, connector, worker):
        self.connector = connector
        self.worker = worker

    def run(self, start_container):
        stack = [start_container]
        while stack:
            container = stack.pop(0)
            self.worker(self.connector[container], self.connector)
            stack.extend(r[1] for r in self.connector.listCollection(container))
