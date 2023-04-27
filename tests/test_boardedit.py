from unittest import IsolatedAsyncioTestCase
from services.boardedit import teamboardload, teamboardcreate, teamboardadduser
import json


class Test(IsolatedAsyncioTestCase):
    async def test_teamboardload(self):
        res = await teamboardload('inf21034@lehre.dhbw-stuttgart.de')
        print(res)

    async def test_teamboardcreate(self):
        res = await teamboardcreate(json.loads('{"kind_of_object": "board", "type_of_edit": "add", "teamboard": {"id": 24, "name": "oof", "tasks": []}}'), "inf21034@lehre.dhbw-stuttgart.de")
        print(res)

    async def test_teamboardadduser(self):
        res = await teamboardadduser(json.loads('{\"kind_of_object\":\"teamboard\",\"type_of_edit\":\"addUser\",\"teamboard_id\":1,\"email\":\"ben.schlauch@gmail.com\"}'), "inf21034@lehre.dhbw-stuttgart.de")

