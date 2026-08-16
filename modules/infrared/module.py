# modules/infrared/module.py
from modules.base_module import BaseModule
import random

class InfraredModule(BaseModule):
    name = "Infrared"
    version = "0.1.0"
    description = "IR transmitter/receiver for remotes"
    icon = "🔴"

    def __init__(self, kernel):
        super().__init__(kernel)
        self.remotes = []

    def on_load(self):
        self.remotes = self.load("remotes", [])

    def on_unload(self):
        self.save("remotes", self.remotes)

    def cmd_scan(self) -> dict:
        """Receive an IR signal"""
        protocols = ["NEC", "NECext", "Samsung32", "RC5", "RC6", "SIRC"]
        return {
            "protocol": random.choice(protocols),
            "address": f"{random.randint(0, 0xFFFF):04X}",
            "command": f"{random.randint(0, 0xFF):02X}"
        }

    def cmd_record(self, remote: str, button: str) -> str:
        """Record a button for a remote"""
        signal = self.cmd_scan()
        signal["remote"] = remote
        signal["button"] = button
        self.remotes.append(signal)
        self.save("remotes", self.remotes)
        return f"Button '{button}' recorded for '{remote}'"

    def cmd_send(self, remote: str, button: str) -> str:
        """Send an IR command"""
        for r in self.remotes:
            if r["remote"] == remote and r["button"] == button:
                return f"Sending '{button}' [{r['protocol']} {r['command']}]"
        raise ValueError(f"Button '{button}' for '{remote}' not found")

    def cmd_list(self) -> list:
        """List all saved remotes/buttons"""
        return self.remotes
