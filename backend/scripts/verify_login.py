import asyncio
from sqlalchemy import select
from app.shared.database.session import AsyncSessionLocal
from app.modules.auth.models import User
from app.core.security import verify_password

async def verify():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == 'demo@smarterp.io'))
        user = res.scalar_one_or_none()
        if not user:
            print("USER NOT FOUND")
            return

        match = verify_password("Password123", user.hashed_password)
        print(f"PASSWORD_MATCH={match}")

if __name__ == "__main__":
    asyncio.run(verify())
