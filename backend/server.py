from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

# Import database and models
from database import (
    get_db, create_tables, initialize_default_data,
    TripType as DBTripType, PackingItem as DBPackingItem, 
    ItineraryEvent as DBItineraryEvent, ExchangeRate as DBExchangeRate
)
from models import (
    TripType, PackingItem, PackingItemCreate, PackingItemUpdate,
    ItineraryEvent, ItineraryEventCreate, ItineraryEventUpdate,
    ExchangeRate, ExchangeRateCreate, ExchangeRateUpdate, Currency,
    ConversionRequest, ConversionResponse
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

@api_router.get("/trip-types", response_model=List[TripType])
async def get_trip_types(db: Session = Depends(get_db)):
    """Get all available trip types with their default packing items"""
    trip_types = db.query(DBTripType).all()
    result = []
    for trip_type in trip_types:
        items = [PackingItem(id=item.id, name=item.name, category=item.category, packed=item.packed) 
                for item in trip_type.items]
        result.append(TripType(
            id=trip_type.id,
            name=trip_type.name,
            icon=trip_type.icon,
            color=trip_type.color,
            items=items
        ))
    return result

@api_router.get("/trip-types/{trip_id}", response_model=TripType)
async def get_trip_type(trip_id: str, db: Session = Depends(get_db)):
    """Get a specific trip type by ID"""
    trip_type = db.query(DBTripType).filter(DBTripType.id == trip_id).first()
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    items = [PackingItem(id=item.id, name=item.name, category=item.category, packed=item.packed) 
            for item in trip_type.items]
    
    return TripType(
        id=trip_type.id,
        name=trip_type.name,
        icon=trip_type.icon,
        color=trip_type.color,
        items=items
    )

@api_router.post("/trip-types/{trip_id}/items", response_model=PackingItem)
async def add_packing_item(trip_id: str, item: PackingItemCreate, db: Session = Depends(get_db)):
    """Add a new packing item to a trip type"""
    trip_type = db.query(DBTripType).filter(DBTripType.id == trip_id).first()
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    new_item = DBPackingItem(
        name=item.name,
        category=item.category,
        trip_type_id=trip_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return PackingItem(id=new_item.id, name=new_item.name, category=new_item.category, packed=new_item.packed)

@api_router.put("/trip-types/{trip_id}/items/{item_id}", response_model=PackingItem)
async def update_packing_item(trip_id: str, item_id: str, item_update: PackingItemUpdate, db: Session = Depends(get_db)):
    """Update a packing item (mainly for toggling packed status)"""
    item = db.query(DBPackingItem).filter(
        DBPackingItem.id == item_id,
        DBPackingItem.trip_type_id == trip_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    item.packed = item_update.packed
    db.commit()
    db.refresh(item)
    
    return PackingItem(id=item.id, name=item.name, category=item.category, packed=item.packed)

@api_router.delete("/trip-types/{trip_id}/items/{item_id}")
async def delete_packing_item(trip_id: str, item_id: str, db: Session = Depends(get_db)):
    """Delete a packing item from a trip type"""
    item = db.query(DBPackingItem).filter(
        DBPackingItem.id == item_id,
        DBPackingItem.trip_type_id == trip_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Packing item deleted successfully"}

# =============================================================================
# ITINERARY ENDPOINTS
# =============================================================================

@api_router.get("/events", response_model=List[ItineraryEvent])
async def get_events(db: Session = Depends(get_db)):
    """Get all itinerary events sorted by date and time"""
    events = db.query(DBItineraryEvent).order_by(DBItineraryEvent.date, DBItineraryEvent.time).all()
    return [ItineraryEvent(
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

@api_router.post("/events", response_model=ItineraryEvent)
async def create_itinerary_event(event: ItineraryEventCreate, db: Session = Depends(get_db)):
    """Create a new itinerary event"""
    # Map event type to icon
    type_icons = {
        "flight": "✈️",
        "accommodation": "🏨",
        "dining": "🍽️",
        "activity": "📅"
    }
    
    new_event = DBItineraryEvent(
        title=event.title,
        date=event.date,
        time=event.time,
        location=event.location,
        description=event.description,
        type=event.type,
        icon=type_icons.get(event.type, "📅")
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return ItineraryEvent(
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

@api_router.put("/events/{event_id}", response_model=ItineraryEvent)
async def update_itinerary_event(event_id: str, event_update: ItineraryEventUpdate, db: Session = Depends(get_db)):
    """Update an existing itinerary event"""
    event = db.query(DBItineraryEvent).filter(DBItineraryEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return ItineraryEvent(
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
async def delete_itinerary_event(event_id: str, db: Session = Depends(get_db)):
    """Delete an itinerary event"""
    event = db.query(DBItineraryEvent).filter(DBItineraryEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}

# =============================================================================
# CURRENCY CONVERTER ENDPOINTS
# =============================================================================

@api_router.get("/currencies", response_model=List[Currency])
async def get_currencies():
    """Get all supported currencies"""
    return SUPPORTED_CURRENCIES

@api_router.get("/exchange-rates", response_model=List[ExchangeRate])
async def get_exchange_rates(db: Session = Depends(get_db)):
    """Get all exchange rates"""
    rates = db.query(DBExchangeRate).all()
    return [ExchangeRate(
        id=rate.id,
        from_currency=rate.from_currency,
        to_currency=rate.to_currency,
        rate=rate.rate,
        last_updated=rate.last_updated
    ) for rate in rates]

@api_router.post("/convert", response_model=ConversionResponse)
async def convert_currency(conversion: ConversionRequest, db: Session = Depends(get_db)):
    """Convert currency from one to another"""
    # Try to find direct exchange rate
    rate = db.query(DBExchangeRate).filter(
        DBExchangeRate.from_currency == conversion.from_currency,
        DBExchangeRate.to_currency == conversion.to_currency
    ).first()
    
    if rate:
        converted_amount = conversion.amount * rate.rate
        return ConversionResponse(
            amount=conversion.amount,
            from_currency=conversion.from_currency,
            to_currency=conversion.to_currency,
            converted_amount=round(converted_amount, 2),
            exchange_rate=rate.rate
        )
    
    # Try inverse rate
    inverse_rate = db.query(DBExchangeRate).filter(
        DBExchangeRate.from_currency == conversion.to_currency,
        DBExchangeRate.to_currency == conversion.from_currency
    ).first()
    
    if inverse_rate:
        converted_amount = conversion.amount / inverse_rate.rate
        return ConversionResponse(
            amount=conversion.amount,
            from_currency=conversion.from_currency,
            to_currency=conversion.to_currency,
            converted_amount=round(converted_amount, 2),
            exchange_rate=round(1 / inverse_rate.rate, 4)
        )
    
    raise HTTPException(status_code=404, detail="Exchange rate not found")

@api_router.put("/exchange-rates/{from_currency}/{to_currency}")
async def update_rate(from_currency: str, to_currency: str, rate_update: ExchangeRateUpdate, db: Session = Depends(get_db)):
    """Update an exchange rate"""
    rate = db.query(DBExchangeRate).filter(
        DBExchangeRate.from_currency == from_currency,
        DBExchangeRate.to_currency == to_currency
    ).first()
    
    if rate:
        rate.rate = rate_update.rate
        rate.last_updated = "2025-07-10"
    else:
        # Create new rate if it doesn't exist
        rate = DBExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate_update.rate,
            last_updated="2025-07-10"
        )
        db.add(rate)
    
    db.commit()
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
    create_tables()
    # Initialize default data
    db = next(get_db())
    try:
        initialize_default_data(db)
    finally:
        db.close()