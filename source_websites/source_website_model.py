from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SourceWebsite(Base):
    __tablename__ = 'source_websites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    author = Column(String(255))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    full_text = Column(Text)
    found_urls = Column(Text)

    def __repr__(self):
        return f"<SourceWebsite(id={self.id}, title='{self.title}', url='{self.url}')>"