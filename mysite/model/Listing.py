from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Listing(Base):
    __tablename__ = 'LISTING'

    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True)
    title = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    number_of_rooms = Column(Integer)
    total_area = Column(DECIMAL)
    floor = Column(Integer)
    created_at = Column(TIMESTAMP)
    last_checked_at = Column(TIMESTAMP)
    original_price = Column(Integer)
    source_website = Column(String(100))

    def __repr__(self):
        return (f"<Listing(id={self.id},"
                f" url='{self.url}',"
                f" title='{self.title}',"
                f" description='{self.description}',"
                f" location='{self.location}',"
                f" number_of_rooms='{self.number_of_rooms}',"
                f" total_area='{self.total_area}',"
                f" floor='{self.floor}',"
                f" floor='{self.floor}',"
                f" location='{self.location}')>")
