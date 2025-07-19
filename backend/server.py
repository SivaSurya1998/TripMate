from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import models and database functions
from models import (
    TripType as TripTypePydantic, PackingItem, PackingItemCreate, PackingItemUpdate,
    ItineraryEvent as ItineraryEventPydantic, ItineraryEventCreate, ItineraryEventUpdate,
    ExchangeRate as ExchangeRatePydantic, ExchangeRateCreate, ExchangeRateUpdate, Currency,
    ConversionRequest
)
from database import (
    get_db, create_tables, initialize_default_data,
    TripType as TripTypeDB, ItineraryEvent as ItineraryEventDB, ExchangeRate as ExchangeRateDB
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Supported currencies
SUPPORTED_CURRENCIES = [
    Currency(code="USD", name="US Dollar", symbol="$"),
    Currency(code="EUR", name="Euro", symbol="€"),
    Currency(code="GBP", name="British Pound", symbol="£"),
    Currency(code="JPY", name="Japanese Yen", symbol="¥"),
    Currency(code="CAD", name="Canadian Dollar", symbol="C$"),
    Currency(code="AUD", name="Australian Dollar", symbol="A$")
]

# Basic health check
@api_router.get("/")
async def root():
    return {"message": "TripMate API is running!"}

# =============================================================================
# PACKING LIST ENDPOINTS
# =============================================================================

@api_router.get("/trip-types", response_model=List[TripTypePydantic])
async def get_trip_types(db: AsyncSession = Depends(get_db)):
    """Get all available trip types with their default packing items"""
    result = await db.execute(select(TripTypeDB))
    trip_types = result.scalars().all()
    
    return [TripTypePydantic(
        id=trip_type.id,
        name=trip_type.name,
        icon=trip_type.icon,
        color=trip_type.color,
        items=[PackingItem(**item) for item in trip_type.items]
    ) for trip_type in trip_types]

@api_router.get("/trip-types/{trip_id}", response_model=TripTypePydantic)
async def get_trip_type(trip_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific trip type by ID"""
    result = await db.execute(select(TripTypeDB).where(TripTypeDB.id == trip_id))
    trip_type = result.scalar_one_or_none()
    
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    return TripTypePydantic(
        id=trip_type.id,
        name=trip_type.name,
        icon=trip_type.icon,
        color=trip_type.color,
        items=[PackingItem(**item) for item in trip_type.items]
    )

@api_router.post("/trip-types/{trip_id}/items", response_model=PackingItem)
async def add_packing_item(trip_id: str, item: PackingItemCreate, db: AsyncSession = Depends(get_db)):
    """Add a new packing item to a trip type"""
    result = await db.execute(select(TripTypeDB).where(TripTypeDB.id == trip_id))
    trip_type = result.scalar_one_or_none()
    
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    new_item = {
        "id": str(len(trip_type.items) + 1000),  # Simple ID generation
        "name": item.name,
        "category": item.category,
        "packed": False
    }
    
    updated_items = trip_type.items + [new_item]
    trip_type.items = updated_items
    
    await db.commit()
    await db.refresh(trip_type)
    
    return PackingItem(**new_item)

@api_router.put("/trip-types/{trip_id}/items/{item_id}", response_model=PackingItem)
async def update_packing_item(trip_id: str, item_id: str, item_update: PackingItemUpdate, db: AsyncSession = Depends(get_db)):
    """Update a packing item (mainly for toggling packed status)"""
    result = await db.execute(select(TripTypeDB).where(TripTypeDB.id == trip_id))
    trip_type = result.scalar_one_or_none()
    
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    item_found = False
    updated_items = []
    for item in trip_type.items:
        if item["id"] == item_id:
            item["packed"] = item_update.packed
            item_found = True
        updated_items.append(item)
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    trip_type.items = updated_items
    await db.commit()
    await db.refresh(trip_type)
    
    return PackingItem(**next(item for item in trip_type.items if item["id"] == item_id))

@api_router.delete("/trip-types/{trip_id}/items/{item_id}")
async def delete_packing_item(trip_id: str, item_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a packing item from a trip type"""
    result = await db.execute(select(TripTypeDB).where(TripTypeDB.id == trip_id))
    trip_type = result.scalar_one_or_none()
    
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    original_length = len(trip_type.items)
    updated_items = [item for item in trip_type.items if item["id"] != item_id]
    
    if len(updated_items) == original_length:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    trip_type.items = updated_items
    await db.commit()
    
    return {"message": "Packing item deleted successfully"}

# =============================================================================
# ITINERARY ENDPOINTS
# =============================================================================

@api_router.get("/events", response_model=List[ItineraryEventPydantic])
async def get_events(db: AsyncSession = Depends(get_db)):
    """Get all itinerary events sorted by date and time"""
    result = await db.execute(select(ItineraryEventDB).order_by(ItineraryEventDB.date, ItineraryEventDB.time))
    events = result.scalars().all()
    
    return [ItineraryEventPydantic(
        id=event.id,
        title=event.title,
        date=event.date,
        time=event.time,
        location=event.location,
        description=event.description,
        type=event.type,
        icon=event.icon,
        created_at=event.created_at
    ) for event in events]

@api_router.post("/events", response_model=ItineraryEventPydantic)
async def create_itinerary_event(event: ItineraryEventCreate, db: AsyncSession = Depends(get_db)):
    """Create a new itinerary event"""
    # Map event type to icon
    type_icons = {
        "flight": "✈️",
        "accommodation": "🏨",
        "dining": "🍽️",
        "activity": "📅"
    }
    
    new_event = ItineraryEventDB(
        id=str(int(datetime.utcnow().timestamp() * 1000)),  # Simple ID generation
        title=event.title,
        date=event.date,
        time=event.time,
        location=event.location,
        description=event.description,
        type=event.type,
        icon=type_icons.get(event.type, "📅"),
        created_at=datetime.utcnow()
    )
    
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    return ItineraryEventPydantic(
        id=new_event.id,
        title=new_event.title,
        date=new_event.date,
        time=new_event.time,
        location=new_event.location,
        description=new_event.description,
        type=new_event.type,
        icon=new_event.icon,
        created_at=new_event.created_at
    )

@api_router.put("/events/{event_id}", response_model=ItineraryEventPydantic)
async def update_itinerary_event(event_id: str, event_update: ItineraryEventUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing itinerary event"""
    result = await db.execute(select(ItineraryEventDB).where(ItineraryEventDB.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    
    return ItineraryEventPydantic(
        id=event.id,
        title=event.title,
        date=event.date,
        time=event.time,
        location=event.location,
        description=event.description,
        type=event.type,
        icon=event.icon,
        created_at=event.created_at
    )

@api_router.delete("/events/{event_id}")
async def delete_itinerary_event(event_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an itinerary event"""
    result = await db.execute(select(ItineraryEventDB).where(ItineraryEventDB.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await db.delete(event)
    await db.commit()
    
    return {"message": "Event deleted successfully"}

# =============================================================================
# CURRENCY CONVERTER ENDPOINTS
# =============================================================================

@api_router.get("/currencies", response_model=List[Currency])
async def get_currencies():
    """Get all supported currencies"""
    return SUPPORTED_CURRENCIES

@api_router.get("/exchange-rates", response_model=List[ExchangeRatePydantic])
async def get_exchange_rates(db: AsyncSession = Depends(get_db)):
    """Get all exchange rates"""
    result = await db.execute(select(ExchangeRateDB))
    rates = result.scalars().all()
    
    return [ExchangeRatePydantic(
        id=rate.id,
        from_currency=rate.from_currency,
        to_currency=rate.to_currency,
        rate=rate.rate,
        last_updated=rate.last_updated
    ) for rate in rates]

@api_router.post("/convert", response_model=dict)
async def convert_currency(conversion: ConversionRequest, db: AsyncSession = Depends(get_db)):
    """Convert currency from one to another"""
    # Try to find direct exchange rate
    result = await db.execute(select(ExchangeRateDB).where(
        ExchangeRateDB.from_currency == conversion.from_currency,
        ExchangeRateDB.to_currency == conversion.to_currency
    ))
    rate = result.scalar_one_or_none()
    
    if rate:
        converted_amount = conversion.amount * rate.rate
        return {
            "amount": conversion.amount,
            "from_currency": conversion.from_currency,
            "to_currency": conversion.to_currency,
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": rate.rate
        }
    
    # Try inverse rate
    result = await db.execute(select(ExchangeRateDB).where(
        ExchangeRateDB.from_currency == conversion.to_currency,
        ExchangeRateDB.to_currency == conversion.from_currency
    ))
    inverse_rate = result.scalar_one_or_none()
    
    if inverse_rate:
        converted_amount = conversion.amount / inverse_rate.rate
        return {
            "amount": conversion.amount,
            "from_currency": conversion.from_currency,
            "to_currency": conversion.to_currency,
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": round(1 / inverse_rate.rate, 4)
        }
    
    raise HTTPException(status_code=404, detail="Exchange rate not found")

@api_router.put("/exchange-rates/{from_currency}/{to_currency}")
async def update_rate(from_currency: str, to_currency: str, rate_update: ExchangeRateUpdate, db: AsyncSession = Depends(get_db)):
    """Update an exchange rate"""
    result = await db.execute(select(ExchangeRateDB).where(
        ExchangeRateDB.from_currency == from_currency,
        ExchangeRateDB.to_currency == to_currency
    ))
    rate = result.scalar_one_or_none()
    
    if rate:
        rate.rate = rate_update.rate
        rate.last_updated = "2025-07-10"
    else:
        # Create new rate if it doesn't exist
        rate = ExchangeRateDB(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate_update.rate,
            last_updated="2025-07-10"
        )
        db.add(rate)
    
    await db.commit()
    return {"message": f"Exchange rate updated: {from_currency} to {to_currency} = {rate_update.rate}"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Initialize the database with tables and default data on startup"""
    await create_tables()
    await initialize_default_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    pass