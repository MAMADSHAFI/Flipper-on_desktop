# ui/theme.py
# ----------------------------------------------------------------------
# سیستم تم قابل‌تعویض (Light/Dark) با متغیرهای دینامیک
# ----------------------------------------------------------------------

from dataclasses import dataclass
from typing import Literal

ThemeMode = Literal["dark", "light"]


@dataclass
class ColorPalette:
    """پالت رنگی مدرن برای هر تم."""
    # برند Flipper
    accent: str
    accent_hover: str
    accent_press: str
    secondary: str
    success: str
    
    # پس‌زمینه
    bg_deep: str
    bg_surface: str
    bg_card: str
    
    # شیشه‌ای
    glass_fill: str
    glass_border: str
    glass_hover: str
    
    # متن
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # خاص
    console_text: str
    shadow_color: str


# تم تاریک (پیش‌فرض)
DARK_PALETTE = ColorPalette(
    accent="#FF8201",
    accent_hover="#FF9A33",
    accent_press="#E06E00",
    secondary="#00B7FF",
    success="#6DD231",
    
    bg_deep="#0A0C0F",
    bg_surface="#12151A",
    bg_card="#1A1E25",
    
    glass_fill="rgba(255, 255, 255, 0.04)",
    glass_border="rgba(255, 255, 255, 0.10)",
    glass_hover="rgba(255, 255, 255, 0.08)",
    
    text_primary="#F5F7FA",
    text_secondary="#D1D5DB",
    text_muted="#9CA3AF",
    
    console_text="#6DD231",
    shadow_color="rgba(0, 0, 0, 0.6)",
)

# تم روشن
LIGHT_PALETTE = ColorPalette(
    accent="#FF6B00",
    accent_hover="#FF8201",
    accent_press="#CC5500",
    secondary="#0095E0",
    success="#4CAF50",
    
    bg_deep="#FAFBFC",
    bg_surface="#FFFFFF",
    bg_card="#F8F9FA",
    
    glass_fill="rgba(0, 0, 0, 0.02)",
    glass_border="rgba(0, 0, 0, 0.08)",
    glass_hover="rgba(0, 0, 0, 0.04)",
    
    text_primary="#1F2937",
    text_secondary="#4B5563",
    text_muted="#9CA3AF",
    
    console_text="#059669",
    shadow_color="rgba(0, 0, 0, 0.15)",
)


def get_theme(mode: ThemeMode = "dark") -> str:
    """تولید استایل QSS بر اساس حالت تم."""
    p = DARK_PALETTE if mode == "dark" else LIGHT_PALETTE
    
    return f"""
    /* ---------- پایه ---------- */
    QWidget {{
        color: {p.text_primary};
        font-family: "Segoe UI Variable Text", "Vazirmatn UI", sans-serif;
        font-size: 14px;
    }}

    QMainWindow {{
        background: {p.bg_deep};
    }}

    #CentralWidget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {p.bg_deep}, stop:1 {p.bg_surface});
    }}

    /* ---------- سایدبار شیشه‌ای ---------- */
    #Sidebar {{
        background: {p.glass_fill};
        border: 1px solid {p.glass_border};
        border-radius: 20px;
    }}

    #AppTitle {{
        font-size: 22px;
        font-weight: 800;
        color: {p.accent};
        padding: 6px 8px;
        letter-spacing: -0.5px;
    }}

    #AppSubtitle {{
        font-size: 11px;
        font-weight: 600;
        color: {p.text_muted};
        text-transform: uppercase;
        letter-spacing: 0.8p
        x;
    }}

    /* ---------- لیست ناوبری ---------- */
    #NavList {{
        background: transparent;
        border: none;
        outline: none;
        padding: 8px 0;
    }}

    #NavList::item {{
        background: transparent;
        color: {p.text_secondary};
        padding: 14px 20px;
        margin: 4px 12px;
        border-radius: 14px;
        font-size: 15px;
        font-weight: 600;
    }}

    #NavList::item:hover {{
        background: {p.glass_hover};
        color: {p.text_primary};
    }}

    #NavList::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {p.accent}, stop:1 {p.accent_hover});
        color: white;
        font-weight: 700;
    }}

    /* ---------- کارت‌های محتوا ---------- */
    .Card {{
        background: {p.glass_fill};
        border: 1px solid {p.glass_border};
        border-radius: 18px;
        padding: 24px;
    }}

    .Card:hover {{
        background: {p.glass_hover};
        border-color: {p.accent};
    }}

    /* ---------- دکمه‌ها ---------- */
    QPushButton {{
        background: {p.accent};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
    }}

    QPushButton:hover {{
        background: {p.accent_hover};
    }}

    QPushButton:pressed {{
        background: {p.accent_press};
    }}

    QPushButton:disabled {{
        background: {p.text_muted};
        color: {p.bg_surface};
    }}

    QPushButton#SecondaryButton {{
        background: {p.glass_fill};
        color: {p.text_primary};
        border: 2px solid {p.glass_border};
    }}

    QPushButton#SecondaryButton:hover {{
        background: {p.glass_hover};
        border-color: {p.secondary};
    }}

    /* ---------- کنسول (QTextEdit) ---------- */
    #Console {{
        background: {p.bg_deep};
        color: {p.console_text};
        border: 1px solid {p.glass_border};
        border-radius: 12px;
        padding: 16px;
        font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
        font-size: 13px;
        selection-background-color: {p.accent};
    }}

    /* ---------- اسکرول‌بار مینیمال ---------- */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {p.glass_border};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {p.text_muted};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
    }}

    QScrollBar::handle:horizontal {{
        background: {p.glass_border};
        border-radius: 5px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {p.text_muted};
    }}

    /* ---------- نوار وضعیت ---------- */
    #StatusBar {{
        background: {p.glass_fill};
        border-top: 1px solid {p.glass_border};
        color: {p.text_secondary};
        font-size: 12px;
        padding: 8px 16px;
    }}

    #StatusLabel {{
        color: {p.text_muted};
        padding: 0 8px;
    }}

    /* ---------- تاگل تم ---------- */
    #ThemeToggle {{
        background: {p.glass_fill};
        border: 2px solid {p.glass_border};
        border-radius: 20px;
        padding: 8px 12px;
        font-size: 18px;
    }}

    #ThemeToggle:hover {{
        background: {p.glass_hover};
        border-color: {p.accent};
    }}
    """


# ادامه دیکشنری ICONS در ui/theme.py

ICONS = {
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>""",

    "rfid": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M7 15h0M2 9.5h20"/></svg>""",

    "settings": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",

    "sun": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>""",

    "moon": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/></svg>""",
}


def make_icon(svg: str, color: str) -> "QIcon":
    """تبدیل رشته‌ی SVG به QIcon با رنگ دلخواه."""
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtCore import Qt
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtGui import QPainter

    svg = svg.replace("currentColor", color)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


