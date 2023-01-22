import time, logging, queue, threading
from queue import Empty

from rtm.threading import RTMThread
from rtm.manager import Manager
# Set up the main/root logger
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)

class DumbThread(RTMThread):
    def run(self):
        while True:
            try:
                sub = self.queue.get(timeout=5)
            except Empty:
                break
            time.sleep(5)
            self.logger.info(f'THREAD {self.id}: {sub}')
            self.queue.task_done()
            if self.stop:
                self.logger.info(f'THREAD {self.id}: SIGNING OFF')
                break


queue = queue.Queue()

for counter in range(400):
    queue.put(counter)

manager = Manager(main_logger, queue, DumbThread)
manager.run()
