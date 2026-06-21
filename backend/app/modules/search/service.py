import uuid
from typing import List, Sequence, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete
from .models import SearchDocument


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_index(
        self,
        company_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        title: str,
        subtitle: str,
        search_terms: List[str],
        url: str
    ):
        # Delete existing if any
        stmt = delete(SearchDocument).where(and_(
            SearchDocument.entity_type == entity_type,
            SearchDocument.entity_id == entity_id
        ))
        await self.db.execute(stmt)

        # Create new
        doc = SearchDocument(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            subtitle=subtitle,
            search_text=" ".join(filter(None, search_terms)).lower(),
            url=url
        )
        self.db.add(doc)
        await self.db.flush()

    async def search(self, company_id: uuid.UUID, query: str, limit: int = 10) -> Sequence[SearchDocument]:
        if not query:
            return []

        search_term = f"%{query.lower()}%"
        stmt = (
            select(SearchDocument)
            .where(and_(
                SearchDocument.company_id == company_id,
                or_(
                    SearchDocument.title.ilike(search_term),
                    SearchDocument.search_text.ilike(search_term)
                )
            ))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def delete_entity(self, entity_type: str, entity_id: uuid.UUID):
        stmt = delete(SearchDocument).where(and_(
            SearchDocument.entity_type == entity_type,
            SearchDocument.entity_id == entity_id
        ))
        await self.db.execute(stmt)
