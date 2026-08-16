from modules.base_module import BaseModule
import random


class RFIDModule(BaseModule):
    name = "RFID"
    version = "0.1.0"
    description = "خواندن/ذخیره کارت‌های RFID (شبیه‌سازی‌شده)"
    icon = "📡"

    def on_load(self) -> None:
        # لیست کارت‌های ذخیره‌شده رو از حافظه بازیابی می‌کنیم
        self.cards = self.load("saved_cards", [])

    def on_unload(self) -> None:
        self.save("saved_cards", self.cards)

    # --- دستورات ---
    def cmd_scan(self) -> str:
        """شبیه‌سازی اسکن یک کارت."""
        card_id = ":".join(f"{random.randint(0,255):02X}" for _ in range(4))
        return card_id

    def cmd_save(self, card_id: str) -> None:
        self.cards.append(card_id)
        self.save("saved_cards", self.cards)

    def cmd_list(self) -> list:
        return self.cards
