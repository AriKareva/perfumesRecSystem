from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base

# Все модели данных, свзанные с парфюмами

class Perfumes(Base):
    __tablename__ = "perfumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    photo = Column(String(255), nullable=True) # фото пока храним локально, возможно позже заменим на облако
    description = Column(Text, nullable=True)
    brand_id  = Column(Integer, ForeignKey('brands.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    concentration_id = Column(Integer, ForeignKey('concentration.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    concentration = relationship('Concentration', back_populates='perfume')
    brand = relationship('Brands', back_populates='perfume')
    rating = relationship('Ratings', back_populates='perfume')
    perfume_note = relationship('PerfumeNotes', back_populates='perfume')


class Concentration(Base):
    __tablename__ = "concentration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concentration_title = Column(String(255), nullable=False, unique=True)
    # concentration_code = Column(Integer, nullable=False, unique=True)

    perfume = relationship('Perfumes', back_populates='concentration')


class Brands(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    perfume = relationship('Perfumes', back_populates='brand')


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_name = Column(String(255), nullable=False, unique=True)

    perfume_note = relationship('PerfumeNotes', back_populates='note')


class NoteTypes(Base):
    __tablename__ = "note_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_type_data = Column(String(255), nullable=False, unique=True)

    perfume_note = relationship('PerfumeNotes', back_populates='note_type')


class PerfumeNotes(Base):
    __tablename__ = "perfume_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    perfume_id = Column(Integer, ForeignKey('perfumes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    note_type_id = Column(Integer, ForeignKey('note_types.id', ondelete='CASCADE', onupdate='CASCADE') ,nullable=False)

    perfume = relationship('Perfumes', back_populates='perfume_note')
    note = relationship('Notes', back_populates='perfume_note')
    note_type = relationship('NoteTypes', back_populates='perfume_note')



