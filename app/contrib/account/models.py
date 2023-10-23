import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.db.models import Base


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(sa.String(254), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(254), nullable=False)
