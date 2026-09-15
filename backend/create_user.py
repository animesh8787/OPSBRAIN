import asyncio

from firebase_admin import auth as firebase_auth

from app.core.firebase import _ensure_app
from app.db.postgres.session import AsyncSessionLocal
from app.db.postgres.models import User


async def main():
    email = "demo@example.com"
    password = "changeme123"  # pick whatever you want, then use it to log in

    _ensure_app()
    firebase_user = firebase_auth.create_user(email=email, password=password)

    async with AsyncSessionLocal() as db:
        user = User(email=email, firebase_uid=firebase_user.uid)
        db.add(user)
        await db.commit()
        print(f"Created user: {email} / {password}")


if __name__ == "__main__":
    asyncio.run(main())
