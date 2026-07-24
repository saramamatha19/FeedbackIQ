import datetime
import uuid

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

'''"This file defines reusable base classes for all database models. 
Base tells SQLAlchemy which classes are database tables. 
UUIDPrimaryKeyMixin automatically adds a UUID primary key called id to every table,
 and TimestampMixin automatically adds a created_at timestamp. Using mixins 
 avoids repeating the same id and created_at code in every model, 
making the code cleaner and easier to maintain."'''