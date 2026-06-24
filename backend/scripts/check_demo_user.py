import asyncio
from sqlalchemy import select
from app.shared.database.session import AsyncSessionLocal
from app.modules.auth.models import User

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == 'demo@smarterp.io'))
        user = res.scalar_one_or_none()
        print(f"USER_EXISTS={user is not None}")
        if user:
            print(f"USER_ID={user.id}")
            print(f"USER_ACTIVE={user.is_active}")

if __name__ == "__main__":
    asyncio.run(check())
