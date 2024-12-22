from models import User, SessionLocal

class DatabaseAdapter:
    def __init__(self):
        self.db = SessionLocal()

    def user_exists(self, telegram_id):
        return self.db.query(User).filter(User.telegram_id == telegram_id).first() is not None

    def add_user(self, telegram_id, full_name, is_admin=False):
        db_user = User(telegram_id=telegram_id, full_name=full_name, is_admin=is_admin)
        self.db.add(db_user)
        self.db.commit()

    def get_user_info(self, telegram_id):
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def close(self):
        self.db.close()