# modules/gpio/module.py
from modules.base_module import BaseModule

class GPIOModule(BaseModule):
    name = "GPIO"
    version = "0.1.0"
    description = "General Purpose I/O control"
    icon = "⚡"

    def __init__(self, kernel):
        super().__init__(kernel)
        # Flipper Zero has 7 GPIO pins (PC0-PC3, PB2-PB3, PA7)
        self.pins = {
            "PC0": {"mode": "input", "state": False},
            "PC1": {"mode": "input", "state": False},
            "PC2": {"mode": "input", "state": False},
            "PC3": {"mode": "input", "state": False},
            "PB2": {"mode": "input", "state": False},
            "PB3": {"mode": "input", "state": False},
            "PA7": {"mode": "input", "state": False},
        }

    def on_load(self):
        saved_pins = self.load("pins", None)
        if saved_pins:
            self.pins.update(saved_pins)

    def on_unload(self):
        self.save("pins", self.pins)

    def cmd_set_mode(self, pin: str, mode: str) -> str:
        """Set pin mode (input/output)"""
        if pin not in self.pins:
            raise ValueError(f"Invalid pin: {pin}")
        if mode not in ["input", "output"]:
            raise ValueError(f"Invalid mode: {mode}")
        self.pins[pin]["mode"] = mode
        return f"Pin {pin} set to {mode} mode"

    def cmd_write(self, pin: str, state: bool) -> str:
        """Write digital value to pin"""
        if pin not in self.pins:
            raise ValueError(f"Invalid pin: {pin}")
        if self.pins[pin]["mode"] != "output":
            raise ValueError(f"Pin {pin} is not in output mode")
        self.pins[pin]["state"] = state
        return f"Pin {pin} set to {'HIGH' if state else 'LOW'}"

    def cmd_read(self, pin: str) -> dict:
        """Read digital value from pin"""
        if pin not in self.pins:
            raise ValueError(f"Invalid pin: {pin}")
        return {
            "pin": pin,
            "mode": self.pins[pin]["mode"],
            "state": self.pins[pin]["state"]
        }

    def cmd_status(self) -> dict:
        """Get status of all pins"""
        return self.pins
