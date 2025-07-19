from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import List
from models import TripType, PackingItem, ItineraryEvent, ExchangeRate

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'tripmate_db')]

# Collections
trip_types_collection = db.trip_types
itinerary_events_collection = db.itinerary_events
exchange_rates_collection = db.exchange_rates

# Initialize default data
async def initialize_default_data():
    """Initialize the database with default trip types and exchange rates"""
    
    # Check if trip types already exist
    existing_trip_types = await trip_types_collection.count_documents({})
    if existing_trip_types == 0:
        default_trip_types = [
            {
                "id": "beach",
                "name": "Beach Getaway",
                "icon": "🏖️",
                "color": "from-blue-400 to-cyan-300",
                "items": [
                    {"id": "1", "name": "Sunscreen SPF 50+", "category": "essentials", "packed": False},
                    {"id": "2", "name": "Swimwear", "category": "clothing", "packed": False},
                    {"id": "3", "name": "Beach towel", "category": "essentials", "packed": False},
                    {"id": "4", "name": "Flip flops", "category": "footwear", "packed": False},
                    {"id": "5", "name": "Sunglasses", "category": "accessories", "packed": False},
                    {"id": "6", "name": "Beach hat", "category": "accessories", "packed": False},
                    {"id": "7", "name": "Water bottle", "category": "essentials", "packed": False},
                ]
            },
            {
                "id": "city",
                "name": "City Explorer",
                "icon": "🏙️",
                "color": "from-purple-400 to-pink-300",
                "items": [
                    {"id": "8", "name": "Comfortable walking shoes", "category": "footwear", "packed": False},
                    {"id": "9", "name": "Portable charger", "category": "electronics", "packed": False},
                    {"id": "10", "name": "Day backpack", "category": "accessories", "packed": False},
                    {"id": "11", "name": "City map/guidebook", "category": "essentials", "packed": False},
                    {"id": "12", "name": "Camera", "category": "electronics", "packed": False},
                    {"id": "13", "name": "Light jacket", "category": "clothing", "packed": False},
                    {"id": "14", "name": "Reusable water bottle", "category": "essentials", "packed": False},
                ]
            },
            {
                "id": "business",
                "name": "Business Trip",
                "icon": "💼",
                "color": "from-gray-400 to-slate-300",
                "items": [
                    {"id": "15", "name": "Business cards", "category": "essentials", "packed": False},
                    {"id": "16", "name": "Laptop + charger", "category": "electronics", "packed": False},
                    {"id": "17", "name": "Professional attire", "category": "clothing", "packed": False},
                    {"id": "18", "name": "Dress shoes", "category": "footwear", "packed": False},
                    {"id": "19", "name": "Portfolio/documents", "category": "essentials", "packed": False},
                    {"id": "20", "name": "Phone charger", "category": "electronics", "packed": False},
                    {"id": "21", "name": "Travel adapter", "category": "electronics", "packed": False},
                ]
            }
        ]
        await trip_types_collection.insert_many(default_trip_types)
    
    # Check if exchange rates already exist
    existing_rates = await exchange_rates_collection.count_documents({})
    if existing_rates == 0:
        default_exchange_rates = [
            {"id": "usd_eur", "from_currency": "USD", "to_currency": "EUR", "rate": 0.85, "last_updated": "2025-07-10"},
            {"id": "usd_gbp", "from_currency": "USD", "to_currency": "GBP", "rate": 0.73, "last_updated": "2025-07-10"},
            {"id": "usd_jpy", "from_currency": "USD", "to_currency": "JPY", "rate": 110.25, "last_updated": "2025-07-10"},
            {"id": "eur_usd", "from_currency": "EUR", "to_currency": "USD", "rate": 1.18, "last_updated": "2025-07-10"},
            {"id": "gbp_usd", "from_currency": "GBP", "to_currency": "USD", "rate": 1.37, "last_updated": "2025-07-10"},
            {"id": "jpy_usd", "from_currency": "JPY", "to_currency": "USD", "rate": 0.0091, "last_updated": "2025-07-10"},
        ]
        await exchange_rates_collection.insert_many(default_exchange_rates)

# Database operations for Trip Types
async def get_all_trip_types() -> List[TripType]:
    trip_types = await trip_types_collection.find().to_list(1000)
    return [TripType(**trip_type) for trip_type in trip_types]

async def get_trip_type_by_id(trip_id: str) -> TripType:
    trip_type = await trip_types_collection.find_one({"id": trip_id})
    if trip_type:
        return TripType(**trip_type)
    return None

async def update_trip_type_items(trip_id: str, items: List[PackingItem]):
    items_dict = [item.dict() for item in items]
    await trip_types_collection.update_one(
        {"id": trip_id},
        {"$set": {"items": items_dict}}
    )

# Database operations for Itinerary Events
async def get_all_events() -> List[ItineraryEvent]:
    events = await itinerary_events_collection.find().sort([("date", 1), ("time", 1)]).to_list(1000)
    return [ItineraryEvent(**event) for event in events]

async def create_event(event: ItineraryEvent) -> ItineraryEvent:
    await itinerary_events_collection.insert_one(event.dict())
    return event

async def update_event(event_id: str, event_data: dict):
    await itinerary_events_collection.update_one(
        {"id": event_id},
        {"$set": event_data}
    )

async def delete_event(event_id: str):
    await itinerary_events_collection.delete_one({"id": event_id})

# Database operations for Exchange Rates
async def get_all_exchange_rates() -> List[ExchangeRate]:
    rates = await exchange_rates_collection.find().to_list(1000)
    return [ExchangeRate(**rate) for rate in rates]

async def get_exchange_rate(from_currency: str, to_currency: str) -> ExchangeRate:
    rate = await exchange_rates_collection.find_one({
        "from_currency": from_currency,
        "to_currency": to_currency
    })
    if rate:
        return ExchangeRate(**rate)
    return None

async def update_exchange_rate(from_currency: str, to_currency: str, new_rate: float):
    await exchange_rates_collection.update_one(
        {"from_currency": from_currency, "to_currency": to_currency},
        {"$set": {"rate": new_rate, "last_updated": "2025-07-10"}},
        upsert=True
    )