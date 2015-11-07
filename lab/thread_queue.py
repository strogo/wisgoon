from Queue import Queue
from threading import Thread
import urllib2

base_url = "http://wisgoon.com/api/v6/post/item/%d/"


def do_stuff(q):
    while True:
        print q.get()
        try:
            r = urllib2.urlopen(base_url % q.get())
            print r.code
            print base_url % q.get()
        except Exception, e:
            print str(e)
        q.task_done()

q = Queue(maxsize=0)
num_threads = 300

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()

for x in range(10000000):
    q.put(x)

q.join()
