from multiprocessing import Process, Lock
import os

def info(title):
    print title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def f(name):
    info('function f')
    print 'hello', name

def g(l, i):
    l.acquire()
    print 'hello world', i
    l.release()

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()

    lock = Lock()

    for num in range(10):
        Process(target=g, args=(lock, num)).start()
