from pydantic import BaseModel, HttpUrl
from typing import Optional


class RawGoogleMapsLead(BaseModel):
    """
    Represents one cleaned business record, mapped from raw Apify output.
    This is the shape everything downstream (crawler, sheets writer) will work with.
    """
    business_name: str
    category: Optional[str] = None
    all_categories: Optional[str] = None  # comma-joined list
    address: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    google_rating: Optional[float] = None
    review_count: Optional[int] = None
    google_maps_url: Optional[str] = None
    place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    search_query: Optional[str] = None
    country_code: Optional[str] = None
    
    class Config:
        extra = "ignore"  # silently ignore any fields we didn't define