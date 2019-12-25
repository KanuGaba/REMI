#############
#   TIMER   #
#############



# Library imports.
import threading
import time

# Internal imports
import utils



class Timer():
    def __init__(self, id, duration, callback):
        self.id = id
        self.duration = duration
        self.callback = callback
        self.timer = None
        self.starttime = None
    
    def start(self):
        utils.debug_log("Timer {} has started!".format(self.id))
        self.timer = threading.Timer(float(self.duration), self.notify_done)
        self.starttime = time.time()
        self.timer.start()
    
    def notify_done(self):
        utils.debug_log("Timer {} is done!".format(self.id))
        self.callback(self.id)

    def cancel(self):
        self.timer.cancel()

    def remaining(self):
        return max(self.duration - (time.time() - self.starttime), 0.0)

if __name__ == "__main__":
    test_timer = Timer(0, 3, lambda id: print ("Timer {} is done!".format(id)))
    test_timer.start()
    # test_timer.cancel()   # Should cause program to terminate immediately.
    