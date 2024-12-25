from src.database.db_adapter import DatabaseAdapter
from src.database.models import User as UserModel
import yaml


class User:
    def __init__(self, telegram_id):
        self.adapter = DatabaseAdapter()
        self.id = telegram_id
        user_info = self.adapter.get_user_info(telegram_id)
        if user_info:
            self.name = user_info.full_name
            self.is_admin = user_info.is_admin
            self.registered_exam_id = user_info.registered_exam_id
        else:
            self.name = None
            self.is_admin = False
            self.registered_exam_id = None

    def __str__(self):
        return f"User: {self.id}, {self.name}, {self.is_admin}, {self.registered_exam_id}"

    def exists(self):
        return self.adapter.user_exists(self.id)

    def add(self, full_name):
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        default_admins = config['default_admins']

        is_admin = self.id in default_admins
        self.adapter.add_user(self.id, full_name, is_admin)
        self.name = full_name
        self.is_admin = is_admin

    def save(self):
        if self.exists():
            self.adapter.db.query(UserModel).filter(UserModel.telegram_id == self.id).update(
                {
                    "full_name": self.name,
                    "is_admin": self.is_admin,
                    "registered_exam_id": self.registered_exam_id
                })
        else:
            pass
        self.adapter.db.commit()

    def get_all_exams(self):
        return self.adapter.get_all_exams()

    def set_registered_exam(self, exam_id):
        self.adapter.set_user_exam(self.id, exam_id)
        self.registered_exam_id = exam_id

    def get_registered_exam(self):
        return self.registered_exam_id
