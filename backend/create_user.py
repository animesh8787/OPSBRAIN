import asyncio
from app.db.postgres.session import AsyncSessionLocal
from app.db.postgres.models import User
from app.core.security import hash_password


async def main():
    email = "demo@example.com"
    password = "changeme123"  # pick whatever you want, then use it to log in

    async with AsyncSessionLocal() as db:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        await db.commit()
        print(f"Created user: {email} / {password}")


if __name__ == "__main__":
    asyncio.run(main())