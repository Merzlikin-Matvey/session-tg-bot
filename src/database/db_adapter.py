from datetime import datetime

from src.database.models import User, Exam, SessionLocal


class DatabaseAdapter:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def user_exists(self, telegram_id):
        return self.db.query(User).filter(User.telegram_id == str(telegram_id)).first() is not None

    def add_user(self, telegram_id, full_name, is_admin=False):
        db_user = User(telegram_id=str(telegram_id), full_name=full_name, is_admin=is_admin)
        self.db.add(db_user)
        self.db.commit()

    def get_user_info(self, telegram_id):
        return self.db.query(User).filter(User.telegram_id == str(telegram_id)).first()

    def add_exam(self, name, timestamp):
        db_exam = Exam(name=name, timestamp=timestamp)
        self.db.add(db_exam)
        self.db.commit()

    def get_all_exams(self):
        return self.db.query(Exam).all()

    def get_available_exams(self):
        exams = self.get_all_exams()
        current_time = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
        upcoming_exams = [exam for exam in exams if datetime.strptime(str(exam.timestamp),
                                                                      "%Y-%m-%d %H:%M:%S").timestamp() >= current_time.timestamp()]
        return sorted(upcoming_exams, key=lambda exam: exam.timestamp)

    def set_user_exam(self, telegram_id, exam_id):
        self.db.query(User).filter(User.telegram_id == str(telegram_id)).update({"registered_exam_id": exam_id})
        self.db.commit()
