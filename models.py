from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
Base = declarative_base()
engine = create_engine('sqlite:///pyazo.db', echo=False)

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, nullable=False)
    star = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
