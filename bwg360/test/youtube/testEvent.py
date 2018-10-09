import time
import multiprocessing

def event_func(event):
    print('\t{0} is waiting'.format(multiprocessing.current_process()))
    if event.is_set():
        print('\t{0} has woken up'.format(multiprocessing.current_process()))

pool = multiprocessing.Pool(processes=5)

def test_event():
    
    manager = multiprocessing.Manager()
    event = manager.Event()
    rsts = [pool.apply_async(event_func, args=(event,)) for i in range(5)]
    # processes = [multiprocessing.Process(target=event_func, args=(event,))
    #              for i in range(5)]

    # for p in processes:
    #     p.start()

    print('main is waiting')
    [r.get() for r in rsts]

    # print('main is setting event')
    # event.set()

    # for p in processes:
    #     p.join()

if __name__ == '__main__':
    test_event()