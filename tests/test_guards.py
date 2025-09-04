import time

from bot.security.guards import (
    CompositeGuard,
    RateLimitGuard,
    MessageLengthGuard,
    ImageSizeGuard,
    ProfanityGuard,
    CommandSpamGuard,
)


def test_message_length_guard_ok():
    guard = MessageLengthGuard(max_chars=10)
    assert guard.check({"text": "hola"}) is None


def test_message_length_guard_block():
    guard = MessageLengthGuard(max_chars=5)
    assert guard.check({"text": "123456"}) is not None


def test_image_size_guard_block():
    guard = ImageSizeGuard(max_bytes=10)
    assert guard.check({"image_size_bytes": 11}) is not None


def test_profanity_guard():
    guard = ProfanityGuard(banned_substrings=("mierda",))
    assert guard.check({"text": "qué mierda"}) is not None
    assert guard.check({"text": "qué lindo"}) is None


def test_command_spam_guard():
    guard = CommandSpamGuard(cooldown_seconds=1)
    user = 1
    # Primero pasa
    assert guard.check({"user_id": user, "is_command": True}) is None
    # Segundo bloquea por cooldown
    assert guard.check({"user_id": user, "is_command": True}) is not None
    time.sleep(1.1)
    # Luego de esperar, pasa
    assert guard.check({"user_id": user, "is_command": True}) is None


def test_rate_limit_guard():
    guard = RateLimitGuard(max_requests=2, window_seconds=1)
    user = 9
    assert guard.check({"user_id": user, "text": "a"}) is None
    assert guard.check({"user_id": user, "text": "b"}) is None
    assert guard.check({"user_id": user, "text": "c"}) is not None
    time.sleep(1.1)
    assert guard.check({"user_id": user, "text": "d"}) is None


def test_composite_guard_first_violation():
    cg = CompositeGuard(MessageLengthGuard(max_chars=3), ImageSizeGuard(max_bytes=10))
    msg = cg.check({"text": "demasiado largo"})
    assert msg is not None
