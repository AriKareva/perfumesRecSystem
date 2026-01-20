from sqlalchemy import Column, Integer, String, DateTime
from db.connection import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_enc = Column(String(255), nullable=False)
    reg_date = Column(DateTime, nullable=False, default=func.now())

    rating = relationship('Ratings', back_populates='user')