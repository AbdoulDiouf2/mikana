from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Création de la base de données SQLite avec support multi-thread
DATABASE_URL = "sqlite:///./predictions.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True  # Pour le débogage
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    article = Column(String)
    quantity_ordered = Column(Float)
    quantity_predicted = Column(Float)
    delivery_rate = Column(Float)
    status = Column(String)
    recommendation = Column(String)
    created_at = Column(DateTime)

# Créer les tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
