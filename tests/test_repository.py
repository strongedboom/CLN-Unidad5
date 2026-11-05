import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_repository_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120


def test_repository_rollback():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None


# ---- E4: prueba del alumno (id=2, total 250) -----------------------------
def test_repository_saves_order_250_with_id_2():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))
        session.commit()
        row = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert (row.id, row.total, row.status) == (2, 250, "NEW")


def test_committed_data_is_visible_from_another_session():
    engine = make_engine()
    with Session(engine) as s1:
        SqlOrderRepository(s1).save(3, Order(80))
        s1.commit()
    with Session(engine) as s2:
        assert s2.get(OrderRow, 3).total == 80


def test_uncommitted_data_is_lost_when_session_closes():
    engine = make_engine()
    with Session(engine) as s1:
        SqlOrderRepository(s1).save(4, Order(80))
    with Session(engine) as s2:
        assert s2.get(OrderRow, 4) is None


def test_duplicate_primary_key_is_rejected_and_rolled_back():
    engine = make_engine()
    with Session(engine) as s1:
        SqlOrderRepository(s1).save(5, Order(10))
        s1.commit()
    with Session(engine) as s2:
        SqlOrderRepository(s2).save(5, Order(99))
        with pytest.raises(IntegrityError):
            s2.commit()
        s2.rollback()
    with Session(engine) as s3:
        assert s3.get(OrderRow, 5).total == 10
