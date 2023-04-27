from unittest import IsolatedAsyncioTestCase
from services.users import login_user, register_user


class Test(IsolatedAsyncioTestCase):
    async def test_register_user(self):
        res = await register_user("test", "ben+schlauch@gmail.com", "test")
    async def test_login_user(self):
        res = login_user("ben.schlauch+++@gmail.com", "test")
