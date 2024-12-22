from db_adapter import DatabaseAdapter

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

    def add(self, full_name, is_admin=False):
        self.adapter.add_user(self.id, full_name, is_admin)
