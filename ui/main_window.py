# ui/main_window.py
import sys
import inspect

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QLabel,
    QMessageBox, QInputDialog, QStackedWidget, QFrame, QScrollArea,
    QGridLayout, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QDateTime, QSize,
)
from PyQt6.QtGui import QColor

from core.kernel import Kernel
from ui.theme import get_theme, make_icon, ICONS, DARK_PALETTE, LIGHT_PALETTE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlipperWin")
        self.setGeometry(100, 100, 1000, 680)
        self.setMinimumSize(820, 560)

        self.theme_mode = "dark"          # حالت فعلی تم
        self.current_module = None

        self.kernel = Kernel()
        self.kernel.boot()

        self._build_ui()
        self._load_modules()
        self._apply_theme()

        # رفرش نوار وضعیت
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._update_statusbar)
        self.refresh_timer.start(1000)

        self._fade_in_window()

    # ------------------------------------------------------------------
    #  ساخت UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(14, 14, 14, 8)
        body.setSpacing(14)

        body.addWidget(self._build_sidebar(), 0)
        body.addWidget(self._build_content(), 1)

        root.addLayout(body, 1)
        root.addWidget(self._build_statusbar(), 0)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        self._add_shadow(sidebar, blur=30, y=4)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(14, 20, 14, 14)
        lay.setSpacing(6)

        title = QLabel("FlipperWin")
        title.setObjectName("AppTitle")
        lay.addWidget(title)

        subtitle = QLabel("MULTI-TOOL SUITE")
        subtitle.setObjectName("AppSubtitle")
        lay.addWidget(subtitle)
        lay.addSpacing(16)

        self.nav = QListWidget()
        self.nav.setObjectName("NavList")
        self.nav.currentRowChanged.connect(self._on_nav)
        lay.addWidget(self.nav, 1)

        # دکمه تعویض تم
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("ThemeToggle")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        lay.addWidget(self.theme_btn)

        return sidebar

    def _build_content(self) -> QWidget:
        self.stack = QStackedWidget()
        self._add_shadow(self.stack, blur=30, y=4)

        self.home_page = self._build_home_page()
        self.stack.addWidget(self.home_page)        # index 0
        self.module_page = self._build_module_page()
        self.stack.addWidget(self.module_page)      # index 1
        return self.stack

    def _build_home_page(self) -> QWidget:
        page = QFrame()
        page.setObjectName("CentralWidget")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(30, 30, 30, 30)

        hello = QLabel("خوش آمدید 👋")
        hello.setStyleSheet("font-size: 26px; font-weight: 800;")
        lay.addWidget(hello)

        hint = QLabel("یک ماژول را از منوی کناری یا کارت‌های زیر انتخاب کنید.")
        hint.setStyleSheet("font-size: 14px; color: #9CA3AF;")
        lay.addWidget(hint)
        lay.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        grid_host = QWidget()
        self.cards_grid = QGridLayout(grid_host)
        self.cards_grid.setSpacing(16)
        scroll.setWidget(grid_host)
        lay.addWidget(scroll, 1)
        return page

    def _build_module_page(self) -> QWidget:
        page = QFrame()
        page.setObjectName("CentralWidget")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)

        self.module_title = QLabel("ماژولی انتخاب نشده")
        self.module_title.setStyleSheet("font-size: 22px; font-weight: 800;")
        lay.addWidget(self.module_title)

        self.module_description = QLabel("")
        self.module_description.setWordWrap(True)
        self.module_description.setStyleSheet("color: #9CA3AF;")
        lay.addWidget(self.module_description)

        self.module_version = QLabel("")
        self.module_version.setStyleSheet("color: #6B7280; font-size: 12px;")
        lay.addWidget(self.module_version)
        lay.addSpacing(14)

        cmd_host = QWidget()
        self.commands_layout = QHBoxLayout(cmd_host)
        self.commands_layout.setContentsMargins(0, 0, 0, 0)
        self.commands_layout.setSpacing(10)
        self.commands_layout.addStretch()
        lay.addWidget(cmd_host)
        lay.addSpacing(10)

        lay.addWidget(QLabel("خروجی:"))
        self.output_log = QTextEdit()
        self.output_log.setObjectName("Console")
        self.output_log.setReadOnly(True)
        lay.addWidget(self.output_log, 1)
        return page

    def _build_statusbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("StatusBar")
        bar.setFixedHeight(34)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)

        self.status_conn = QLabel("● آماده")
        self.status_conn.setObjectName("StatusLabel")
        lay.addWidget(self.status_conn)
        lay.addStretch()

        self.status_clock = QLabel("")
        self.status_clock.setObjectName("StatusLabel")
        lay.addWidget(self.status_clock)
        return bar

    # ------------------------------------------------------------------
    #  بارگذاری ماژول‌ها
    # ------------------------------------------------------------------
    def _load_modules(self) -> None:
        self.nav.clear()

        home_item = QListWidgetItem("  خانه")
        home_item.setIcon(make_icon(ICONS["home"], self._palette().text_secondary))
        self.nav.addItem(home_item)

        for name, module in self.kernel.modules.items():
            item = QListWidgetItem(f"  {name}")
            icon_key = name.lower() if name.lower() in ICONS else "settings"
            item.setIcon(make_icon(ICONS[icon_key], self._palette().text_secondary))
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.nav.addItem(item)

        self._build_home_cards()
        self.nav.setCurrentRow(0)

    def _build_home_cards(self) -> None:
        while self.cards_grid.count():
            w = self.cards_grid.takeAt(0).widget()
            if w:
                w.setParent(None)

        col = row = 0
        for name, module in self.kernel.modules.items():
            card = self._make_module_card(name, module)
            self.cards_grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _make_module_card(self, name, module) -> QWidget:
        card = QFrame()
        card.setProperty("class", "Card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setFixedHeight(140)
        self._add_shadow(card, blur=20, y=3)

        lay = QVBoxLayout(card)
        icon_lbl = QLabel(getattr(module, "icon", "📦"))
        icon_lbl.setStyleSheet("font-size: 28px;")
        lay.addWidget(icon_lbl)

        title = QLabel(name)
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        lay.addWidget(title)

        desc = QLabel(getattr(module, "description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        lay.addWidget(desc)
        lay.addStretch()

        card.mousePressEvent = lambda e, n=name: self._open_module(n)
        return card

    # ------------------------------------------------------------------
    #  ناوبری
    # ------------------------------------------------------------------
    def _on_nav(self, row: int) -> None:
        if row <= 0:
            self._fade_stack(0)
            return
        item = self.nav.item(row)
        name = item.data(Qt.ItemDataRole.UserRole)
        if name:
            self._open_module(name)

    def _open_module(self, name: str) -> None:
        module = self.kernel.modules.get(name)
        if not module:
            return
        self.current_module = module

        self.module_title.setText(f"{getattr(module,'icon','')} {module.name}")
        self.module_description.setText(module.description)
        self.module_version.setText(f"نسخه: {module.version}")

        # پاک‌سازی دکمه‌های قبلی
        for i in reversed(range(self.commands_layout.count())):
            w = self.commands_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for attr in dir(module):
            if attr.startswith("cmd_"):
                cmd = attr[4:]
                btn = QPushButton(cmd)
                btn.clicked.connect(lambda _, c=cmd: self._execute_command(c))
                self.commands_layout.addWidget(btn)
        self.commands_layout.addStretch()

        self._fade_stack(1)

    # ------------------------------------------------------------------
    #  اجرای دستور
    # ------------------------------------------------------------------
    def _execute_command(self, command: str) -> None:
        try:
            sig = inspect.signature(getattr(self.current_module, f"cmd_{command}"))
            kwargs = {}
            for p in sig.parameters.values():
                if p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty:
                    text, ok = QInputDialog.getText(
                        self, "ورودی دستور", f"مقدار '{p.name}':"
                    )
                    if not ok:
                        self.output_log.append(f"دستور '{command}' لغو شد.")
                        return
                    kwargs[p.name] = text

            result = self.kernel.run_command(self.current_module.name, command, **kwargs)
            self.output_log.append(f"> {self.current_module.name}.{command}({kwargs})")
            self.output_log.append(f"  نتیجه: {result}\n")
        except Exception as e:
            self.output_log.append(f"[خطا] {e}")
            QMessageBox.critical(self, "خطا", str(e))

    # ------------------------------------------------------------------
    #  تم و افکت‌ها
    # ------------------------------------------------------------------
    def _palette(self):
        return DARK_PALETTE if self.theme_mode == "dark" else LIGHT_PALETTE

    def _apply_theme(self) -> None:
        self.setStyleSheet(get_theme(self.theme_mode))
        icon = ICONS["moon"] if self.theme_mode == "dark" else ICONS["sun"]
        self.theme_btn.setIcon(make_icon(icon, self._palette().text_primary))
        self.theme_btn.setText("  تم روشن" if self.theme_mode == "dark" else "  تم تاریک")
        self._refresh_nav_icons()
        self._try_win_blur()

    def _toggle_theme(self) -> None:
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self._apply_theme()

    def _refresh_nav_icons(self) -> None:
        color = self._palette().text_secondary
        self.nav.item(0).setIcon(make_icon(ICONS["home"], color))
        for i in range(1, self.nav.count()):
            name = self.nav.item(i).data(Qt.ItemDataRole.UserRole) or ""
            key = name.lower() if name.lower() in ICONS else "settings"
            self.nav.item(i).setIcon(make_icon(ICONS[key], color))

    def _try_win_blur(self) -> None:
        try:
            from ui.win_effects import enable_blur
            enable_blur(int(self.winId()), mode="acrylic")
        except Exception:
            pass

    # ------------------------------------------------------------------
    #  انیمیشن‌ها
    # ------------------------------------------------------------------
    def _add_shadow(self, w, blur=25, y=4):
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(blur)
        eff.setXOffset(0)
        eff.setYOffset(y)
        eff.setColor(QColor(0, 0, 0, 130))
        w.setGraphicsEffect(eff)

    def _fade_in_window(self):
        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(350)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def _fade_stack(self, index: int):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        page.setWindowOpacity(0.0)
        eff = QGraphicsDropShadowEffect()  # trick برای opacity روی widget
        # انیمیشن ساده‌ی محو
        anim = QPropertyAnimation(page, b"windowOpacity")
        anim.setDuration(250)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        self._page_anim = anim

    # ------------------------------------------------------------------
    #  نوار وضعیت
    # ------------------------------------------------------------------
    def _update_statusbar(self) -> None:
        now = QDateTime.currentDateTime().toString("hh:mm:ss  |  yyyy/MM/dd")
        self.status_clock.setText(now)
        count = len(self.kernel.modules)
        self.status_conn.setText(f"● آماده — {count} ماژول بارگذاری شد")

    def closeEvent(self, event) -> None:
        self.kernel.shutdown()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
