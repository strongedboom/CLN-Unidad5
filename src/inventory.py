"""Adaptación PIA (ejemplo): reglas de inventario.

R1  No se vende sin inventario suficiente.
R2  La cantidad debe ser un entero positivo.
R3  Reabastecer suma stock sin exceder la capacidad del almacén (1000).
R4  Si tras reservar el stock queda por debajo del mínimo se pide reposición
    al proveedor (servicio externo -> se prueba con mock).
"""
from dataclasses import dataclass

MAX_CAPACITY = 1000
MIN_STOCK = 5


class InvalidQuantity(ValueError):
    pass


class OutOfStock(Exception):
    pass


class CapacityExceeded(Exception):
    pass


def _check_quantity(quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise InvalidQuantity("quantity must be a positive integer")


@dataclass
class InventoryItem:
    sku: str
    stock: int = 0

    def reserve(self, quantity):
        _check_quantity(quantity)
        if quantity > self.stock:
            raise OutOfStock(f"only {self.stock} units available")
        self.stock -= quantity
        return self.stock

    def restock(self, quantity):
        _check_quantity(quantity)
        if self.stock + quantity > MAX_CAPACITY:
            raise CapacityExceeded("warehouse capacity exceeded")
        self.stock += quantity
        return self.stock


class InventoryService:
    """Reserva stock y, si queda bajo el mínimo, solicita reposición."""

    def __init__(self, supplier):
        self.supplier = supplier

    def reserve(self, item, quantity):
        remaining = item.reserve(quantity)
        if remaining < MIN_STOCK:
            self.supplier.request_restock(item.sku, MIN_STOCK * 2 - remaining)
        return remaining
