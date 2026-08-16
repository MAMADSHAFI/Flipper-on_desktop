# modules/subghz/module.py
from modules.base_module import BaseModule
import random
from datetime import datetime

class SubGHzModule(BaseModule):
    name = "Sub-GHz"
    version = "0.1.0"
    description = "300-928MHz radio transmitter/receiver"
    icon = "📻"

    def __init__(self, kernel):
        super().__init__(kernel)
        self.signals = []
        self.frequencies = [315.0, 433.92, 868.3, 915.0]  # MHz

    def on_load(self):
        self.signals = self.load("signals", [])

    def on_unload(self):
        self.save("signals", self.signals)

    def cmd_scan(self, frequency: float = 433.92) -> dict:
        """Scan for Sub-GHz signals"""
        protocols = ["Princeton", "Came", "Nice", "KeeLoq", "Star Line"]
        return {
            "frequency": frequency,
            "protocol": random.choice(protocols),
            "key": f"{random.randint(0, 0xFFFFFFFF):08X}",
            "timestamp": datetime.now().isoformat()
        }

    def cmd_record(self, name: str, frequency: float = 433.92) -> str:
        """Record a new signal"""
        signal = self.cmd_scan(frequency)
        signal["name"] = name
        self.signals.append(signal)
        self.save("signals", self.signals)
        return f"Signal '{name}' recorded at {frequency}MHz"

    def cmd_replay(self, name: str) -> str:
        """Replay a saved signal"""
        for sig in self.signals:
            if sig["name"] == name:
                return f"Replaying '{name}' ({sig['frequency']}MHz, {sig['protocol']})"
        raise ValueError(f"Signal '{name}' not found")

    def cmd_list(self) -> list:
        """List all saved signals"""
        return self.signals

    def cmd_delete(self, name: str) -> str:
        """Delete a saved signal"""
        self.signals = [s for s in self.signals if s["name"] != name]
        self.save("signals", self.signals)
        return f"Signal '{name}' deleted"
