# -*- coding: utf-8 -*-

from multiprocessing import Process
import os
from time import ctime, sleep


# 子进程要执行的代码
def movie(name):
    print(f"I was watching {name}, {ctime()}")
    sleep(5)
    print('Run child process %s (%s)...' % (name, os.getpid()))


def listen(name):
    print(f"I was listening {name}, {ctime()}")
    sleep(2)
    print()


if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    p1 = Process(target=movie, args=('阿凡达',))  # 创建进程对象
    p2 = Process(target=listen, args=('我是一只小小鸟'))
    # p.start()  # 启动子进程
    # p.join()
    print('Child process end.')
