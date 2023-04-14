from unittest import TestCase
from services.boardedit import teamboardload
import asyncio


class Test(TestCase):
    def test_teamboardload(self):
        res = asyncio.run(teamboardload("inf21034@lehre.dhbw-stuttgart.de"), debug=True)
        print(res)
        self.fail()

