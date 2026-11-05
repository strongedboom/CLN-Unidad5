from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from src.inventory import InventoryItem
from src.repository import Base


class InventoryRow(Base):
    __tablename__ = "inventory"
    sku = Column(String, primary_key=True)
    stock = Column(Integer, nullable=False)


class SqlInventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, item: InventoryItem):
        self.session.add(InventoryRow(sku=item.sku, stock=item.stock))

    def get(self, sku):
        row = self.session.get(InventoryRow, sku)
        return None if row is None else InventoryItem(row.sku, row.stock)
