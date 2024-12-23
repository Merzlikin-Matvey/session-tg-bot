from src.database.db_adapter import DatabaseAdapter
from sqlalchemy import Column, Integer, String, DateTime, Text, ARRAY, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    timestamp = Column(DateTime)
    tasks_paths = Column(Text)
    participants = Column(ARRAY(String), default=[])
    started = Column(Boolean, default=False)

    def __init__(self, name, timestamp, tasks_paths="", participants=[], started=False):
        self.adapter = DatabaseAdapter()
        self.name = name
        self.timestamp = timestamp
        self.tasks_paths = tasks_paths
        self.participants = participants
        self.started = started
        self.save()

    @staticmethod
    def get_exam_by_id(exam_id):
        adapter = DatabaseAdapter()
        exam_data = adapter.db.query(Exam).filter(Exam.id == exam_id).first()
        if exam_data:
            return Exam(
                name=exam_data.name,
                timestamp=exam_data.timestamp,
                tasks_paths=exam_data.tasks_paths,
                participants=exam_data.participants,
                started=exam_data.started
            )
        return None

    @staticmethod
    def get_all_exams():
        adapter = DatabaseAdapter()
        return adapter.db.query(Exam).all()

    def exists(self):
        return self.adapter.db.query(Exam).filter(Exam.name == self.name).first() is not None

    def save(self):
        if self.exists():
            self.adapter.db.query(Exam).filter(Exam.name == self.name).update(
                {
                    "timestamp": self.timestamp,
                    "tasks_paths": self.tasks_paths,
                    "participants": self.participants,
                    "started": self.started
                })
        else:
            self.adapter.db.add(self)
        self.adapter.db.commit()


    def add_task(self, path):
        if self.tasks_paths:
            self.tasks_paths += f";{path}"
        else:
            self.tasks_paths = path
        self.save()

    def add_participant(self, telegram_id):
        if telegram_id not in self.participants:
            self.participants.append(telegram_id)
            self.save()