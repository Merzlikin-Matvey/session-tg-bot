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
    examiners = Column(ARRAY(String), default=[])
    started = Column(Boolean, default=False)

    def __init__(self, name, timestamp, tasks_paths="", participants=[], examiners=[], started=False, adapter=None):
        self.adapter = adapter or DatabaseAdapter()
        self.name = name
        self.timestamp = timestamp
        self.tasks_paths = tasks_paths
        self.participants = participants
        self.examiners = examiners
        self.started = started
        print('create')

    @staticmethod
    def get_exam_by_id(exam_id):
        adapter = DatabaseAdapter()
        exam_data = adapter.db.query(Exam).filter(Exam.id == exam_id).first()
        if exam_data:
            exam = Exam(
                name=exam_data.name,
                timestamp=exam_data.timestamp,
                tasks_paths=exam_data.tasks_paths,
                participants=exam_data.participants,
                examiners=exam_data.examiners,
                started=exam_data.started,
                adapter=adapter
            )
            return exam
        return None

    @staticmethod
    def get_all_exams():
        adapter = DatabaseAdapter()
        return adapter.db.query(Exam).all()

    def exists(self):
        try:
            self.adapter.db.query(Exam).filter(Exam.name == self.name).first() is not None
        except AttributeError:
            self.adapter = DatabaseAdapter()
        return self.adapter.db.query(Exam).filter(Exam.name == self.name).first() is not None


    def save(self):
        if self.exists():
            self.adapter.db.query(Exam).filter(Exam.name == self.name).update(
                {
                    "timestamp": self.timestamp,
                    "tasks_paths": self.tasks_paths,
                    "participants": self.participants,
                    "examiners": self.examiners,
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

    def remove_participant(self, telegram_id):
        if telegram_id in self.participants:
            self.participants.remove(telegram_id)
            self.save()

    def add_examiner(self, telegram_id):
        if telegram_id not in self.examiners:
            self.examiners.append(telegram_id)
            self.save()

    def is_examiner(self, telegram_id):
        return telegram_id in self.examiners

    def is_student_assigned(self, student_id):
        return self.adapter.db.query(Exam).filter(Exam.participants.any(student_id), Exam.examiners.any()).first() is not None

    def assign_student_to_examiner(self, student_id, examiner_id):
        self.adapter.db.query(Exam).filter(Exam.participants.any(student_id)).update({"examiners": [examiner_id]})
        self.adapter.db.commit()
