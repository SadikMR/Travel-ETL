from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Database:
    """Minimal wrapper around SQLAlchemy for cron usage without Flask."""

    def __init__(self, uri: Optional[str] = None) -> None:
        self.uri = uri
        self.engine = None
        self.session_factory = None
        self.session = None

    def initialize(self, uri: Optional[str] = None):
        resolved_uri = uri or self.uri
        if not resolved_uri:
            from config import Config

            resolved_uri = Config.SQLALCHEMY_DATABASE_URI

        if self.engine is None or self.uri != resolved_uri:
            self.uri = resolved_uri
            self.engine = create_engine(resolved_uri)
            self.session_factory = sessionmaker(bind=self.engine)
            self.session = self.session_factory()

        return self

    def create_all(self) -> None:
        self.initialize()
        Base.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        self.initialize()
        Base.metadata.drop_all(self.engine)

    def get_inspector(self):
        from sqlalchemy import inspect

        return inspect(self.engine)


class DBService:
    """Base class for services that need DB access. Provides `self.db`."""

    def __init__(self, db_instance: Optional[Database] = None) -> None:
        self.db = db_instance or db
        self.db.initialize()


db = Database()