from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)  # 📌 НОВОЕ: Имя
    last_name = Column(String, nullable=False)   # 📌 НОВОЕ: Фамилия
    middle_name = Column(String)                 # 📌 НОВОЕ: Отчество
    birth_date = Column(Date, nullable=False)    # 📌 НОВОЕ: Дата рождения
    
    wings = relationship("Wing", back_populates="owner")

class Type(Base):
    __tablename__ = "types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    wings = relationship("Wing", back_populates="type")

class Wing(Base):
    __tablename__ = "wings"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("types.id"), nullable=False)
    profit = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    
    owner = relationship("Owner", back_populates="wings")
    type = relationship("Type", back_populates="wings")
    moves = relationship("Move", back_populates="wing")

class Place(Base):
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, nullable=False)
    scale = Column(Float, nullable=False)
    
    moves = relationship("Move", back_populates="place")

class Move(Base):
    __tablename__ = "moves"
    
    id = Column(Integer, primary_key=True, index=True)
    wing_id = Column(Integer, ForeignKey("wings.id"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    price = Column(Float, nullable=False)
    dt = Column(DateTime, default=datetime.utcnow)
    
    wing = relationship("Wing", back_populates="moves")
    place = relationship("Place", back_populates="moves")