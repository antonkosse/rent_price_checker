from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserWatchlist(Base):
    __tablename__ = 'USER_WATCHLIST'

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.id'))
    user_email = Column(String(255))
    notify_on_price_change = Column(Boolean)
    notify_on_availability_change = Column(Boolean)
    created_at = Column(TIMESTAMP)

    def __repr__(self):
        return (f"<UserWatchlist(id={self.id}, listing_id='{self.listing_id}',"
                f" user_email='{self.user_email}',"
                f" notify_on_price_change='{self.notify_on_price_change}', "
                f" notify_on_availability_change='{self.notify_on_availability_change}', "
                f" created_at='{self.created_at}')>")