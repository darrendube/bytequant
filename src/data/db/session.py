from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///bytequant.db')

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
