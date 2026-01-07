import threading
import time


def boy_setting(boy):
    boy.append(4)
    print('hello1')
    time.sleep(5)
    print(d.boy)


class Builder:
    def __init__(self):
        self.small_icon = None

    def setSmallIcon(self):
        self.small_icon = 'picture'


class Xain:
    def __init__(self):
        self.boy = [1, 2, 3]

    def set_boy(self):
        threading.Thread(
            target=boy_setting,
            args=[self.boy]
        ).start()
        print('hello')


d = Xain()
d.set_boy()
print(d.boy)

