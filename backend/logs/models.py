# from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
# from db.connection import Base
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship

# class Logs(Base):
#     __tablename__ = 'logs'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     log_data = Column(Text, nullable=False)
#     log_date = Column(DateTime, nullable=False, default=func.now())
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

#     user = relationship('Logs', back_populates='users')
    
