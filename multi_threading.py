# -*- coding: utf-8 -*-

import threading
import time

# 主线程等待子线程运行完成后才退出/ 未实现


def target(second):
    print(f"Threading {threading.current_thread().name} is running")
    print(f"Threading {threading.current_thread().name} sleep {second}s")

    time.sleep(second)
    print(f"Threading {threading.current_thread().name} is ended.")


print(f"Threading {threading.current_thread().name} is running.")

for i in [1, 5]:
    t = threading.Thread(target=target, args=[i])
    t.start()
print(f"Threading {threading.current_thread().name} is ended.")

