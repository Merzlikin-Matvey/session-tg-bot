import unittest
import sys

sys.path.append('./')
from src.database import db_adapter


class AdapterTests(unittest.TestCase):
    def test_exists(self):
        try:
            adapter = db_adapter.DatabaseAdapter()
            user_info = adapter.get_user_info(1648778328)
            self.assertIsNotNone(user_info)
        except Exception as e:
            self.fail("Не создается :(")

    def test_get_user_info(self):
        try:
            adapter = db_adapter.DatabaseAdapter()
            user_info = adapter.get_user_info(1648778328)
            self.assertIsNotNone(user_info)
        except Exception as e:
            self.fail("Не получается :(")

    def test_get_all_exams(self):
        try:
            adapter = db_adapter.DatabaseAdapter()
            exams = adapter.get_all_exams()
            self.assertIsNotNone(exams)
        except Exception as e:
            self.fail("Не получается :(")

    def test_add_user(self):
        try:
            adapter = db_adapter.DatabaseAdapter()
            adapter.add_user(123456, "Test User")
            self.assertEqual(0, 0)
        except Exception as e:
            self.fail("Не добавляется :(")

    def test_add_exam(self):
        try:
            adapter = db_adapter.DatabaseAdapter()
            adapter.add_exam("Test Exam", "2052-06-6 12:12")
            self.assertEqual(0, 0)
        except Exception as e:
            self.fail("Не добавляется :(")


if __name__ == "__main__":
    unittest.main()
