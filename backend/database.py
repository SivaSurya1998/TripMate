from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, Float, DateTime, Text, Integer, JSON
from datetime import datetime
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///./tripmate.db')

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# =============================================================================
# DATABASE MODELS
# =============================================================================

class TripType(Base):
    __tablename__ = "trip_types"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    color = Column(String, nullable=False)
    items = Column(JSON, nullable=False, default=list)  # Store items as JSON

class ItineraryEvent(Base):
    __tablename__ = "itinerary_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
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
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Initialize default data
async def initialize_default_data():
    """Initialize the database with default trip types and exchange rates"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # Check if trip types already exist
        result = await session.execute(select(TripType))
        existing_trip_types = result.scalars().all()
        
        if not existing_trip_types:
            # Create default trip types with items as JSON
            default_trip_types = [
                TripType(
                    id="beach",
                    name="Beach Getaway",
                    icon="🏖️",
                    color="from-blue-400 to-cyan-300",
                    items=[
                        {"id": "1", "name": "Sunscreen SPF 50+", "category": "essentials", "packed": False},
                        {"id": "2", "name": "Swimwear", "category": "clothing", "packed": False},
                        {"id": "3", "name": "Beach towel", "category": "essentials", "packed": False},
                        {"id": "4", "name": "Flip flops", "category": "footwear", "packed": False},
                        {"id": "5", "name": "Sunglasses", "category": "accessories", "packed": False},
                        {"id": "6", "name": "Beach hat", "category": "accessories", "packed": False},
                        {"id": "7", "name": "Water bottle", "category": "essentials", "packed": False},
                    ]
                ),
                TripType(
                    id="city",
                    name="City Explorer",
                    icon="🏙️",
                    color="from-purple-400 to-pink-300",
                    items=[
                        {"id": "8", "name": "Comfortable walking shoes", "category": "footwear", "packed": False},
                        {"id": "9", "name": "Portable charger", "category": "electronics", "packed": False},
                        {"id": "10", "name": "Day backpack", "category": "accessories", "packed": False},
                        {"id": "11", "name": "City map/guidebook", "category": "essentials", "packed": False},
                        {"id": "12", "name": "Camera", "category": "electronics", "packed": False},
                        {"id": "13", "name": "Light jacket", "category": "clothing", "packed": False},
                        {"id": "14", "name": "Reusable water bottle", "category": "essentials", "packed": False},
                    ]
                ),
                TripType(
                    id="business",
                    name="Business Trip",
                    icon="💼",
                    color="from-gray-400 to-slate-300",
                    items=[
                        {"id": "15", "name": "Business cards", "category": "essentials", "packed": False},
                        {"id": "16", "name": "Laptop + charger", "category": "electronics", "packed": False},
                        {"id": "17", "name": "Professional attire", "category": "clothing", "packed": False},
                        {"id": "18", "name": "Dress shoes", "category": "footwear", "packed": False},
                        {"id": "19", "name": "Portfolio/documents", "category": "essentials", "packed": False},
                        {"id": "20", "name": "Phone charger", "category": "electronics", "packed": False},
                        {"id": "21", "name": "Travel adapter", "category": "electronics", "packed": False},
                    ]
                )
            ]
            session.add_all(default_trip_types)
            await session.commit()
        
        # Check if exchange rates already exist
        result = await session.execute(select(ExchangeRate))
        existing_rates = result.scalars().all()
        
        if not existing_rates:
            default_exchange_rates = [
                ExchangeRate(id="usd_eur", from_currency="USD", to_currency="EUR", rate=0.85, last_updated="2025-07-10"),
                ExchangeRate(id="usd_gbp", from_currency="USD", to_currency="GBP", rate=0.73, last_updated="2025-07-10"),
                ExchangeRate(id="usd_jpy", from_currency="USD", to_currency="JPY", rate=110.25, last_updated="2025-07-10"),
                ExchangeRate(id="eur_usd", from_currency="EUR", to_currency="USD", rate=1.18, last_updated="2025-07-10"),
                ExchangeRate(id="gbp_usd", from_currency="GBP", to_currency="USD", rate=1.37, last_updated="2025-07-10"),
                ExchangeRate(id="jpy_usd", from_currency="JPY", to_currency="USD", rate=0.0091, last_updated="2025-07-10"),
            ]
            session.add_all(default_exchange_rates)
            await session.commit()