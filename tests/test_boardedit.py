from unittest import IsolatedAsyncioTestCase
from services.boardedit import teamboardload


class Test(IsolatedAsyncioTestCase):
    async def test_teamboardload(self):
        res = await teamboardload("inf21034@lehre.dhbw-stuttgart.de")
        print(res)

