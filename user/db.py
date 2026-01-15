from sqlalchemy import create_engine, Integer, String, Numeric, UUID, Text

from sqlalchemy.orm import declarative_base, mapped_column, sessionmaker, Mapped
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# from utils import DB_URL

import uuid as uid
import os

DB_URL = f'postgresql+asyncpg://{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}'

engine = create_async_engine(DB_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
class Client(Base):
	__tablename__ = "clients"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	uuid: Mapped[uid.UUID] = mapped_column(
		UUID(as_uuid=True),
		unique=True,
		nullable=False,
		# default=uid.uuid4
	)
	username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password: Mapped[str] = mapped_column(String(100), nullable=False)
	role: Mapped[str] = mapped_column(String(30), nullable=False, default="user")
	balance: Mapped[float] = mapped_column(
		Numeric(9, 2),
		nullable=False,
		default=0
	)
	country: Mapped[str] = mapped_column(Text)
	discount: Mapped[float] = mapped_column(
		Numeric(5, 2),
		nullable=False,
		default=0
	)

