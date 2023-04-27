from unittest import IsolatedAsyncioTestCase
from services.users import login_user, register_user


class Test(IsolatedAsyncioTestCase):
    async def test_register_user(self):
        res = await register_user("test", "teamboard.projekt@gmail.com", "Hallo1234")


    async def test_login_user(self):
        res = await login_user("teamboard.projekt@gmail.com", "Hallo1234")
        print(res)
