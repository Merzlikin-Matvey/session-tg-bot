import unittest
import sys
sys.path.append('./')
from src.objects.exam import Exam


class TestExams(unittest.TestCase):
    def test_creating(self):
        try:
            exam = Exam("Test Exam", "2052-06-6 12:12")
            self.assertIsNotNone(exam)
        except Exception as e:
            self.fail("Не создается :(")

    def test_get_exam_by_id(self):
        try:
            exam = Exam.get_exam_by_id(2)
            self.assertIsNotNone(exam)
        except Exception as e:
            self.fail("Не получается :(")

    def test_get_all_exams(self):
        try:
            exams = Exam.get_all_exams()
            self.assertIsNotNone(exams)
        except Exception as e:
            self.fail("Не получается :(")

    def test_exists(self):
        try:
            exam = Exam("Test Exam", "2052-06-6 12:12")
            self.assertTrue(exam.exists())
        except Exception as e:
            self.fail("Не существует :(")

    def test_add_participant(self):
        try:
            exam = Exam("Test Exam", "2052-06-6 12:12")
            exam.add_participant(123456789)
            self.assertEqual(0, 0)
        except Exception as e:
            self.fail("Не добавляется :(")

    def test_add_task(self):
        try:
            exam = Exam("Test Exam", "2052-06-6 12:12")
            exam.add_task("test_task.py")
            self.assertEqual(0, 0)
        except Exception as e:
            self.fail("Не добавляется :(")

    def test_save(self):
        try:
            exam = Exam("Test Exam", "2052-06-6 12:12")
            exam.save()
            self.assertEqual(0, 0)
        except Exception as e:
            self.fail("Не сохраняется :(")


if __name__ == "__main__":
    unittest.main()
