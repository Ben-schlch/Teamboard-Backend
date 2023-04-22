from unittest import IsolatedAsyncioTestCase
from services.boardedit import teamboardload, teamboardcreate, subtaskmove
import json


class Test(IsolatedAsyncioTestCase):
    async def test_teamboardload(self):
        res = await teamboardload('inf21034@lehre.dhbw-stuttgart.de')
        print(res)

    async def test_teamboardcreate(self):
        res = await teamboardcreate(json.loads('{"kind_of_object": "board", "type_of_edit": "add", "teamboard": {"id": 24, "name": "oof", "tasks": []}}'), "inf21034@lehre.dhbw-stuttgart.de")
        print(res)

    async def test_move_subtask(self):
        with open('./testdata/subtask-between-states.json') as f:
            res = await subtaskmove(json.load(f))
            print(res)

