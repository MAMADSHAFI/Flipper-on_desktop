from core.state_manager import StateManager
from core.plugin_loader import PluginLoader


class Kernel:
    """هسته سیستم — مدیریت ماژول‌ها و حافظه."""

    def __init__(self):
        self.state_manager = StateManager()
        self.modules: dict[str, "BaseModule"] = {}
        self._loader = PluginLoader(self)

    def boot(self) -> None:
        print("[*] در حال بوت FlipperWin...")
        for module in self._loader.discover():
            module.on_load()
            self.modules[module.name] = module
            print(f"    ✓ ماژول بارگذاری شد: {module.icon} {module.name}")
        print(f"[*] {len(self.modules)} ماژول فعال است.")

    def run_command(self, module_name: str, command: str, **kwargs):
        module = self.modules.get(module_name)
        if not module:
            raise ValueError(f"ماژول '{module_name}' یافت نشد.")
        return module.execute(command, **kwargs)

    def shutdown(self) -> None:
        for module in self.modules.values():
            module.on_unload()
        self.state_manager.close()
        print("[*] خاموش شد.")
