from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String, unique=True, nullable=False, index=True)
    processed_at = Column(DateTime, default=func.now(), nullable=False)
