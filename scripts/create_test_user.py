from db.database import create_db_and_tables, engine
from db.models import User
from auth.service import get_password_hash, get_user
from sqlmodel import Session

create_db_and_tables()

with Session(engine) as session:
    if get_user(session, email="a@b.com"):
        print("User already exists: a@b.com")
    else:
        user = User(
            email="a@b.com",
            hashed_password=get_password_hash("secret"),
            name="Test User",
        )
        session.add(user)
        session.commit()
        print(f"Created test user: {user.email}:secret")
