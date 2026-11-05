from unittest.mock import Mock, patch

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)


def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))


# ---- E5: pruebas del alumno -------------------------------------------------
def test_vip_payment_rejected_charges_170_and_raises():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(Order(200, vip=True))
    gateway.charge.assert_called_once_with(170)


def test_vip_payment_approved_returns_170():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(200, vip=True)) == 170


def test_gateway_timeout_is_propagated():
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    with pytest.raises(TimeoutError):
        OrderService(gateway).checkout(Order(100))
    gateway.charge.assert_called_once_with(100)


def test_gateway_is_not_called_when_order_is_invalid():
    gateway = Mock()
    with pytest.raises(ValueError):
        OrderService(gateway).checkout(Order(0))
    gateway.charge.assert_not_called()


def test_mock_gateway_never_opens_a_network_connection():
    gateway = Mock()
    gateway.charge.return_value = True
    with patch("socket.socket", side_effect=AssertionError("network used!")):
        assert OrderService(gateway).checkout(Order(100)) == 100


@pytest.mark.xfail(
    strict=True,
    reason="RIESGO CONOCIDO: el pedido se confirma antes de saber si el pago fue aceptado",
)
def test_order_should_not_stay_confirmed_when_payment_is_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(100)
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)
    assert order.status != "CONFIRMED"
