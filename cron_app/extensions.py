from flask_sqlalchemy import SQLAlchemy
from typing import Optional


class Database(SQLAlchemy):
	"""Thin wrapper around SQLAlchemy to allow future extensions and helpers."""

	def get_inspector(self):
		return self.inspect(self.engine)


class DBService:
	"""Base class for services that need DB access. Provides `self.db`."""

	def __init__(self, db_instance: Optional[Database] = None) -> None:
		self.db = db_instance or db


db = Database()