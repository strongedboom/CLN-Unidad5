"""E9: adaptación a reglas del PIA (ejemplo de inventario, 3 reglas x 3 casos)."""
from unittest.mock import Mock

import pytest

from src.inventory import (
    CapacityExceeded,
    InvalidQuantity,
    InventoryItem,
    InventoryService,
    OutOfStock,
)


# --- R1: no vender sin inventario suficiente --------------------------------
def test_cp_pia_01_reserve_with_stock_succeeds():
    assert InventoryItem("A", 10).reserve(3) == 7


def test_cp_pia_02_reserve_more_than_stock_is_rejected():
    item = InventoryItem("A", 2)
    with pytest.raises(OutOfStock):
        item.reserve(3)
    assert item.stock == 2


def test_cp_pia_03_reserve_exact_stock_leaves_zero():
    assert InventoryItem("A", 3).reserve(3) == 0


# --- R2: la cantidad debe ser un entero positivo ----------------------------
def test_cp_pia_04_valid_quantity_one():
    assert InventoryItem("A", 5).reserve(1) == 4


@pytest.mark.parametrize("quantity", [-1, 0, 1.5, "2", True, None])
def test_cp_pia_05_06_invalid_quantities_are_rejected(quantity):
    with pytest.raises(InvalidQuantity):
        InventoryItem("A", 5).reserve(quantity)


# --- R3: reabastecer sin exceder capacidad ----------------------------------
def test_cp_pia_07_restock_adds_units():
    assert InventoryItem("A", 10).restock(5) == 15


def test_cp_pia_08_restock_negative_is_rejected():
    with pytest.raises(InvalidQuantity):
        InventoryItem("A", 10).restock(-3)


def test_cp_pia_09_restock_up_to_capacity_is_allowed():
    assert InventoryItem("A", 990).restock(10) == 1000


def test_restock_over_capacity_is_rejected_and_stock_unchanged():
    item = InventoryItem("A", 990)
    with pytest.raises(CapacityExceeded):
        item.restock(11)
    assert item.stock == 990


# --- R4: servicio externo del proveedor (mock) ------------------------------
def test_supplier_is_asked_to_restock_when_stock_falls_below_minimum():
    supplier = Mock()
    remaining = InventoryService(supplier).reserve(InventoryItem("A", 8), 5)
    assert remaining == 3
    supplier.request_restock.assert_called_once_with("A", 7)


def test_supplier_not_called_when_stock_stays_at_minimum_or_more():
    supplier = Mock()
    InventoryService(supplier).reserve(InventoryItem("A", 10), 5)
    supplier.request_restock.assert_not_called()


def test_supplier_timeout_is_propagated():
    supplier = Mock()
    supplier.request_restock.side_effect = TimeoutError("supplier timeout")
    with pytest.raises(TimeoutError):
        InventoryService(supplier).reserve(InventoryItem("A", 6), 5)


def test_supplier_not_called_when_reservation_fails():
    supplier = Mock()
    with pytest.raises(OutOfStock):
        InventoryService(supplier).reserve(InventoryItem("A", 1), 5)
    supplier.request_restock.assert_not_called()
