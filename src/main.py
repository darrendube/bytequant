from sqlalchemy import create_engine
from sqlalchemy.org import sessionmaker
from data.models import Base # TODO: fix this import


# setup database using db models in data/models.py
# TODO: perhaps this code should sit in the data folder?

engine = create_engine('sqlite:///data/bytequant.db', echo=True)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

