"""Create a user from the command line (the only way to create agents).

    python -m app.create_user --email agent@example.com --password 'secret123' --role agent
"""
import argparse
import asyncio

from app.db.database import SessionLocal, engine
from app.repositories.user_repository import UserRepository
from app.schema.user import Role
from app.services.auth_service import AuthService

async def main(email: str, password: str, role: Role) -> None:
    async with SessionLocal() as db:
        user = await AuthService(UserRepository(db)).register(email, password, role)
        await db.commit()
    await engine.dispose()
    print(f"Created {user.role} {user.email} ({user.id})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", choices=[r.value for r in Role], default=Role.CUSTOMER.value)
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password, Role(args.role)))
