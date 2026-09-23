"""Bootstrap script: creates the first Admin user.

Run once, locally, before any login is possible - there is no public
self-registration endpoint by design; Admins create every other account.

Usage:
    python scripts/create_admin.py
"""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gen_m.core.security import get_password_hash
from gen_m.database.session import SessionLocal
from gen_m.models.user import User, UserRole


def main() -> None:
    email = input("Admin email: ").strip()
    full_name = input("Full name: ").strip()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"A user with email {email} already exists.")
            return

        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin user {email} created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
