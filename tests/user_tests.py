import unittest
import sys
import time
sys.path.append('./')
from src.objects.user import User
from src.database.db_adapter import DatabaseAdapter


class UserTests(unittest.TestCase):
    def test_creating(self):
        try:
            user = User(int(time.time()))
            self.assertIsNotNone(user)
        except Exception as e:
            self.fail(f"Ошибка: {e}")

    def test_exists(self):
        try:
            user = User(int(time.time()))
            user.save()
            self.assertTrue(user.exists())
        except Exception as e:
            self.fail(f"Ошибка: {e}")


if __name__ == "__main__":
    unittest.main()
