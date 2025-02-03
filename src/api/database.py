from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuration MySQL
MYSQL_USER = os.getenv("MYSQL_USER", "mikana_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "mikana_password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "mikana_db")

# URL de connexion MySQL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Configuration du moteur avec des paramètres optimisés pour MySQL
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Pour le débogage
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    article = Column(String(255), nullable=False)
    quantity_ordered = Column(Numeric(10, 2), nullable=False)  # Plus précis qu'un Float
    quantity_predicted = Column(Numeric(10, 2), nullable=False)
    delivery_rate = Column(Numeric(5, 2), nullable=False)
    status = Column(String(50), nullable=False)
    recommendation = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "article": self.article,
            "quantity_ordered": float(self.quantity_ordered),
            "quantity_predicted": float(self.quantity_predicted),
            "delivery_rate": float(self.delivery_rate),
            "status": self.status,
            "recommendation": self.recommendation
        }

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialisation de la base si c'est le fichier principal
if __name__ == "__main__":
    init_db()