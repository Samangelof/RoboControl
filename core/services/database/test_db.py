from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Document
from db_operations import add_document, document_exists


# connect SQLite in a memory
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=True)

# create tables
Base.metadata.create_all(bind=engine)

# create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


test_doc_number = "DOC-123"

print(f"Документ {test_doc_number} существует? {document_exists(db, test_doc_number)}")
add_document(db, test_doc_number)
print(f"Документ {test_doc_number} существует? {document_exists(db, test_doc_number)}")

db.close()