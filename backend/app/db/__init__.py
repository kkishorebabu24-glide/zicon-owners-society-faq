# Database and models package

from sqlalchemy import create_engine  # type: ignore[import]
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore[import]

Base = declarative_base()

# TODO: Create database engine
# TODO: Define models (User, TelegramGroup, Message, Digest, Offer, Request, etc.)
