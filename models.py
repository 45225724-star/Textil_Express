# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Usuario(Base):
    __tablename__ = "tbl_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    rol = Column(String(20), default="cliente") # 'cliente' o 'administrador/taller'