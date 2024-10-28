from datetime import datetime
from sqlmodel import Field, SQLModel, Column, Integer, DECIMAL
from decimal import Decimal


class Product(SQLModel, table=True, arbitrary_types_allowed=True):
    id: int = Field(sa_column=Column(Integer(), primary_key=True, autoincrement=True))
    web_id: str
    name: str = Field(index=True)
    brand: str
    image_url: str
    description: str
    price: Decimal = Field(sa_column=Column(DECIMAL(100, 2)))
    supermarket: str
    last_updated: datetime
