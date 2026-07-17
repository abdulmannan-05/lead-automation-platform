from pydantic import BaseModel, Field
from typing import Optional


class ScrapeJobRequest(BaseModel):
    business_type: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=100)
    max_results: int = Field(default=50, ge=1, le=500)


class EmailCampaignRequest(BaseModel):
    subject: Optional[str] = Field(default=None, max_length=200)
    body_template: Optional[str] = Field(default=None, max_length=5000)
    delay_seconds_between: int = Field(default=10, ge=1, le=300)


        