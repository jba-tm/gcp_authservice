from typing import Generic, Optional, TypeVar
from pydantic import BaseModel as PydanticBaseModel, ConfigDict

DataType = TypeVar("DataType")


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class IResponseBase(PydanticBaseModel, Generic[DataType]):
    message: Optional[str] = None
    data: DataType

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class VisibleBase(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
