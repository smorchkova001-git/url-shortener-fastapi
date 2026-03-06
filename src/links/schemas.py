from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional
import uuid

class LinkBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None

class LinkCreate(LinkBase):
    expires_at: Optional[datetime] = None

class LinkUpdate(BaseModel):
    original_url: HttpUrl

class LinkResponse(LinkBase):
    id: int
    short_code: str
    user_id: Optional[uuid.UUID]
    created_at: datetime
    click_count: int
    last_accessed: Optional[datetime]
    is_active: bool
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LinkStats(BaseModel):
    original_url: HttpUrl
    created_at: datetime
    click_count: int
    last_accessed: Optional[datetime]
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClickResponse(BaseModel):
    id: int
    link_id: int
    accessed_at: datetime
    referer: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]

    class Config:
        from_attributes = True

class LinkAnalytics(BaseModel):
    total_clicks: int
    unique_referers: int
    clicks_by_date: List[dict]
    last_10_clicks: List[ClickResponse]