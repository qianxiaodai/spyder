# -*- coding: utf-8 -*-
"""
换个环境/多次运行结果不同
并发或并行执行
加锁处理
"""
import threading
import time

count = 0


class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global count
        lock.acquire()  # 加锁
        temp = count + 1
        time.sleep(0.001)
        count = temp
        lock.release()  # 释放锁


lock = threading.lock()
threads = []

for _ in range(1000):
    thread = MyThread()
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
print(f'Final count: {count}')



