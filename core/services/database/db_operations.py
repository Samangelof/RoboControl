from sqlalchemy.orm import Session
from .models import Document


def add_document(db: Session, doc_number: str):
    db_doc = Document(document_number=doc_number)
    db.add(db_doc)
    db.commit()

def document_exists(db: Session, doc_number: str) -> bool:
    return db.query(Document).filter_by(document_number=doc_number).first() is not None
