from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi.responses import RedirectResponse

from src.core.database import get_async_session
from src.links.models import Link, Click

router = APIRouter(tags=["redirect"])

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Link).where(
            Link.short_code == short_code,
            Link.is_active == True
        )
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This link has expired"
        )

    click = Click(
        link_id=link.id,
        referer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    session.add(click)

    link.click_count += 1
    link.last_accessed = datetime.now(timezone.utc)
    await session.commit()

    return RedirectResponse(url=link.original_url, status_code=302)