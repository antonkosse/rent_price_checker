from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AvailabilityHistory(Base):
    __tablename__ = 'AVAILABILITY_HISTORY'

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.id'))
    is_available = Column(Boolean)
    changed_at = Column(TIMESTAMP)

    def __repr__(self):
        return (f"<AvailabilityHistory(id={self.id}, listing_id='{self.listing_id}', is_available='{self.is_available}',"
                f" changed_at='{self.changed_at}')>")