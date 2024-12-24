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
            self.fail("Не создается :(")

    def test_exists(self):
        user = User(1648778328)
        self.assertTrue(user.exists())

    def test_get_all_exams(self):
        user = User(5064226866)
        exams = user.get_all_exams()
        self.assertIsNotNone(exams)


if __name__ == "__main__":
    unittest.main()
