from unittest import TestCase
from services.passwords import check_pw, hash_and_salt
import time


class Test(TestCase):
    def test_check_pw(self):
        pw = hash_and_salt("test")
        start = time.time()
        checked = check_pw("test", pw)
        elapsed = time.time() - start
        print(elapsed)
        self.assertTrue(checked)

