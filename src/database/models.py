from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, BigInteger, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(String, primary_key=True)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)


class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    timestamp = Column(DateTime)
    tasks_paths = Column(Text)
    participants = Column(ARRAY(String), default=[])
    started = Column(Boolean, default=False)


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=50,
    max_overflow=50,
    pool_timeout=50,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
