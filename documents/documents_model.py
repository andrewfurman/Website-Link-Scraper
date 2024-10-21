# documents/documents_model.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from source_websites.source_website_model import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_website_id = Column(Integer, ForeignKey('source_websites.id'), nullable=True)
    title = Column(Text, nullable=True)
    author = Column(Text, nullable=True)
    full_contents = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Add relationship to DocumentSection
    sections = relationship("DocumentSection", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', url='{self.url}')>"

class DocumentSection(Base):
    __tablename__ = 'document_sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    document_text = Column(Text, nullable=True)
    custom_prompt = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Add relationship to Document
    document = relationship("Document", back_populates="sections")

    def __repr__(self):
        return f"<DocumentSection(id={self.id}, document_id={self.document_id}, start_page={self.start_page}, end_page={self.end_page})>"