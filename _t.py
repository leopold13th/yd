import multiprocessing
import time

a = "baskjifsdf"

def worker():
    """worker function"""
    print a
    time.sleep(15)
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
