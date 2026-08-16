# modules/u2f/module.py
from modules.base_module import BaseModule
import random
import hashlib

class U2FModule(BaseModule):
    name = "U2F"
    version = "0.1.0"
    description = "FIDO U2F security key emulation"
    icon = "🔐"

    def __init__(self, kernel):
        super().__init__(kernel)
        self.registered_sites = []

    def on_load(self):
        self.registered_sites = self.load("sites", [])

    def on_unload(self):
        self.save("sites", self.registered_sites)

    def cmd_register(self, site: str) -> dict:
        """Register with a U2F site"""
        # Generate fake key handle and public key
        key_handle = hashlib.sha256(f"{site}{random.randint(0, 999999)}".encode()).hexdigest()[:32]
        public_key = hashlib.sha256(key_handle.encode()).hexdigest()[:64]
        
        registration = {
            "site": site,
            "key_handle": key_handle,
            "public_key": public_key
        }
        self.registered_sites.append(registration)
        self.save("sites", self.registered_sites)
        return registration

    def cmd_authenticate(self, site: str) -> dict:
        """Authenticate to a registered site"""
        for reg in self.registered_sites:
            if reg["site"] == site:
                # Simulate signature
                signature = hashlib.sha256(f"{reg['key_handle']}{random.randint(0, 999999)}".encode()).hexdigest()
                return {
                    "site": site,
                    "signature": signature,
                    "counter": random.randint(1, 100)
                }
        raise ValueError(f"Site '{site}' not registered")

    def cmd_list(self) -> list:
        """List all registered sites"""
        return [{"site": r["site"], "key_handle": r["key_handle"]} for r in self.registered_sites]

    def cmd_delete(self, site: str) -> str:
        """Delete registration for a site"""
        self.registered_sites = [r for r in self.registered_sites if r["site"] != site]
        self.save("sites", self.registered_sites)
        return f"Registration for '{site}' deleted"
