from sqlmodel import create_engine, Session, SQLModel

from config import settings


# echo=True logs all SQL statements (disabled in prod)
engine = create_engine(settings.database_url, echo=settings.app_env != "prod")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def seed_admin_user():
    if not settings.admin_email:
        return

    from auth.service import get_password_hash, get_user
    from db.models import User

    with Session(engine) as session:
        user = get_user(session, email=settings.admin_email)
        if user:
            user.hashed_password = get_password_hash(settings.admin_password)
            user.is_admin = True
        else:
            user = User(
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                is_admin=True,
            )
        session.add(user)
        session.commit()
        print(f"Admin user ready: {settings.admin_email}")
