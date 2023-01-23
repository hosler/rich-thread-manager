from logging.handlers import BufferingHandler



class PopBufferingHandler(BufferingHandler):
    def flush(self):
        self.acquire()
        try:
            while len(self.buffer) >= self.capacity:
                self.buffer.pop(0)
        except IndexError:
            pass
        finally:
            self.release()