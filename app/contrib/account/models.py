import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.db.models import Base


class User(Base):
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
