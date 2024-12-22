from src.database.db_adapter import DatabaseAdapter
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    timestamp = Column(DateTime)

    def __init__(self, name, timestamp):
        self.adapter = DatabaseAdapter()
        self.name = name
        self.timestamp = timestamp
        self.add_exam_to_db()

    def add_exam_to_db(self):
        self.adapter.db.add(self)
        self.adapter.db.commit()

    def save(self):
        exam_info = self.adapter.db.query(Exam).filter(Exam.name == self.name).first()
        if exam_info:
            exam_info.name = self.name
            exam_info.timestamp = self.timestamp
            self.adapter.db.commit()