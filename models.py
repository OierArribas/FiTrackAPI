from sqlalchemy import Column, Boolean, ForeignKey,Integer, String, LargeBinary
from sqlalchemy.dialects.postgresql import BYTEA

from database import Base

class User(Base):
    __tablename__ = 'usuarios3'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String)
    hashed_password = Column(String)
    foto = Column(String(length=500000))




