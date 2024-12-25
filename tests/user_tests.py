import unittest
import sys
import time
sys.path.append('./')
from src.objects.user import User


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

    def test_get_all_exams(self):
        try:
            user = User(5064226866)
            exams = user.get_all_exams()
            self.assertIsNotNone(exams)
        except Exception as e:
            self.fail(f"Ошибка: {e}")


if __name__ == "__main__":
    unittest.main()
