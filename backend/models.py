from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

# =============================================================================
# PYDANTIC MODELS FOR API
# =============================================================================

# Packing List Models
class PackingItemBase(BaseModel):
    name: str
    category: str
    packed: bool = False

class PackingItem(PackingItemBase):
    id: str

class PackingItemCreate(BaseModel):
    name: str
    category: str = "custom"

class PackingItemUpdate(BaseModel):
    packed: bool

class TripTypeBase(BaseModel):
    name: str
    icon: str
    color: str

class TripType(TripTypeBase):
    id: str
    items: List[PackingItem] = []

# Itinerary Models
class ItineraryEventBase(BaseModel):
    title: str
    date: str
    time: str
    location: str
    description: str
    type: str = "activity"

class ItineraryEvent(ItineraryEventBase):
    id: str
    icon: str = "📅"
    created_at: datetime

class ItineraryEventCreate(ItineraryEventBase):
    pass

class ItineraryEventUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

# Currency Converter Models
class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float

class ExchangeRate(ExchangeRateBase):
    id: str
    last_updated: str

class ExchangeRateCreate(ExchangeRateBase):
    pass

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

class ConversionResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    exchange_rate: float