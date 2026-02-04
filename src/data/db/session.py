from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bytequant.db')
engine = create_engine(f'sqlite:///{DB_PATH}')

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
