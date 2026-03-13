import sys
sys.path.insert(0, ".")

from db.database import create_db_and_tables, engine
from db.models import User
from auth.service import get_password_hash
from sqlmodel import Session

create_db_and_tables()

with Session(engine) as session:
    user = User(
        email="test@test.com",
        hashed_password=get_password_hash("abc"),
        name="Test User",
    )
    session.add(user)
    session.commit()
    print(f"Created user: {user.email}")
