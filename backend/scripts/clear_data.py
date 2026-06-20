import asyncio
from sqlalchemy import text
from app.shared.database.session import engine

async def clear_data():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE companies CASCADE;"))
        print("Data cleared.")

if __name__ == "__main__":
    asyncio.run(clear_data())
