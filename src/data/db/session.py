from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bytequant.db')
#engine = create_engine(f'sqlite:///{DB_PATH}')
#engine = create_engine("postgresql+psycopg2://postgres.xahhzasispcbcvequfot:ByteQuantDBPW@aws-1-eu-west-1.pooler.supabase.com:5432/postgres", pool_pre_ping=True)
engine = create_engine("postgresql+psycopg2://postgres.dyqwphivjbxibumybonu:ByteQuantDBPW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres", pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
