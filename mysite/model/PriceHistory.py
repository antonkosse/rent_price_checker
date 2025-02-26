from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PriceHistory(Base):
    __tablename__ = 'PRICE_HISTORY'

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.id'))
    price = Column(Integer)
    recorded_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<PriceHistory(id={self.id}, listing_id='{self.listing_id}', price='{self.price}', recorded_at='{self.recorded_at}')>"