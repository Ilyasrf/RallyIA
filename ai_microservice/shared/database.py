from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/igudar_ai"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float, nullable=True)
    min_investment = Column(Float)
    investment_period = Column(Integer)
    risk_assessment = Column(String)
    rental_yield = Column(Float, nullable=True)
    expected_roi = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    embedding = Column(Vector(384))
