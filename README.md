# Unidad 5 CLN · Integración, pruebas y calidad

Proyecto de pedidos con pruebas unitarias, de integración (SQLAlchemy + SQLite en memoria),
mocks de pasarela de pago/proveedor, pruebas de autorización, cobertura >= 80 % y CI en GitHub Actions.

## Instalación y ejecución

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ruff check src tests
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

macOS / Linux: `python3 -m venv .venv && source .venv/bin/activate` y los mismos comandos `python -m ...`.
El reporte HTML queda en `htmlcov/index.html`.

## Arquitectura

| Archivo | Responsabilidad |
| --- | --- |
| `src/domain.py` | Reglas del pedido (descuento VIP 15 %, deuda, total positivo, no confirmar dos veces) |
| `src/application.py` | `OrderService.checkout`: confirma y cobra mediante un puerto `gateway` |
| `src/repository.py` | Persistencia SQLAlchemy de pedidos (commit/rollback) |
| `src/security.py` | Política de cancelación (enviado nunca; admin siempre; dueño < 24 h) |
| `src/inventory.py`, `src/inventory_repository.py` | Adaptación PIA (ejemplo): reglas de inventario + proveedor externo |
| `tests/` | Pruebas unitarias, de integración, con mocks, de seguridad y dirigidas por CSV |
| `data/` | CSV didácticos (pedidos, clientes, casos) y base SQLite demostrativa |
| `docs/` | Matrices de resultados (CSV): casos, autorización y PIA |

Las pruebas de repositorio usan SQLite **en memoria**; los CSV/SQLite de `data/` no se importan a la base de las pruebas.
`tests/test_casos_csv.py` los lee con `csv.DictReader`.

## Decisiones y riesgos documentados

* **TDD (CP08):** `test_cannot_confirm_twice` se escribió primero (RED) y falló; se añadió la guarda en `Order.confirm` (GREEN) y las precondiciones se movieron a `_ensure_can_confirm` (REFACTOR).
* **Riesgo conocido:** `checkout` confirma el pedido antes de saber si el pago fue aceptado. Está documentado con una prueba `xfail(strict=True)`; al corregirlo, esa prueba obligará a retirar la marca.
* **Cancelación:** un pedido `SHIPPED` nunca se cancela, ni siquiera por administrador.
* **Protección de rama:** el YAML ejecuta las verificaciones; bloquear el merge requiere activar branch protection / rulesets en GitHub.
