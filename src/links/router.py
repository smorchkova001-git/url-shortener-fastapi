from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta, timezone
import random
import string
from typing import Optional
from fastapi.responses import RedirectResponse, Response
import qrcode
import io
from sqlalchemy import func
from collections import Counter

from src.core.database import get_async_session
from src.links.models import Link, Click
from src.links.schemas import LinkCreate, LinkUpdate, LinkResponse, LinkStats
from src.auth.users import current_active_user, current_user_optional
from src.auth.db import User
from .utils import delete_unused_links

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

router = APIRouter()

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/shorten", response_model=LinkResponse)
async def create_short_link(
    link_data: LinkCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(current_user_optional)
):
    if link_data.custom_alias:
        short_code = link_data.custom_alias
        existing = await session.execute(
            select(Link).where(Link.short_code == short_code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom alias already exists"
            )
    else:
        short_code = generate_short_code()
        while True:
            existing = await session.execute(
                select(Link).where(Link.short_code == short_code)
            )
            if not existing.scalar_one_or_none():
                break
            short_code = generate_short_code()

    user_id = current_user.id if current_user else None

    new_link = Link(
        short_code=short_code,
        original_url=str(link_data.original_url),
        custom_alias=link_data.custom_alias,
        user_id=user_id,
        expires_at=link_data.expires_at
    )
    session.add(new_link)
    await session.commit()
    await FastAPICache.clear(namespace="fastapi-cache")
    await session.refresh(new_link)

    return new_link

@router.get("/search", response_model=list[LinkResponse]) 
@cache(expire=60)
async def search_by_original_url(
    original_url: str,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Link).where(Link.original_url.contains(original_url))
    )
    links = result.scalars().all()
    return links

@router.post("/cleanup-unused")
async def cleanup_unused(days: int = 30):
    deleted = await delete_unused_links(days)
    return {"deleted_count": deleted, "older_than_days": days}

@router.get("/unused")
async def get_unused_links(
    days: int = 30,
    session: AsyncSession = Depends(get_async_session)
):
    threshold = datetime.now() - timedelta(days=days)
    result = await session.execute(
        select(Link).where(Link.last_accessed < threshold)
    )
    links = result.scalars().all()
    return links if links else []


@router.get("/{short_code}/qr")
async def get_qr_code(
    short_code: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    
    base_url = str(request.base_url).rstrip('/')
    short_url = f"{base_url}/{short_code}"
    qr.add_data(short_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return Response(content=img_io.getvalue(), media_type="image/png")

@router.get("/{short_code}/stats", response_model=LinkStats)
@cache(expire=60)
async def get_link_stats(
    short_code: str,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    return link

@router.put("/{short_code}", response_model=LinkResponse)
async def update_link(
    short_code: str,
    link_data: LinkUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    link.original_url = str(link_data.original_url)
    await session.commit()
    await FastAPICache.clear(namespace="fastapi-cache")
    await session.refresh(link)

    return link

@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    await session.delete(link)
    await session.commit()
    await FastAPICache.clear(namespace="fastapi-cache")
    return None


@router.get("/{short_code}/analytics")
async def get_link_analytics(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    result = await session.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Доступ только у владельца
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result = await session.execute(
        select(Click).where(Click.link_id == link.id).order_by(Click.accessed_at.desc())
    )
    clicks = result.scalars().all()

    total_clicks = len(clicks)
    unique_referers = len(set(c.referer for c in clicks if c.referer))

    return {
        "total_clicks": total_clicks,
        "unique_referers": unique_referers,
        "last_10_clicks": clicks[:10]
    }