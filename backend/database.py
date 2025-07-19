from sqlalchemy import create_engine, Column, String, Boolean, Float, DateTime, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/tripmate_db')

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# DATABASE MODELS
# =============================================================================

class TripType(Base):
    __tablename__ = "trip_types"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    color = Column(String, nullable=False)
    
    # Relationship to packing items
    items = relationship("PackingItem", back_populates="trip_type", cascade="all, delete-orphan")

class PackingItem(Base):
    __tablename__ = "packing_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="custom")
    packed = Column(Boolean, default=False)
    trip_type_id = Column(String, ForeignKey("trip_types.id"), nullable=False)
    
    # Relationship to trip type
    trip_type = relationship("TripType", back_populates="items")

class ItineraryEvent(Base):
    __tablename__ = "itinerary_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Using string for simplicity, could be Date type
    time = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False, default="activity")
    icon = Column(String, nullable=False, default="📅")
    created_at = Column(DateTime, default=datetime.utcnow)

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency = Column(String, nullable=False)
    to_currency = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    last_updated = Column(String, nullable=False)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize default data
def initialize_default_data(db: Session):
    """Initialize the database with default trip types and exchange rates"""
    
    # Check if trip types already exist
    existing_trip_types = db.query(TripType).count()
    if existing_trip_types == 0:
        # Create default trip types
        beach_trip = TripType(
            id="beach",
            name="Beach Getaway",
            icon="🏖️",
            color="from-blue-400 to-cyan-300"
        )
        
        city_trip = TripType(
            id="city",
            name="City Explorer",
            icon="🏙️",
            color="from-purple-400 to-pink-300"
        )
        
        business_trip = TripType(
            id="business",
            name="Business Trip",
            icon="💼",
            color="from-gray-400 to-slate-300"
        )
        
        db.add_all([beach_trip, city_trip, business_trip])
        db.commit()
        
        # Add default items for beach trip
        beach_items = [
            PackingItem(id="1", name="Sunscreen SPF 50+", category="essentials", trip_type_id="beach"),
            PackingItem(id="2", name="Swimwear", category="clothing", trip_type_id="beach"),
            PackingItem(id="3", name="Beach towel", category="essentials", trip_type_id="beach"),
            PackingItem(id="4", name="Flip flops", category="footwear", trip_type_id="beach"),
            PackingItem(id="5", name="Sunglasses", category="accessories", trip_type_id="beach"),
            PackingItem(id="6", name="Beach hat", category="accessories", trip_type_id="beach"),
            PackingItem(id="7", name="Water bottle", category="essentials", trip_type_id="beach"),
        ]
        
        # Add default items for city trip
        city_items = [
            PackingItem(id="8", name="Comfortable walking shoes", category="footwear", trip_type_id="city"),
            PackingItem(id="9", name="Portable charger", category="electronics", trip_type_id="city"),
            PackingItem(id="10", name="Day backpack", category="accessories", trip_type_id="city"),
            PackingItem(id="11", name="City map/guidebook", category="essentials", trip_type_id="city"),
            PackingItem(id="12", name="Camera", category="electronics", trip_type_id="city"),
            PackingItem(id="13", name="Light jacket", category="clothing", trip_type_id="city"),
            PackingItem(id="14", name="Reusable water bottle", category="essentials", trip_type_id="city"),
        ]
        
        # Add default items for business trip
        business_items = [
            PackingItem(id="15", name="Business cards", category="essentials", trip_type_id="business"),
            PackingItem(id="16", name="Laptop + charger", category="electronics", trip_type_id="business"),
            PackingItem(id="17", name="Professional attire", category="clothing", trip_type_id="business"),
            PackingItem(id="18", name="Dress shoes", category="footwear", trip_type_id="business"),
            PackingItem(id="19", name="Portfolio/documents", category="essentials", trip_type_id="business"),
            PackingItem(id="20", name="Phone charger", category="electronics", trip_type_id="business"),
            PackingItem(id="21", name="Travel adapter", category="electronics", trip_type_id="business"),
        ]
        
        db.add_all(beach_items + city_items + business_items)
        db.commit()
    
    # Check if exchange rates already exist
    existing_rates = db.query(ExchangeRate).count()
    if existing_rates == 0:
        default_exchange_rates = [
            ExchangeRate(id="usd_eur", from_currency="USD", to_currency="EUR", rate=0.85, last_updated="2025-07-10"),
            ExchangeRate(id="usd_gbp", from_currency="USD", to_currency="GBP", rate=0.73, last_updated="2025-07-10"),
            ExchangeRate(id="usd_jpy", from_currency="USD", to_currency="JPY", rate=110.25, last_updated="2025-07-10"),
            ExchangeRate(id="eur_usd", from_currency="EUR", to_currency="USD", rate=1.18, last_updated="2025-07-10"),
            ExchangeRate(id="gbp_usd", from_currency="GBP", to_currency="USD", rate=1.37, last_updated="2025-07-10"),
            ExchangeRate(id="jpy_usd", from_currency="JPY", to_currency="USD", rate=0.0091, last_updated="2025-07-10"),
        ]
        db.add_all(default_exchange_rates)
        db.commit()