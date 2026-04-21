#!python3.13
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2025/10/15 12:12:12.120092
Revised: 2026/04/21 18:45:24.646268
"""

import contextlib
import ctypes
import os
import platform
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pyperclip
import qrcode
from PIL import Image
from PyQt6.QtCore import QByteArray, QEasingCurve, QEvent, QPropertyAnimation, QSettings, Qt, QTimer
from PyQt6.QtGui import QCursor, QIcon, QImage, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
ICON_PATH = _BASE / "media" / "icon.png"

DARK = {
    "bg": "#0f0f17",
    "panel": "#17171f",
    "border": "#2a2a3d",
    "text": "#e2e2ec",
    "text_dim": "#64647a",
    "accent": "#6366f1",
    "accent_hov": "#7c7fff",
    "accent_act": "#4f52d2",
    "btn": "#202030",
    "btn_hov": "#2a2a3d",
    "btn_act": "#18182a",
    "red": "#ef4444",
    "green": "#22c55e",
    "qr_bg": "#ffffff",
}

LIGHT = {
    "bg": "#f0f0f7",
    "panel": "#fafaff",
    "border": "#d0d0e0",
    "text": "#111120",
    "text_dim": "#8888a0",
    "accent": "#6366f1",
    "accent_hov": "#7c7fff",
    "accent_act": "#4f52d2",
    "btn": "#e4e4f0",
    "btn_hov": "#d8d8ec",
    "btn_act": "#cacade",
    "red": "#dc2626",
    "green": "#16a34a",
    "qr_bg": "#ffffff",
}

WINDOW_W = 380

# --- SVG icons (Lucide-style, 16x16 viewBox) ---


def _svg(color: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        f' fill="none" stroke="{color}" stroke-width="2"'
        f' stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
    )


_SVG_BODIES = {
    "sun": (
        '<circle cx="12" cy="12" r="4"/>'
        '<line x1="12" y1="2" x2="12" y2="6"/>'
        '<line x1="12" y1="18" x2="12" y2="22"/>'
        '<line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>'
        '<line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>'
        '<line x1="2" y1="12" x2="6" y2="12"/>'
        '<line x1="18" y1="12" x2="22" y2="12"/>'
        '<line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>'
        '<line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>'
    ),
    "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "eye": ('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'),
    "eye_off": (
        '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8'
        'a18.45 18.45 0 0 1 5.06-5.94"/>'
        '<path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8'
        'a18.5 18.5 0 0 1-2.16 3.19"/>'
        '<line x1="1" y1="1" x2="23" y2="23"/>'
    ),
    "x": ('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'),
    "lock": (
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    ),
    "lock_open": (
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 9.9-1"/>'
    ),
}


def _svg_icon(name: str, color: str, size: int = 16) -> QIcon:
    svg_bytes = QByteArray(_svg(color, _SVG_BODIES[name]).encode())
    renderer = QSvgRenderer(svg_bytes)
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    renderer.render(p)
    p.end()
    return QIcon(px)


def _icon_btn(name: str, color: str, size: int = 16) -> QPushButton:
    btn = QPushButton()
    btn.setObjectName("icon_btn")
    btn.setIcon(_svg_icon(name, color, size))
    btn.setFixedSize(28, 26)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    return btn


# --- Logic ---


class ClipboardProvider:
    def get_text(self) -> str:
        try:
            text = pyperclip.paste()
            return text if isinstance(text, str) and text.strip() else ""
        except Exception:
            return ""


class QRCodeGenerator:
    def __init__(self, box_size=8, border=3, max_size=320):
        self.box_size = box_size
        self.border = border
        self.max_size = max_size

    def generate(self, text: str) -> Image.Image:
        qr = qrcode.QRCode(box_size=self.box_size, border=self.border)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        return self._resize(img)

    def _resize(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        scale = min(self.max_size / w, self.max_size / h, 1.0)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return img


def copy_image_to_clipboard(img: Image.Image):
    system = platform.system()
    if system == "Windows":
        import win32clipboard

        buf = BytesIO()
        img.convert("RGB").save(buf, "BMP")
        data = buf.getvalue()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data[14:])
        win32clipboard.CloseClipboard()
    elif system == "Linux":
        with contextlib.suppress(Exception):
            buf = BytesIO()
            img.save(buf, format="PNG")
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", "image/png"],
                input=buf.getvalue(),
                check=True,
            )


def _force_foreground(hwnd: int):
    user32 = ctypes.windll.user32
    SW_SHOW = 5
    user32.ShowWindow(hwnd, SW_SHOW)
    fg = user32.GetForegroundWindow()
    if fg and fg != hwnd:
        tid_fg = user32.GetWindowThreadProcessId(fg, None)
        tid_self = ctypes.windll.kernel32.GetCurrentThreadId()
        if tid_fg != tid_self:
            user32.AttachThreadInput(tid_fg, tid_self, True)
            user32.SetForegroundWindow(hwnd)
            user32.AttachThreadInput(tid_fg, tid_self, False)
            return
    user32.SetForegroundWindow(hwnd)


# --- Helpers ---



def _clip_preview(text: str, max_chars: int = 28) -> str:
    if not text:
        return "—"
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def _screen_for_cursor() -> object:
    pos = QCursor.pos()
    screen = QApplication.screenAt(pos)
    return screen or QApplication.primaryScreen()


# --- Stylesheet ---


def build_stylesheet(c: dict) -> str:
    return f"""
    QWidget {{
        background-color: {c["bg"]};
        color: {c["text"]};
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 13px;
        border: none;
        outline: none;
    }}
    QFrame#card {{
        background-color: {c["panel"]};
        border: 1px solid {c["border"]};
        border-radius: 12px;
    }}
    QFrame#qr_frame {{
        background-color: {c["qr_bg"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 8px;
    }}
    QPushButton {{
        background-color: {c["btn"]};
        color: {c["text"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        padding: 4px 10px;
    }}
    QPushButton:hover   {{ background-color: {c["btn_hov"]}; border-color: {c["accent"]}; }}
    QPushButton:pressed {{ background-color: {c["btn_act"]}; }}
    QPushButton#icon_btn {{
        background-color: transparent;
        border: none;
        border-radius: 5px;
        padding: 3px;
    }}
    QPushButton#icon_btn:hover   {{ background-color: {c["btn_hov"]}; }}
    QPushButton#icon_btn:pressed {{ background-color: {c["btn_act"]}; }}
    QPushButton#icon_btn_active {{
        background-color: {c["accent"]};
        border: none;
        border-radius: 5px;
        padding: 3px;
    }}
    QPushButton#icon_btn_active:hover   {{ background-color: {c["accent_hov"]}; }}
    QPushButton#icon_btn_active:pressed {{ background-color: {c["accent_act"]}; }}
    QPushButton#accent {{
        background-color: {c["accent"]};
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 5px 14px;
        font-weight: 600;
    }}
    QPushButton#accent:hover   {{ background-color: {c["accent_hov"]}; }}
    QPushButton#accent:pressed {{ background-color: {c["accent_act"]}; }}
    QLabel#preview  {{ color: {c["text_dim"]}; font-size: 12px; font-family: "Consolas", monospace; }}
    QLabel#revealed {{ color: {c["text"]}; font-size: 12px; font-family: "Consolas", monospace; }}
    QLabel#error    {{ color: {c["red"]}; font-size: 13px; }}
    QLabel#status_ok  {{ color: {c["green"]}; font-size: 11px; }}
    QLabel#status_err {{ color: {c["red"]};   font-size: 11px; }}
    QTextEdit {{
        background-color: {c["panel"]};
        color: {c["text"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        padding: 6px;
        font-family: "Consolas", "Courier New", monospace;
        font-size: 12px;
        selection-background-color: {c["accent"]};
    }}
    QScrollBar:vertical {{
        background: {c["bg"]};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {c["border"]};
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


# --- Full Text Dialog ---


class FullTextDialog(QDialog):
    def __init__(self, text: str, c: dict, parent=None):
        super().__init__(parent, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(build_stylesheet(c))
        self.resize(520, 340)
        self._drag_pos = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 14)
        layout.setSpacing(8)

        bar = QHBoxLayout()
        title = QLabel("Clipboard Text")
        title.setStyleSheet("font-weight: 600; font-size: 13px;")
        close_btn = _icon_btn("x", c["text_dim"], 14)
        close_btn.setFixedSize(26, 26)
        close_btn.clicked.connect(self.close)
        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(close_btn)
        layout.addLayout(bar)

        editor = QTextEdit()
        editor.setPlainText(text)
        editor.setReadOnly(True)
        layout.addWidget(editor)

        if parent:
            pg = parent.frameGeometry()
            self.move(pg.center() - self.rect().center())

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def changeEvent(self, e):
        if e.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            pinned = self.parent()._pinned if self.parent() else False
            if not pinned:
                self.close()
        super().changeEvent(e)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.close()


# --- Main Window ---


class FluxWindow(QWidget):
    def __init__(self, clip_text: str, qr_img: Image.Image | None, qr_error: str | None):
        super().__init__()
        self.clip_text = clip_text
        self.qr_img = qr_img
        self.qr_error = qr_error

        self._settings = QSettings("flux", "flux")
        self.dark_mode: bool = self._settings.value("dark_mode", True, type=bool)
        self.text_visible: bool = self._settings.value("text_visible", False, type=bool)
        self._pinned: bool = self._settings.value("pinned", False, type=bool)
        self._drag_pos = None
        self._opening_child = False

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setFixedWidth(WINDOW_W)

        self._build_ui()
        self._apply_theme()
        self.show()
        QApplication.processEvents()
        self._center()
        self.activateWindow()
        self.raise_()
        self._focus_attempts = 0

        self._autofocus_timer = QTimer(self)
        self._autofocus_timer.setInterval(50)
        self._autofocus_timer.timeout.connect(self._force_focus)
        self._autofocus_timer.start()

    def _force_focus(self):
        self.activateWindow()
        self.raise_()
        if platform.system() == "Windows":
            hwnd = int(self.winId())
            _force_foreground(hwnd)
        self._focus_attempts += 1
        if self._focus_attempts >= 5:
            self._autofocus_timer.stop()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = QFrame(objectName="card")
        self._card.setFixedWidth(WINDOW_W)
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(14, 11, 14, 14)
        root.setSpacing(10)

        # --- Title bar ---
        bar = QHBoxLayout()
        bar.setSpacing(4)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(16, 16)

        title = QLabel("flux")
        title.setStyleSheet("font-weight: 700; font-size: 14px; letter-spacing: 1px; margin-left: 4px;")

        self._btn_theme = _icon_btn("sun", DARK["text_dim"])
        self._btn_theme.clicked.connect(self._toggle_theme)

        self._btn_pin = _icon_btn("lock_open", DARK["text_dim"])
        self._btn_pin.setToolTip("Pin: keep open when focus is lost")
        self._btn_pin.clicked.connect(self._toggle_pin)

        self._btn_close = _icon_btn("x", DARK["text_dim"])
        self._btn_close.clicked.connect(self.close)

        bar.addWidget(self._icon_lbl)
        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(self._btn_theme)
        bar.addWidget(self._btn_pin)
        bar.addWidget(self._btn_close)
        root.addLayout(bar)

        # --- Clipboard row ---
        clip_row = QHBoxLayout()
        clip_row.setSpacing(6)

        self._lbl_clip = QLabel(objectName="preview")
        self._lbl_clip.setFixedWidth(WINDOW_W - 14 * 2 - 40)
        self._lbl_clip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._lbl_clip.mousePressEvent = (
            lambda e: self._show_full_text()
            if e.button() == Qt.MouseButton.LeftButton and self.text_visible
            else None
        )

        self._btn_eye = _icon_btn("eye", DARK["text_dim"])
        self._btn_eye.setToolTip("Show/hide  •  Click label for full text")
        self._btn_eye.setFixedSize(30, 26)
        self._btn_eye.clicked.connect(self._toggle_text)

        clip_row.addWidget(self._lbl_clip, stretch=1)
        clip_row.addWidget(self._btn_eye)
        root.addLayout(clip_row)

        # --- QR area ---
        if self.qr_img:
            qr_w = self.qr_img.width + 16  # image width + 8px padding each side
            qr_frame = QFrame(objectName="qr_frame")
            qr_frame.setFixedWidth(qr_w)
            qr_layout = QVBoxLayout(qr_frame)
            qr_layout.setContentsMargins(8, 8, 8, 8)
            qr_layout.setSpacing(0)

            self._lbl_qr = QLabel()
            self._lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._lbl_qr.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self._lbl_qr.setToolTip("Right-click to copy QR as image")
            self._lbl_qr.mousePressEvent = self._lbl_qr_mouse_press
            self._set_qr_pixmap()
            qr_layout.addWidget(self._lbl_qr, alignment=Qt.AlignmentFlag.AlignCenter)

            root.addWidget(qr_frame, alignment=Qt.AlignmentFlag.AlignCenter)

            self._lbl_status = QLabel("")
            self._lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._lbl_status.setFixedHeight(18)

            self._status_effect = QGraphicsOpacityEffect(self._lbl_status)
            self._lbl_status.setGraphicsEffect(self._status_effect)
            self._status_effect.setOpacity(0.0)

            self._status_anim = QPropertyAnimation(self._status_effect, b"opacity", self)
            self._status_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            self._status_timer = QTimer(self)
            self._status_timer.setSingleShot(True)
            self._status_timer.timeout.connect(self._fade_out_status)

            root.addWidget(self._lbl_status)
        else:
            lbl_err = QLabel(self.qr_error or "No QR code.", objectName="error")
            lbl_err.setWordWrap(True)
            lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(lbl_err)

    def _lbl_qr_mouse_press(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self._copy_qr()
        elif e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _set_qr_pixmap(self):
        img = self.qr_img.convert("RGBA")
        w, h = img.size
        qimg = QImage(img.tobytes(), w, h, QImage.Format.Format_RGBA8888)
        self._lbl_qr.setPixmap(QPixmap.fromImage(qimg))

    # --- Theme ---

    def _apply_theme(self):
        c = DARK if self.dark_mode else LIGHT
        self.setStyleSheet(build_stylesheet(c))
        if ICON_PATH.exists():
            self._icon_lbl.setPixmap(
                QPixmap(str(ICON_PATH)).scaled(
                    16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            )
        self._btn_theme.setIcon(_svg_icon("sun" if self.dark_mode else "moon", c["text_dim"]))
        self._refresh_clip_label()
        self._btn_close.setIcon(_svg_icon("x", c["text_dim"]))
        self._btn_eye.setIcon(_svg_icon("eye" if not self.text_visible else "eye_off", c["text_dim"]))
        self._refresh_pin_btn()

    def _refresh_clip_label(self):
        if self.text_visible:
            self._lbl_clip.setObjectName("revealed")
            self._lbl_clip.setText(_clip_preview(self.clip_text, 42))
        else:
            if self.clip_text:
                self._lbl_clip.setObjectName("preview")
                self._lbl_clip.setText("•" * min(len(self.clip_text), 16))
            else:
                self._lbl_clip.setObjectName("preview")
                self._lbl_clip.setText("—")
        self._lbl_clip.style().unpolish(self._lbl_clip)
        self._lbl_clip.style().polish(self._lbl_clip)

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _toggle_pin(self):
        self._pinned = not self._pinned
        self._refresh_pin_btn()
        if not self._pinned:
            for w in self.findChildren(QDialog):
                w.close()

    def _refresh_pin_btn(self):
        c = DARK if self.dark_mode else LIGHT
        if self._pinned:
            self._btn_pin.setObjectName("icon_btn_active")
            self._btn_pin.setIcon(_svg_icon("lock", "#ffffff"))
            self._btn_pin.setToolTip("Pinned: will stay open")
        else:
            self._btn_pin.setObjectName("icon_btn")
            self._btn_pin.setIcon(_svg_icon("lock_open", c["text_dim"]))
            self._btn_pin.setToolTip("Pin: keep open when focus is lost")
        self._btn_pin.style().unpolish(self._btn_pin)
        self._btn_pin.style().polish(self._btn_pin)

    # --- Text visibility ---

    def _toggle_text(self):
        self.text_visible = not self.text_visible
        c = DARK if self.dark_mode else LIGHT
        self._btn_eye.setIcon(_svg_icon("eye_off" if self.text_visible else "eye", c["text_dim"]))
        self._refresh_clip_label()
        self.adjustSize()

    def _show_full_text(self):
        self._opening_child = True
        dlg = FullTextDialog(self.clip_text, DARK if self.dark_mode else LIGHT, self)
        self._opening_child = False
        dlg.show()

    # --- QR copy ---

    def _copy_qr(self):
        if self.qr_img is None:
            return
        try:
            copy_image_to_clipboard(self.qr_img)
            self._set_status("✓  Copied to clipboard", ok=True)
        except Exception:
            self._set_status("⚠  Copy failed", ok=False)

    def _set_status(self, msg: str, ok: bool = True):
        self._status_anim.stop()
        self._lbl_status.setObjectName("status_ok" if ok else "status_err")
        self._lbl_status.setText(msg)
        self._lbl_status.style().unpolish(self._lbl_status)
        self._lbl_status.style().polish(self._lbl_status)
        self._status_anim.setDuration(120)
        self._status_anim.setStartValue(0.0)
        self._status_anim.setEndValue(1.0)
        self._status_anim.start()
        self._status_timer.start(2200)

    def _fade_out_status(self):
        self._status_anim.stop()
        self._status_anim.setDuration(600)
        self._status_anim.setStartValue(1.0)
        self._status_anim.setEndValue(0.0)
        self._status_anim.start()

    # --- Window behavior ---

    def _center(self):
        screen = _screen_for_cursor()
        self.adjustSize()
        geom = screen.availableGeometry()
        self.move(
            geom.center().x() - self.width() // 2,
            geom.center().y() - self.height() // 2,
        )

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def changeEvent(self, e):
        if (
            e.type() == QEvent.Type.ActivationChange
            and not self.isActiveWindow()
            and not self._pinned
            and not self._opening_child
            and self._focus_attempts >= 5
        ):
            active = QApplication.activeWindow()
            if active is None or (active is not self and active.parent() is not self):
                self.close()
        super().changeEvent(e)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.close()

    def closeEvent(self, e):
        self._autofocus_timer.stop()
        self._settings.setValue("dark_mode", self.dark_mode)
        self._settings.setValue("pinned", self._pinned)
        self._settings.setValue("text_visible", self.text_visible)
        super().closeEvent(e)
        QApplication.quit()


# --- Entry Point ---


if __name__ == "__main__":
    import traceback

    _log = Path(__file__).parent / "flux_debug.log"
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("flux.flux")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName("flux")
        if ICON_PATH.exists():
            app.setWindowIcon(QIcon(str(ICON_PATH)))

        clip = ClipboardProvider()
        gen = QRCodeGenerator()
        text = clip.get_text()
        qr_img: Image.Image | None = None
        qr_error: str | None = None

        if not text:
            qr_error = "Clipboard is empty."
        else:
            try:
                qr_img = gen.generate(text)
            except (qrcode.exceptions.DataOverflowError, ValueError):
                qr_error = f"Text is too long for a QR code ({len(text.encode())} / 2,953 bytes)."
            except Exception as exc:
                qr_error = f"Could not generate QR code: {exc}"

        win = FluxWindow(text, qr_img, qr_error)
        code = app.exec()
        os._exit(code)
    except Exception:
        _log.write_text(traceback.format_exc())
        os._exit(1)
