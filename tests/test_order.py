import pytest

from src.domain import CustomerHasDebt, Order


# ---- Pruebas originales del proyecto base -------------------------------
def test_vip_discount():
    o = Order(100, vip=True)  # Arrange
    assert o.confirm() == 85  # Act + Assert
    assert o.status == "CONFIRMED"


def test_regular_no_discount():
    assert Order(200).confirm() == 999


def test_customer_debt():
    with pytest.raises(CustomerHasDebt):
        Order(100).confirm(customer_debt=50)


@pytest.mark.parametrize("total", [0, -1])
def test_invalid_total(total):
    with pytest.raises(ValueError):
        Order(total).confirm()


# ---- E2: pruebas añadidas por el alumno ---------------------------------
def test_vip_discount_200():
    assert Order(200, vip=True).confirm() == 170


def test_regular_customer_200_has_no_discount():
    assert Order(200).confirm() == 200


def test_vip_discount_is_stored_in_order():
    order = Order(200, vip=True)
    order.confirm()
    assert order.discount == 30


def test_minimum_valid_total_is_accepted():
    assert Order(0.01).confirm() == pytest.approx(0.01)


def test_failed_confirmation_keeps_status_new():
    order = Order(100)
    with pytest.raises(CustomerHasDebt):
        order.confirm(customer_debt=1)
    assert order.status == "NEW"


def test_zero_debt_does_not_block_confirmation():
    assert Order(100).confirm(customer_debt=0) == 100


# ---- E3: TDD (RED -> GREEN -> REFACTOR) ---------------------------------
def test_cannot_confirm_twice():
    order = Order(100)
    order.confirm()
    with pytest.raises(ValueError, match="already confirmed"):
        order.confirm()


def test_already_confirmed_order_loaded_as_confirmed_is_rejected():
    with pytest.raises(ValueError, match="already confirmed"):
        Order(250, status="CONFIRMED").confirm()
