import re

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column

metadata = sa.MetaData()


class UnMapped:
    __allow_unmapped__ = True


PlainBase = declarative_base(metadata=metadata, cls=UnMapped)


class Base(PlainBase):
    __name__: str
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', cls.__name__).lower()
