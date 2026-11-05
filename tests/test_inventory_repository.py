"""Persistencia del inventario (PIA): commit y rollback sobre SQLite en memoria."""
from sqlalchemy.orm import Session

from src.inventory import InventoryItem
from src.inventory_repository import SqlInventoryRepository
from src.repository import make_engine


def test_inventory_persists_after_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlInventoryRepository(session).save(InventoryItem("SKU-1", 42))
        session.commit()
    with Session(engine) as session:
        item = SqlInventoryRepository(session).get("SKU-1")
        assert (item.sku, item.stock) == ("SKU-1", 42)


def test_inventory_rollback_discards_item():
    engine = make_engine()
    with Session(engine) as session:
        repo = SqlInventoryRepository(session)
        repo.save(InventoryItem("SKU-2", 5))
        session.rollback()
        assert repo.get("SKU-2") is None
