import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url = os.getenv('SQLALCHEMY_DATABASE_URI')
engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()
