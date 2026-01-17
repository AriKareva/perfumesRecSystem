from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import SERIAL

Base = declarative_base()

# Все модели данных, свзанные с парфюмами

class Perfumes(Base):
    __tablename__ = "perfumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    photo = Column(String(255), nullable=True) #фото пока храним локально, возможно позже заменим на облако
    description = Column(Text, nullable=True)
    brand_id  = Column(Integer, ForeignKey('brand.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    concentration_id = Column(Integer, ForeignKey('concentration.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    concentration = relationship('Perfumes', back_populates='concentration')
    brand = relationship('Perfumes', back_populates='brands')
    rating = relationship('Perfumes', back_populates='ratings')
    perfume_note = relationship('Perfumes', back_populates='perfume_notes')


class Concentration(Base):
    __tablename__ = "concentration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concentration_data = Column(String(255), nullable=True, unique=True)

    perfume = relationship('Concentration', back_populates='perfumes')


class Brands(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True, unique=True)

    perfume = relationship('Brands', back_populates='perfumes')


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_name = Column(String(255), nullable=True, unique=True)

    perfume_note = relationship('Notes', back_populates='perfume_notes')


class NoteTypes(Base):
    __tablename__ = "note_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_type_data = Column(String(255), nullable=True, unique=True)

    perfume_note = relationship('NoteTypes', back_populates='perfume_notes')


class PerfumeNotes(Base):
    __tablename__ = "perfume_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    perfume_id = Column(Integer, ForeignKey('perfume.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    node_type_id = Column(Integer, ForeignKey('note_types.id', ondelete='CASCADE', onupdate='CASCADE') ,nullable=False)

    perfume = relationship('PerfumeNotes', back_populates='perfumes')
    note = relationship('PerfumeNotes', back_populates='notes')
    note_type = relationship('PerfumeNotes', back_populates='note_types')



