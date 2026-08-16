# modules/ibutton/module.py
from modules.base_module import BaseModule
import random

class iButtonModule(BaseModule):
    name = "iButton"
    version = "0.1.0"
    description = "Dallas 1-Wire device reader/emulator"
    icon = "🔑"

    def __init__(self, kernel):
        super().__init__(kernel)
        self.keys = []

    def on_load(self):
        self.keys = self.load("keys", [])

    def on_unload(self):
        self.save("keys", self.keys)

    def cmd_scan(self) -> dict:
        """Simulate reading an iButton key"""
        families = {
            0x01: "DS1990A (ID only)",
            0x33: "DS1961S (SHA-1)",
            0x89: "DS2502 (EEPROM)"
        }
        family = random.choice(list(families.keys()))
        serial = f"{random.randint(0, 0xFFFFFFFFFFFF):012X}"
        return {
            "family": f"{family:02X}",
            "type": families[family],
            "serial": serial
        }

    def cmd_save(self, name: str) -> str:
        """Save scanned key"""
        key_data = self.cmd_scan()
        key_data["name"] = name
        self.keys.append(key_data)
        self.save("keys", self.keys)
        return f"Key '{name}' saved ({key_data['type']})"

    def cmd_emulate(self, name: str) -> str:
        """Emulate a saved key"""
        for key in self.keys:
            if key["name"] == name:
                return f"Emulating '{name}' [{key['family']} {key['serial']}]"
        raise ValueError(f"Key '{name}' not found")

    def cmd_list(self) -> list:
        """List all saved keys"""
        return self.keys

    def cmd_delete(self, name: str) -> str:
        """Delete a saved key"""
        self.keys = [k for k in self.keys if k["name"] != name]
        self.save("keys", self.keys)
        return f"Key '{name}' deleted"
