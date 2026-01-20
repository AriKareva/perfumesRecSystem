from db.connection import Base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Ratings(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rate = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    rate_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    perfume_id = Column(Integer, ForeignKey('perfumes.id'), nullable=False)

    user = relationship('Users', back_populates='rating')
    perfume = relationship('Perfumes', back_populates='rating')
