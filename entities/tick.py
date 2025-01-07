import time

class Tick():
    def __init__(self, fps):
        self.start = time.time()
        self.end = self.start + (1/fps)

    def wait_for_tick(self):
        if self.end < time.time():
            return False
        time.sleep(self.end - time.time())
        return True

