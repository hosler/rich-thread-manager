import time, logging, queue, threading
from queue import Empty

from rtmui.threading import RTMThread
from rtmui.manager import Manager

# Set up the main/root logger
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# main_logger.addHandler(handler)


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

for counter in range(40):
    queue.put(counter)

manager = Manager(main_logger, queue, DumbThread)
manager.run()
