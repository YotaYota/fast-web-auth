from sqlmodel import create_engine, Session, SQLModel

from config import settings


# echo=True logs all SQL statements (disabled in prod)
engine = create_engine(settings.database_url, echo=settings.app_env != "prod")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
