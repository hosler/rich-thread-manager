from threading import Thread

class RTMThread(Thread):
    def __init__(self, id, logger, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.logger = logger
        self.stop = False

    def run(self):
        while True:
            if self.stop:
                self.logger.info(f'THREAD {self.id}: SIGNING OFF')
                break

    def kill(self):
        self.stop = True