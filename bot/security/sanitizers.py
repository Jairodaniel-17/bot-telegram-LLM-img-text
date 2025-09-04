import re
from typing import Protocol


class Sanitizer(Protocol):
    def sanitize(self, text: str) -> str: ...


class CompositeSanitizer:
    def __init__(self, *sanitizers: Sanitizer) -> None:
        self._sanitizers = list(sanitizers)

    def add(self, sanitizer: Sanitizer) -> None:
        self._sanitizers.append(sanitizer)

    def sanitize(self, text: str) -> str:
        result = text
        for sanitizer in self._sanitizers:
            result = sanitizer.sanitize(result)
        return result


class MarkdownEscapeSanitizer:
    _escape_chars = r"_*[]()~`>#+-=|{}.!"

    def sanitize(self, text: str) -> str:
        return re.sub(f"([{re.escape(self._escape_chars)}])", r"\\\\\1", text)


class TrimSanitizer:
    def sanitize(self, text: str) -> str:
        return text.strip()


class ControlCharsSanitizer:
    _control = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

    def sanitize(self, text: str) -> str:
        return self._control.sub("", text)
