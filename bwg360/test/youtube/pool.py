import multiprocessing
from queue import Queue


class WrapperProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self._args = None
        self._kwargs = None
        self._worker = None

    def setTarget(self, worker=None, args=(), kwargs={}):
        self._args = args
        self._kwargs = kwargs
        self._worker = worker

    def run(self):
        try:
            if self._worker:
                return self._worker(*self._args, **self._kwargs)
        except Exception as e:
            raise
        

class ProcessPool(object):
    def __init__(self, ps_size=0):
        cpu_cnt = multiprocessing.cpu_count()
        sz = ps_size if ps_size > cpu_cnt else cpu_cnt
        self.queue = Queue(maxsize=sz)
        for i in range(sz):
            self.put(WrapperProcess())

    def empty(self):
        return self.queue.empty()

    def put(self, ps, block=True, timeout=None):
        print('Put Process into queue again')
        self.queue.put(item=ps, block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        print('Get Process from queue')
        try:
            # If `False`, the program is not blocked. 
            # `Queue.Empty` is thrown if the queue is empty
            s = self.queue.get(False)
        except Queue.Empty:
            s = WrapperProcess()

        return s


if __name__ == '__main__':
    processPool = ProcessPool(2)
