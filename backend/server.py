from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
from datetime import datetime

# Import models and database functions
from models import (
    TripType, PackingItem, PackingItemCreate, PackingItemUpdate,
    ItineraryEvent, ItineraryEventCreate, ItineraryEventUpdate,
    ExchangeRate, ExchangeRateCreate, ExchangeRateUpdate, Currency,
    ConversionRequest
)
from database import (
    initialize_default_data, get_all_trip_types, get_trip_type_by_id, update_trip_type_items,
    get_all_events, create_event, update_event, delete_event,
    get_all_exchange_rates, get_exchange_rate, update_exchange_rate
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
async def get_trip_types():
    """Get all available trip types with their default packing items"""
    return await get_all_trip_types()

@api_router.get("/trip-types/{trip_id}", response_model=TripType)
async def get_trip_type(trip_id: str):
    """Get a specific trip type by ID"""
    trip_type = await get_trip_type_by_id(trip_id)
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    return trip_type

@api_router.post("/trip-types/{trip_id}/items", response_model=PackingItem)
async def add_packing_item(trip_id: str, item: PackingItemCreate):
    """Add a new packing item to a trip type"""
    trip_type = await get_trip_type_by_id(trip_id)
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    new_item = PackingItem(
        id=str(len(trip_type.items) + 1000),  # Simple ID generation
        **item.dict()
    )
    trip_type.items.append(new_item)
    await update_trip_type_items(trip_id, trip_type.items)
    return new_item

@api_router.put("/trip-types/{trip_id}/items/{item_id}", response_model=PackingItem)
async def update_packing_item(trip_id: str, item_id: str, item_update: PackingItemUpdate):
    """Update a packing item (mainly for toggling packed status)"""
    trip_type = await get_trip_type_by_id(trip_id)
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    item_found = False
    for item in trip_type.items:
        if item.id == item_id:
            item.packed = item_update.packed
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    await update_trip_type_items(trip_id, trip_type.items)
    return next(item for item in trip_type.items if item.id == item_id)

@api_router.delete("/trip-types/{trip_id}/items/{item_id}")
async def delete_packing_item(trip_id: str, item_id: str):
    """Delete a packing item from a trip type"""
    trip_type = await get_trip_type_by_id(trip_id)
    if not trip_type:
        raise HTTPException(status_code=404, detail="Trip type not found")
    
    original_length = len(trip_type.items)
    trip_type.items = [item for item in trip_type.items if item.id != item_id]
    
    if len(trip_type.items) == original_length:
        raise HTTPException(status_code=404, detail="Packing item not found")
    
    await update_trip_type_items(trip_id, trip_type.items)
    return {"message": "Packing item deleted successfully"}

# =============================================================================
# ITINERARY ENDPOINTS
# =============================================================================

@api_router.get("/events", response_model=List[ItineraryEvent])
async def get_events():
    """Get all itinerary events sorted by date and time"""
    return await get_all_events()

@api_router.post("/events", response_model=ItineraryEvent)
async def create_itinerary_event(event: ItineraryEventCreate):
    """Create a new itinerary event"""
    # Map event type to icon
    type_icons = {
        "flight": "✈️",
        "accommodation": "🏨",
        "dining": "🍽️",
        "activity": "📅"
    }
    
    new_event = ItineraryEvent(
        id=str(int(datetime.utcnow().timestamp() * 1000)),  # Simple ID generation
        **event.dict(),
        icon=type_icons.get(event.type, "📅"),
        created_at=datetime.utcnow()
    )
    return await create_event(new_event)

@api_router.put("/events/{event_id}", response_model=ItineraryEvent)
async def update_itinerary_event(event_id: str, event_update: ItineraryEventUpdate):
    """Update an existing itinerary event"""
    # Get current event to check if it exists
    events = await get_all_events()
    current_event = next((e for e in events if e.id == event_id), None)
    if not current_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    update_data = event_update.dict(exclude_unset=True)
    if update_data:
        await update_event(event_id, update_data)
    
    # Return updated event
    updated_events = await get_all_events()
    return next(e for e in updated_events if e.id == event_id)

@api_router.delete("/events/{event_id}")
async def delete_itinerary_event(event_id: str):
    """Delete an itinerary event"""
    events = await get_all_events()
    event_exists = any(e.id == event_id for e in events)
    if not event_exists:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await delete_event(event_id)
    return {"message": "Event deleted successfully"}

# =============================================================================
# CURRENCY CONVERTER ENDPOINTS
# =============================================================================

@api_router.get("/currencies", response_model=List[Currency])
async def get_currencies():
    """Get all supported currencies"""
    return SUPPORTED_CURRENCIES

@api_router.get("/exchange-rates", response_model=List[ExchangeRate])
async def get_exchange_rates():
    """Get all exchange rates"""
    return await get_all_exchange_rates()

@api_router.post("/convert", response_model=dict)
async def convert_currency(conversion: ConversionRequest):
    """Convert currency from one to another"""
    # Try to find direct exchange rate
    rate = await get_exchange_rate(conversion.from_currency, conversion.to_currency)
    
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
    inverse_rate = await get_exchange_rate(conversion.to_currency, conversion.from_currency)
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
async def update_rate(from_currency: str, to_currency: str, rate_update: ExchangeRateUpdate):
    """Update an exchange rate"""
    await update_exchange_rate(from_currency, to_currency, rate_update.rate)
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
    """Initialize the database with default data on startup"""
    await initialize_default_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()