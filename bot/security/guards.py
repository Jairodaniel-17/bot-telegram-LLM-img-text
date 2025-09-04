import time
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any


class Guard(Protocol):
    def check(self, context: Dict[str, Any]) -> Optional[str]: ...


class CompositeGuard:
    def __init__(self, *guards: Guard) -> None:
        self._guards = list(guards)

    def add(self, guard: Guard) -> None:
        self._guards.append(guard)

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        for guard in self._guards:
            message = guard.check(context)
            if message:
                return message
        return None


@dataclass
class RateLimitGuard:
    max_requests: int = 5
    window_seconds: int = 10

    def __post_init__(self) -> None:
        self._buckets: Dict[int, list[float]] = {}

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        user_id = int(context.get("user_id", 0))
        now = time.time()
        bucket = self._buckets.setdefault(user_id, [])
        # purge old
        cutoff = now - self.window_seconds
        bucket[:] = [t for t in bucket if t >= cutoff]
        if len(bucket) >= self.max_requests:
            return "⏳ Estás enviando mensajes muy rápido. Inténtalo de nuevo en unos segundos."
        bucket.append(now)
        return None


@dataclass
class MessageLengthGuard:
    max_chars: int = 4000

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        text: str = context.get("text") or ""
        if len(text) > self.max_chars:
            return f"📏 Tu mensaje es muy largo (>{self.max_chars} caracteres). Reduce el tamaño."
        return None


@dataclass
class ImageSizeGuard:
    max_bytes: int = 5 * 1024 * 1024  # 5 MB

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        image_size = context.get("image_size_bytes")
        if image_size is not None and image_size > self.max_bytes:
            return "🖼️ La imagen es demasiado grande. Máximo permitido: 5 MB."
        return None


@dataclass
class ProfanityGuard:
    banned_substrings: tuple[str, ...] = (
        "fuck",
        "shit",
        "bitch",
        "pendejo",
        "mierda",
    )

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        text: str = (context.get("text") or "").lower()
        if any(word in text for word in self.banned_substrings):
            return "🚫 Por favor evita lenguaje ofensivo."
        return None


@dataclass
class CommandSpamGuard:
    cooldown_seconds: int = 2

    def __post_init__(self) -> None:
        self._last_command_time: Dict[int, float] = {}

    def check(self, context: Dict[str, Any]) -> Optional[str]:
        if not context.get("is_command"):
            return None
        user_id = int(context.get("user_id", 0))
        now = time.time()
        last = self._last_command_time.get(user_id, 0.0)
        if now - last < self.cooldown_seconds:
            return "🛑 No envíes comandos tan seguido. Espera un momento."
        self._last_command_time[user_id] = now
        return None
