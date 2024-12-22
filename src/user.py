from src.database.db_adapter import DatabaseAdapter
import yaml

class User:
    def __init__(self, telegram_id):
        self.adapter = DatabaseAdapter()
        self.id = telegram_id
        user_info = self.adapter.get_user_info(telegram_id)
        if user_info:
            self.name = user_info.full_name
            self.is_admin = user_info.is_admin
        else:
            self.name = None
            self.is_admin = False

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
        user_info = self.adapter.get_user_info(self.id)
        if user_info:
            user_info.full_name = self.name
            user_info.is_admin = self.is_admin

    def get_all_exams(self):
        return self.adapter.get_all_exams()