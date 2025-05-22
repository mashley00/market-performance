from sqlalchemy import Column, String, Integer, Float, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use SQLite for now — can switch to Postgres later
DATABASE_URL = "sqlite:///./campaign_insights.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class CampaignInsight(Base):
    __tablename__ = "campaign_insights"

    job_number = Column(String, primary_key=True, index=True)
    topic = Column(String)
    city = Column(String)
    state = Column(String)
    first_event_date = Column(Date)
    second_event_date = Column(Date, nullable=True)
    client_name = Column(String)
    num_events = Column(Integer)
    target_registrations = Column(Integer)
    target_attendees = Column(Integer)
    target_cpr = Column(Float)
    campaign_name = Column(String)
    impressions = Column(Integer)
    reach = Column(Integer)
    spend = Column(Float)

def init_db():
    Base.metadata.create_all(bind=engine)
