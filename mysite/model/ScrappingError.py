from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ScrappingError(Base):
    __tablename__ = 'SCRAPPING_ERROR'

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.id'))
    error_message = Column(Text)
    recorded_at = Column(TIMESTAMP)

    def __repr__(self):
        return (f"<ScrappingError(id={self.id}, listing_id='{self.listing_id}',"
                f" error_message='{self.error_message}',"
                f" recorded_at='{self.recorded_at}')>")