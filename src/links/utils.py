from sqlalchemy import delete
from datetime import datetime, timedelta
from src.core.database import async_session_maker
from src.links.models import Link

async def delete_unused_links(days: int = 30):
    threshold = datetime.now() - timedelta(days=days)
    async with async_session_maker() as session:
        query = delete(Link).where(Link.last_accessed < threshold)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount