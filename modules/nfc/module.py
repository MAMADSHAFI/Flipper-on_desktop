# modules/nfc/module.py
from modules.base_module import BaseModule
import random

class NFCModule(BaseModule):
    name = "NFC"
    version = "0.1.0"
    description = "13.56MHz NFC reader/writer"
    icon = "💳"

    def __init__(self, kernel):
        super().__init__(kernel)
        self.cards = []

    def on_load(self):
        self.cards = self.load("cards", [])

    def on_unload(self):
        self.save("cards", self.cards)

    def cmd_scan(self) -> dict:
        """Scan for NFC card"""
        card_types = ["MIFARE Classic 1K", "MIFARE Ultralight", "NTAG215", "ISO14443A"]
        uid = f"{random.randint(0, 0xFFFFFFFF):08X}"
        return {
            "type": random.choice(card_types),
            "uid": uid,
            "atqa": f"{random.randint(0, 0xFFFF):04X}",
            "sak": f"{random.randint(0, 0xFF):02X}"
        }

    def cmd_save(self, name: str) -> str:
        """Save scanned card"""
        card = self.cmd_scan()
        card["name"] = name
        self.cards.append(card)
        self.save("cards", self.cards)
        return f"Card '{name}' saved (UID: {card['uid']})"

    def cmd_emulate(self, name: str) -> str:
        """Emulate a saved card"""# modules/nfc/module.py (ادامه)
    def cmd_emulate(self, name: str) -> str:
        """Emulate a saved card"""
        for card in self.cards:
            if card["name"] == name:
                return f"Emulating '{name}' (UID: {card['uid']}, {card['type']})"
        raise ValueError(f"Card '{name}' not found")

    def cmd_list(self) -> list:
        """List all saved cards"""
        return self.cards

    def cmd_delete(self, name: str) -> str:
        """Delete a saved card"""
        self.cards = [c for c in self.cards if c["name"] != name]
        self.save("cards", self.cards)
        return f"Card '{name}' deleted"


