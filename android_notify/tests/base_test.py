import unittest
import time

secs2 = 2
secs3 = 3
secs5 = 5


class AndroidNotifyBaseTest(unittest.TestCase):

    def setUp(self):
        max_int = 2_147_483_647
        self.uid = int(time.time() * 1000) % max_int

    def tearDown(self):
        time.sleep(secs3)

from android_notify.config import on_android_platform, from_service_file
if on_android_platform() and not from_service_file():
    from kivymd.toast import toast
else:
    def toast(text=None,length_long=0):
        print(f'Fallback toast - text: {text}, length_long: {length_long}')
