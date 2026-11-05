"""Pruebas dirigidas por datos: casos_de_prueba.csv + pedidos_prueba.csv.

Los CSV no se cargan solos: se leen aquí con csv.DictReader y se convierten
en pruebas parametrizadas (una por caso CP01..CP12).
"""
import csv
from pathlib import Path

import pytest

from src.domain import CustomerHasDebt, Order

DATA = Path(__file__).resolve().parent.parent / "data"

# CP08: el CSV original describe el comportamiento ANTERIOR al TDD ("CONFIRMED").
# Tras el ciclo RED-GREEN-REFACTOR la expectativa correcta es ValueError.
EXPECTED_AFTER_TDD = {"CP08": "ValueError"}


def _read(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _cases():
    orders = {row["pedido_id"]: row for row in _read("pedidos_prueba.csv")}
    cases = []
    for case in _read("casos_de_prueba.csv"):
        if case["accion"] != "confirmar":
            continue  # CP13-CP15 se cubren en test_service / test_repository
        expected = EXPECTED_AFTER_TDD.get(case["caso_id"], case["resultado_esperado"])
        cases.append(pytest.param(orders[case["pedido_id"]], expected, id=case["caso_id"]))
    return cases


@pytest.mark.parametrize("row, expected", _cases())
def test_confirm_matches_csv_matrix(row, expected):
    order = Order(float(row["total"]), vip=row["es_vip"] == "1", status=row["estado_inicial"])
    debt = float(row["deuda_cliente"])

    if expected in ("ValueError", "CustomerHasDebt"):
        exc = ValueError if expected == "ValueError" else CustomerHasDebt
        with pytest.raises(exc):
            order.confirm(customer_debt=debt)
        return

    charge = float(expected.split("cobro")[1])
    assert order.confirm(customer_debt=debt) == pytest.approx(charge, abs=0.005)
    assert order.status == "CONFIRMED"


def test_csv_matrix_has_expected_size():
    assert len(_read("casos_de_prueba.csv")) == 15
    assert len(_cases()) == 12
