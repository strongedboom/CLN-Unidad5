from datetime import UTC, datetime, timedelta

from src.security import can_cancel

NOW = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)  # fecha fija


def test_owner_within_24h():
    assert can_cancel("NEW", 1, 1, False, NOW - timedelta(hours=1), NOW)


def test_stranger_denied():
    assert not can_cancel("NEW", 1, 2, False, NOW, NOW)


def test_shipped_denied_even_admin():
    assert not can_cancel("SHIPPED", 1, 1, True, NOW, NOW)


def test_expired_denied():
    assert not can_cancel("NEW", 1, 1, False, NOW - timedelta(hours=25), NOW)


# ---- E6: pruebas del alumno -------------------------------------------------
def test_admin_can_cancel_new_order_of_another_user():
    assert can_cancel("NEW", 1, 99, True, NOW - timedelta(days=10), NOW)


def test_owner_denied_at_exactly_24_hours():
    assert not can_cancel("NEW", 1, 1, False, NOW - timedelta(hours=24), NOW)


def test_owner_allowed_one_minute_before_24_hours():
    created = NOW - timedelta(hours=23, minutes=59)
    assert can_cancel("NEW", 1, 1, False, created, NOW)


def test_owner_cannot_cancel_shipped_order():
    assert not can_cancel("SHIPPED", 1, 1, False, NOW, NOW)


def test_admin_can_cancel_confirmed_order():
    assert can_cancel("CONFIRMED", 1, 99, True, NOW, NOW)


def test_default_now_uses_current_utc_time():
    created = datetime.now(UTC) - timedelta(minutes=5)
    assert can_cancel("NEW", 1, 1, False, created)
