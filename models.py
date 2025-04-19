from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Summary(Base):
    __tablename__ = "Summaries"  # Corrected table name to lowercase

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    source = Column(String, nullable=False)  # Made 'source' non-nullable
    content = Column(Text, nullable=False)  # Made 'content' non-nullable
    summary = Column(Text, nullable=False)  # Made 'summary' non-nullable
    language = Column(String)  # Optional 'language' column
    sentiment = Column(String)  # Optional 'sentiment' column

    def __repr__(self):
        return f"<Summary(id={self.id}, source={self.source}, language={self.language}, sentiment={self.sentiment})>"
