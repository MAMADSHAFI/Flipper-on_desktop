import importlib
import pkgutil
import inspect
from pathlib import Path
from modules.base_module import BaseModule


class PluginLoader:
    """کشف و بارگذاری خودکار ماژول‌ها از پوشه modules/."""

    def __init__(self, kernel, modules_path: str = None):
        """
        سازنده PluginLoader.
        Args:
            kernel: نمونه هسته (Kernel) برای تزریق به ماژول‌ها.
            modules_path: مسیری که ماژول‌ها در آن قرار دارند.
                         اگر None باشد، به صورت خودکار نسبت به محل این فایل محاسبه می‌شود.
        """
        self.kernel = kernel
        
        # ✅ محاسبه خودکار مسیر ماژول‌ها نسبت به محل فایل plugin_loader.py
        if modules_path is None:
            # مسیر ریشه پروژه (یک پوشه بالاتر از core/)
            project_root = Path(__file__).resolve().parent.parent
            modules_path = str(project_root / "modules")
        
        self.modules_path = modules_path

    def discover(self) -> list[BaseModule]:
        """
        ماژول‌ها را در مسیر مشخص شده کشف و بارگذاری می‌کند.
        فقط پکیج‌هایی را که شامل یک فایل `module.py` هستند و کلاسی را
        پیاده‌سازی می‌کنند که از `BaseModule` ارث‌بری کرده باشد، بارگذاری می‌کند.
        """
        loaded = []
        base = Path(self.modules_path)  # ایجاد شیء Path از مسیر ماژول‌ها

        # تکرار بر روی ساب‌ماژول‌ها/ساب‌پکیج‌ها در مسیر base
        for finder, name, ispkg in pkgutil.iter_modules([str(base)]):
            if not ispkg:
                # فقط پکیج‌ها (دایرکتوری‌هایی که شامل __init__.py هستند) را پردازش می‌کنیم.
                continue
            try:
                # تلاش برای وارد کردن فایل module.py درون هر پکیج
                # مثال: برای پوشه modules/rfid/، ماژول modules.rfid.module وارد می‌شود.
                mod = importlib.import_module(
                    f"modules.{name}.module"  # ✅ از "modules" ثابت استفاده شده
                )
                # بررسی اعضای ماژول وارد شده برای یافتن کلاس‌ها
                for _, obj in inspect.getmembers(mod, inspect.isclass):
                    # اگر کلاس از BaseModule ارث‌بری کرده باشد و خود BaseModule نباشد
                    if issubclass(obj, BaseModule) and obj is not BaseModule:
                        # یک نمونه از کلاس ماژول ایجاد می‌کنیم و هسته را به آن تزریق می‌کنیم.
                        instance = obj(self.kernel)
                        loaded.append(instance)
            except Exception as e:
                print(f"[!] خطا در بارگذاری ماژول {name}: {e}")

        return loaded
