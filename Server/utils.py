from threading import Event, Thread
from time import time, sleep

def call_repeatedly(interval, func, *args):
    stopped = Event()
    def loop():
        start = time()
        while not stopped.wait(interval - (time()-start)): # the first call is in `interval` secs
            start = time()
            func(*args)
    thread = Thread(target=loop)
    thread.daemon = True
    thread.start()
    return stopped.set
