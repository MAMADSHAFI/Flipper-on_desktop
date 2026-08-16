from abc import ABC, abstractmethod
from typing import Any


class BaseModule(ABC):
    """کلاس پایه برای همه ماژول‌ها (پلاگین‌ها)."""

    name: str = "Unnamed"
    version: str = "0.1.0"
    description: str = ""
    icon: str = "📦"

    def __init__(self, kernel):
        self.kernel = kernel
        self.state = kernel.state_manager
        self._enabled = False

    @abstractmethod
    def on_load(self) -> None:
        """هنگام بارگذاری ماژول اجرا میشه."""
        ...

    @abstractmethod
    def on_unload(self) -> None:
        """هنگام خاموش‌شدن ماژول اجرا میشه."""
        ...

    def execute(self, command: str, **kwargs) -> Any:
        """اجرای یک دستور روی این ماژول."""
        handler = getattr(self, f"cmd_{command}", None)
        if handler is None:
            raise ValueError(f"دستور '{command}' در ماژول {self.name} یافت نشد.")
        return handler(**kwargs)

    # --- کمک‌کننده‌ها برای حافظه ---
    def save(self, key: str, value: Any) -> None:
        self.state.set(f"{self.name}.{key}", value)

    def load(self, key: str, default: Any = None) -> Any:
        return self.state.get(f"{self.name}.{key}", default)
