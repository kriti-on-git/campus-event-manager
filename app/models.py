from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from .database import Base
from sqlalchemy import UniqueConstraint
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import Enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="participant"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )




class Event(Base):
    __tablename__ = "events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text
    )

    venue = Column(
        String,
        nullable=False
    )

    date = Column(
        String,
        nullable=False
    )

    time = Column(
        String,
        nullable=False
    )

    capacity = Column(
        Integer,
        default=100
    )

    category = Column(
        String,
        default="General"
    )

    status = Column(
        String,
        default="Upcoming"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    event_id = Column(
        Integer,
        ForeignKey("events.id")
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_id",
            name="unique_registration"
        ),
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(
        String,
        default="Pending"
    )

    event_id = Column(
        Integer,
        ForeignKey("events.id")
    )

    volunteer_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )