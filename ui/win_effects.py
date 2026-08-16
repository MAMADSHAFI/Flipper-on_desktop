# ui/win_effects.py
# ----------------------------------------------------------------------
# افکت Acrylic / Mica واقعی روی ویندوز 10/11
# ----------------------------------------------------------------------

import sys
import ctypes
from ctypes import wintypes


def enable_blur(hwnd: int, mode: str = "acrylic") -> bool:
    """
    فعال‌سازی افکت شیشه‌ای واقعی ویندوز.
    mode: "acrylic" | "mica" | "blur"
    برمی‌گرداند: True در صورت موفقیت
    """
    if sys.platform != "win32":
        return False

    try:
        # ---- روش ۱: Mica (ویندوز 11 build 22000+) ----
        if mode == "mica":
            DWMWA_SYSTEMBACKDROP_TYPE = 38
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            backdrop = ctypes.c_int(2)  # 2 = Mica
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(backdrop), ctypes.sizeof(backdrop)
            )
            dark = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(dark), ctypes.sizeof(dark)
            )
            return True

        # ---- روش ۲: Acrylic / Blur (ویندوز 10+) ----
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int),
            ]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t),
            ]

        accent = ACCENT_POLICY()
        # 3 = ACRYLIC_BLURBEHIND | 4 در بعضی نسخه‌ها
        accent.AccentState = 4 if mode == "acrylic" else 3
        accent.GradientColor = 0x99000000  # رنگ + شفافیت (AABBGGRR)

        data = WINCOMPATTRDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(
            wintypes.HWND(hwnd), ctypes.byref(data)
        )
        return True

    except Exception as e:
        print(f"[win_effects] خطا در فعال‌سازی blur: {e}")
        return False
