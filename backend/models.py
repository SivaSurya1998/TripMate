from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

# Packing List Models
class PackingItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    packed: bool = False

class TripType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    icon: str
    color: str
    items: List[PackingItem] = []

class PackingItemCreate(BaseModel):
    name: str
    category: str = "custom"

class PackingItemUpdate(BaseModel):
    packed: bool

# Itinerary Models
class ItineraryEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    date: str
    time: str
    location: str
    description: str
    type: str = "activity"  # flight, accommodation, dining, activity
    icon: str = "📅"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ItineraryEventCreate(BaseModel):
    title: str
    date: str
    time: str
    location: str
    description: str
    type: str = "activity"

class ItineraryEventUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

# Currency Converter Models
class ExchangeRate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_currency: str
    to_currency: str
    rate: float
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%d'))

class ExchangeRateCreate(BaseModel):
    from_currency: str
    to_currency: str
    rate: float

class ExchangeRateUpdate(BaseModel):
    rate: float

class Currency(BaseModel):
    code: str
    name: str
    symbol: str

class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str