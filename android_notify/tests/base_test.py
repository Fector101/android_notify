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
