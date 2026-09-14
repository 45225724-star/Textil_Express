# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta del archivo de base de datos SQLite local en Visual Studio Code
SQLALCHEMY_DATABASE_URL = "sqlite:///textil_express.db"

# Creación del motor de conexión SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos ORM
Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    print("Base de datos SQLite inicializada exitosamente para Textil Express.")