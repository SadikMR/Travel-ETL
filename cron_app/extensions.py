from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Database:
    """Minimal wrapper around SQLAlchemy for cron usage without Flask."""

    def __init__(self, uri: Optional[str] = None) -> None:
        self.uri = uri
        self.engine = None
        self.session_factory = None

    def initialize(self, uri: Optional[str] = None):
        resolved_uri = uri or self.uri

        if not resolved_uri:
            from config import Config  # pragma: no cover
            resolved_uri = Config.SQLALCHEMY_DATABASE_URI  # pragma: no cover

        if self.engine is None or self.uri != resolved_uri:
            self.uri = resolved_uri
            self.engine = create_engine(resolved_uri)
            self.session_factory = sessionmaker(bind=self.engine)

        return self

    @contextmanager
    def session_scope(self):
        self.initialize()

        session = self.session_factory()

        try:
            yield session
            session.commit()
        except Exception:  # pragma: no cover
            session.rollback()  # pragma: no cover
            raise  # pragma: no cover
        finally:
            session.close()

    def create_all(self) -> None:  # pragma: no cover
        self.initialize()  # pragma: no cover
        Base.metadata.create_all(self.engine)  # pragma: no cover

    def drop_all(self) -> None:  # pragma: no cover
        self.initialize()  # pragma: no cover
        Base.metadata.drop_all(self.engine)  # pragma: no cover

    def get_inspector(self):  # pragma: no cover
        from sqlalchemy import inspect  # pragma: no cover
        return inspect(self.engine)  # pragma: no cover


class DBService:
    """Base class for services that need DB access."""

    def __init__(self, db_instance: Optional[Database] = None):
        self.db = db_instance or db
        self.db.initialize()


db = Database()