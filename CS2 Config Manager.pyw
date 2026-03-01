"""
CS2 Config Manager
Bootstrap: installs PyQt6 if missing, then re-launches.
"""

import sys
import subprocess

def bootstrap():
    try:
        import PyQt6
    except ImportError:
        print("PyQt6 not found — installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
        print("Installed. Restarting...")
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)

bootstrap()

# ── Imports ───────────────────────────────────────────────────────────────────
import json
import platform
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QCheckBox,
    QGroupBox, QFrame, QSplitter, QTextEdit,
    QMessageBox, QDialog, QStackedWidget, QScrollArea,
    QButtonGroup, QRadioButton, QAbstractButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

# ── Constants ─────────────────────────────────────────────────────────────────
APP_NAME = "CS2 CONFIG MANAGER"
ORG_NAME = "Pure Mint Software"

SETTINGS_FILES = [
    "cs2_machine_convars.vcfg",
    "cs2_user_convars_0_slot0.vcfg",
    "cs2_user_keys_0_slot0.vcfg",
]

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    DEFAULT_STEAM_BASE = r"C:\Program Files (x86)\Steam\userdata"
    DEFAULT_CSGO_CFG   = r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg"
else:
    DEFAULT_STEAM_BASE = str(Path.home() / ".steam" / "steam" / "userdata")
    DEFAULT_CSGO_CFG   = str(Path.home() / ".steam" / "steam" / "steamapps" / "common"
                             / "Counter-Strike Global Offensive" / "game" / "csgo" / "cfg")

STEAM_SUFFIX = "730/local/cfg"

# ── Colours ───────────────────────────────────────────────────────────────────
C_BG        = "#0d0f14"
C_BG2       = "#161820"
C_BORDER    = "#2a2f3d"
C_GOLD      = "#e8a020"
C_GOLD_DIM  = "#3a3010"
C_TEXT      = "#c8cdd8"
C_DIM       = "#4a5565"
C_GREEN     = "#4a9a5a"
C_GREEN_DIM = "#1a3a20"
C_AMBER     = "#d08020"
C_AMBER_DIM = "#3a2800"
C_RED       = "#c04040"
C_RED_DIM   = "#3a1010"
C_LOG_TEXT  = "#7a8a6a"

# ── Stylesheet ────────────────────────────────────────────────────────────────
STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QGroupBox {{
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    margin-top: 16px;
    padding-top: 10px;
    padding-bottom: 6px;
    font-weight: bold;
    color: {C_GOLD};
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 2px;
    padding: 2px 6px;
}}
QLineEdit {{
    background: {C_BG2};
    border: 1px solid {C_BORDER};
    border-radius: 3px;
    padding: 5px 8px;
    color: {C_TEXT};
    selection-background-color: {C_GOLD};
}}
QLineEdit:focus {{ border-color: {C_GOLD}; }}
QPushButton {{
    background: #1e2130;
    border: 1px solid {C_BORDER};
    border-radius: 3px;
    padding: 5px 14px;
    color: {C_TEXT};
}}
QPushButton:hover {{
    background: #252a3a;
    border-color: {C_GOLD};
    color: {C_GOLD};
}}
QPushButton:pressed {{
    background: {C_GOLD};
    color: {C_BG};
}}
QPushButton#run_btn {{
    background: {C_GOLD};
    color: {C_BG};
    font-weight: bold;
    font-size: 13px;
    padding: 4px 24px;
    border: none;
    letter-spacing: 1px;
}}
QPushButton#run_btn:hover {{ background: #ffb830; }}
QPushButton#run_btn:pressed {{ background: #c07010; }}
QPushButton#run_btn:disabled {{ background: #3a3010; color: #6a5a20; }}
QPushButton#browse_btn {{
    background: {C_GOLD_DIM};
    border: 1px solid {C_GOLD};
    border-radius: 3px;
    color: {C_GOLD};
    font-weight: bold;
    padding: 5px 10px;
}}
QPushButton#browse_btn:hover {{ background: {C_GOLD}; color: {C_BG}; }}
QPushButton#del_btn {{
    background: #1e2130;
    border: 1px solid #3a2020;
    color: #a05050;
    padding: 0px;
}}
QPushButton#del_btn:hover {{ border-color: {C_RED}; color: {C_RED}; }}
QCheckBox {{ spacing: 8px; color: {C_TEXT}; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {C_BORDER};
    border-radius: 2px;
    background: {C_BG2};
}}
QCheckBox::indicator:checked {{ background: {C_GOLD}; border-color: {C_GOLD}; }}
QRadioButton {{ spacing: 8px; color: {C_TEXT}; padding: 4px 0px; }}
QRadioButton::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {C_BORDER};
    border-radius: 7px;
    background: {C_BG2};
}}
QRadioButton::indicator:checked {{ background: {C_GOLD}; border-color: {C_GOLD}; }}
QTextEdit {{
    background: #070809;
    border: 1px solid #1a1f2d;
    border-radius: 3px;
    color: {C_LOG_TEXT};
    font-family: 'Consolas', monospace;
    font-size: 12px;
    padding: 6px;
}}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QFrame#separator {{ background: {C_BORDER}; max-height: 1px; }}
QSplitter::handle {{ background: {C_BG}; width: 6px; }}
QSplitter::handle:hover {{ background: #1e2130; }}
"""

WIZARD_STYLE = STYLE + f"""
QDialog {{ background-color: {C_BG}; }}
QLabel#page_title {{
    font-size: 18px; font-weight: bold;
    color: {C_GOLD}; letter-spacing: 2px;
}}
QLabel#page_sub {{ color: {C_DIM}; font-size: 11px; letter-spacing: 1px; }}
QLabel#field_label {{ color: {C_GOLD}; font-size: 11px; font-weight: bold; letter-spacing: 1px; }}
QLabel#field_hint {{ color: {C_DIM}; font-size: 11px; font-style: italic; }}
QFrame#wiz_sep {{ background: #1e2230; max-height: 1px; }}
QPushButton#btn_next {{
    background: {C_GOLD}; color: {C_BG};
    font-weight: bold; border: none;
    padding: 8px 28px; letter-spacing: 1px;
}}
QPushButton#btn_next:hover {{ background: #ffb830; }}
QPushButton#btn_next:disabled {{ background: {C_GOLD_DIM}; color: #6a5a20; }}
QPushButton#btn_add {{ background: #1e2130; border: 1px solid #2a3a2a; color: #6a9a6a; }}
QPushButton#btn_add:hover {{ border-color: #6a9a6a; }}
QPushButton#btn_remove {{
    background: #1e2130; border: 1px solid #3a2020;
    color: #a05050; padding: 4px 10px;
}}
QPushButton#btn_remove:hover {{ border-color: {C_RED}; color: {C_RED}; }}
QRadioButton#mode_btn {{
    font-size: 13px; color: {C_TEXT};
    padding: 10px 14px;
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    background: {C_BG2};
}}
QRadioButton#mode_btn:checked {{
    border-color: {C_GOLD};
    color: {C_GOLD};
    background: {C_GOLD_DIM};
}}
"""


# ── Data structures ────────────────────────────────────────────────────────────
@dataclass
class FileStatus:
    name: str
    backup_path: Path
    source_path: Path       # where the "live" copy lives (steam cfg or game cfg)
    source_label: str       # human name of source location

    backup_exists: bool = False
    source_exists: bool = False
    backup_mtime: Optional[datetime] = None
    source_mtime: Optional[datetime] = None

    def refresh(self):
        self.backup_exists = self.backup_path.exists()
        self.source_exists = self.source_path.exists()
        self.backup_mtime  = (datetime.fromtimestamp(self.backup_path.stat().st_mtime)
                               if self.backup_exists else None)
        self.source_mtime  = (datetime.fromtimestamp(self.source_path.stat().st_mtime)
                               if self.source_exists else None)

    @property
    def backup_newer(self) -> bool:
        if self.backup_mtime and self.source_mtime:
            return self.backup_mtime > self.source_mtime
        return False

    @property
    def source_newer(self) -> bool:
        if self.backup_mtime and self.source_mtime:
            return self.source_mtime > self.backup_mtime
        return False

    @property
    def age_delta_days(self) -> Optional[int]:
        if self.backup_mtime and self.source_mtime:
            return abs((self.source_mtime - self.backup_mtime).days)
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────
def is_valid_steam_id(steam_id: str) -> bool:
    sid = steam_id.strip()
    return bool(sid) and sid.isdigit()

def build_steam_path(steam_id: str) -> str:
    sid = steam_id.strip()
    if not sid:
        return ""
    return str(Path(DEFAULT_STEAM_BASE) / sid / STEAM_SUFFIX)

def build_steam_path_masked(steam_id: str) -> str:
    if not steam_id.strip():
        return ""
    return str(Path(DEFAULT_STEAM_BASE) / "6942069" / STEAM_SUFFIX)

def _fmt_dt(dt: Optional[datetime]) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d %b %Y  %H:%M")

def _wlabel(text: str, role: str = "") -> QLabel:
    l = QLabel(text)
    if role:
        l.setObjectName(role)
    l.setWordWrap(True)
    return l


# ── Worker thread ─────────────────────────────────────────────────────────────
class SyncWorker(QThread):
    log  = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def _copy(self, src: Path, dst: Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dated = datetime.fromtimestamp(src.stat().st_mtime).strftime("%d %b %Y %H:%M")
        shutil.copy2(src, dst)
        self.log.emit(f"  ✓  {src.name}  ({dated})")

    def run(self):
        cfg           = self.config
        master_dir    = Path(cfg["master_dir"])
        steam_dirs    = [Path(p) for p in cfg["steam_dirs"] if p.strip()]
        csgo_cfg_dir  = Path(cfg["csgo_cfg_dir"])
        settings_dir  = cfg["settings_direction"]
        scripts_dir   = cfg["scripts_direction"]
        cfg_files     = cfg["cfg_files"]
        sync_settings = cfg["sync_settings"]

        errors = False

        try:
            # ── GAME OPTIONS (.vcfg) ─────────────────────────────────────────
            if sync_settings and steam_dirs and settings_dir not in ("none", "skip"):
                master_steam = steam_dirs[0]

                if settings_dir == "pull":
                    self.log.emit("\n── GAME OPTIONS  ◄  Steam → Backup ──")
                    for fname in SETTINGS_FILES:
                        src = master_steam / fname
                        if src.exists():
                            self._copy(src, master_dir / fname)
                        else:
                            self.log.emit(f"  ⚠  {fname} — not in Steam account (has CS2 been run?)")

                elif settings_dir == "push":
                    self.log.emit("\n── GAME OPTIONS  ►  Backup → Steam ──")
                    for steam_path in steam_dirs:
                        steam_id = steam_path.parents[2].name
                        self.log.emit(f"\n  → {steam_id}")
                        for fname in SETTINGS_FILES:
                            src = master_dir / fname
                            if src.exists():
                                self._copy(src, steam_path / fname)
                            else:
                                self.log.emit(f"  ✘  {fname} — not in backup (run Pull first)")
                                errors = True

            # ── CFG SCRIPTS (.cfg) ───────────────────────────────────────────
            if cfg_files and scripts_dir not in ("none", "skip"):

                if scripts_dir == "pull":
                    self.log.emit("\n── CFG SCRIPTS  ◄  CS2 Folder → Backup ──")
                    for fname in cfg_files:
                        src = csgo_cfg_dir / fname
                        if src.exists():
                            self._copy(src, master_dir / fname)
                        else:
                            self.log.emit(f"  ⚠  {fname} — not found in CS2 folder")

                elif scripts_dir == "push":
                    self.log.emit("\n── CFG SCRIPTS  ►  Backup → CS2 Folder ──")
                    for fname in cfg_files:
                        src = master_dir / fname
                        if src.exists():
                            self._copy(src, csgo_cfg_dir / fname)
                        else:
                            self.log.emit(f"  ✘  {fname} — not in backup")
                            errors = True

            self.log.emit("\n✔  Done.")

        except Exception as e:
            self.log.emit(f"\n✘  Error: {e}")
            errors = True

        self.done.emit(not errors)


# ── File status row widget ─────────────────────────────────────────────────────
class FileStatusRow(QWidget):
    def __init__(self, status: FileStatus, direction: str):
        super().__init__()
        self.setFixedHeight(34)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setSpacing(6)

        s = status

        # Filename
        name = QLabel(s.name)
        name.setFixedWidth(210)
        name.setStyleSheet(f"color: {C_TEXT}; font-size: 11px;")
        lay.addWidget(name)

        # Backup chip
        lay.addWidget(self._chip(s.backup_exists, s.backup_mtime))

        # Arrow
        arrow_ch, arrow_col, tip = self._arrow_info(s, direction)
        arr = QLabel(arrow_ch)
        arr.setFixedWidth(36)
        arr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arr.setStyleSheet(f"color: {arrow_col}; font-size: 22px; font-weight: 900; background: transparent;")
        arr.setToolTip(tip)
        lay.addWidget(arr)

        # Source chip
        lay.addWidget(self._chip(s.source_exists, s.source_mtime))

        # Status pill
        pill_text, pill_fg, pill_bg = self._pill_info(s, direction)
        pill = QLabel(pill_text)
        pill.setFixedHeight(20)
        pill.setContentsMargins(8, 0, 8, 0)
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setStyleSheet(
            f"color: {pill_fg}; background: {pill_bg}; border-radius: 10px; "
            f"font-size: 10px; font-weight: bold; letter-spacing: 1px;"
        )
        lay.addWidget(pill)
        lay.addStretch()

    def _chip(self, exists: bool, mtime: Optional[datetime]) -> QLabel:
        if exists:
            text = f"● {mtime.strftime('%d %b %y') if mtime else '—'}"
            style = f"color: {C_GREEN}; font-size: 11px; min-width: 110px;"
        else:
            text = "✘  MISSING"
            style = f"color: {C_RED}; font-size: 11px; min-width: 110px; font-weight: bold;"
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _arrow_info(self, s: FileStatus, d: str) -> tuple[str, str, str]:
        if d == "pull":
            col = C_GREEN if s.source_exists else C_RED
            return "←", col, f"{s.source_label} → Backup"
        if d == "push":
            col = C_GOLD if s.backup_exists else C_RED
            return "→", col, f"Backup → {s.source_label}"
        return "—", C_DIM, "Skipped"

    def _pill_info(self, s: FileStatus, d: str) -> tuple[str, str, str]:
        if d == "skip" or d == "none":
            return "SKIP", C_DIM, C_BG2
        if d == "pull":
            if not s.source_exists:    return "NO SOURCE", C_RED,   C_RED_DIM
            if s.backup_newer:         return f"⚠ {s.age_delta_days or 0}d OLDER", C_RED, C_RED_DIM
            if not s.backup_exists:    return "WILL CREATE", C_AMBER, C_AMBER_DIM
            return "SAFE", C_GREEN, C_GREEN_DIM
        if d == "push":
            if not s.backup_exists:    return "NO BACKUP", C_RED,   C_RED_DIM
            if s.source_newer:         return f"⚠ {s.age_delta_days or 0}d OLDER", C_AMBER, C_AMBER_DIM
            if not s.source_exists:    return "WILL CREATE", C_AMBER, C_AMBER_DIM
            return "SAFE", C_GREEN, C_GREEN_DIM
        return "", C_DIM, C_BG2


# ── File Status Panel ─────────────────────────────────────────────────────────
class FileStatusPanel(QGroupBox):
    def __init__(self):
        super().__init__("FILE STATUS")
        self._rows_widget = QWidget()
        self._rows_lay = QVBoxLayout(self._rows_widget)
        self._rows_lay.setContentsMargins(0, 0, 0, 0)
        self._rows_lay.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidget(self._rows_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(80)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 14, 10, 10)

        # Column headers
        hdr = QWidget()
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(6, 0, 6, 0)
        hdr_lay.setSpacing(6)
        for text, width in [("FILE", 210), ("BACKUP", 110), ("", 36),
                             ("SOURCE", 110), ("", 0)]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {C_DIM}; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            if width:
                lbl.setFixedWidth(width)
            hdr_lay.addWidget(lbl, 0 if width else 1)
        outer.addWidget(hdr)

        sep = QFrame()
        sep.setObjectName("separator")
        outer.addWidget(sep)
        outer.addWidget(scroll)

        self._no_config_lbl = QLabel("Configure paths and file lists above, then click Refresh Status.")
        self._no_config_lbl.setStyleSheet(f"color: {C_DIM}; font-style: italic; padding: 10px;")
        self._rows_lay.addWidget(self._no_config_lbl)

    def refresh(self, statuses: list[FileStatus],
                settings_dir: str, scripts_dir: str,
                settings_files: list[str], cfg_files: list[str]):
        # Clear
        while self._rows_lay.count():
            item = self._rows_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not statuses:
            self._rows_lay.addWidget(self._no_config_lbl)
            return

        # Section header helper
        def section(title: str, subtitle: str):
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(4, 6, 4, 2)
            t = QLabel(title)
            t.setStyleSheet(f"color: {C_GOLD}; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            s = QLabel(subtitle)
            s.setStyleSheet(f"color: {C_DIM}; font-size: 10px;")
            l.addWidget(t)
            l.addWidget(s)
            l.addStretch()
            self._rows_lay.addWidget(w)

        settings_statuses = [st for st in statuses if st.name in settings_files]
        cfg_statuses       = [st for st in statuses if st.name not in settings_files]

        if settings_statuses:
            dir_label = {"pull": "← Steam → Backup",
                         "push": "→ Backup → Steam",
                         "none": "SKIPPED",
                         "skip": "SKIPPED"}.get(settings_dir, "")
            section("GAME OPTIONS  (.vcfg)", dir_label)
            for st in settings_statuses:
                st.refresh()
                row = FileStatusRow(st, settings_dir)
                self._rows_lay.addWidget(row)

        if cfg_statuses:
            dir_label = {"pull": "← CS2 Folder → Backup",
                         "push": "→ Backup → CS2 Folder",
                         "none": "SKIPPED",
                         "skip": "SKIPPED"}.get(scripts_dir, "")
            section("CFG SCRIPTS  (.cfg)", dir_label)
            for st in cfg_statuses:
                st.refresh()
                row = FileStatusRow(st, scripts_dir)
                self._rows_lay.addWidget(row)

        self._rows_lay.addStretch()


# ── Direction selector widget ─────────────────────────────────────────────────
# ── Segmented three-way toggle ────────────────────────────────────────────────
class SegmentedControl(QWidget):
    changed = pyqtSignal(str)

    _OPTS = [
        ("pull", "◄  PULL",  C_GREEN, "#0d1a10"),
        ("skip", "SKIP",     C_DIM,   C_BG2),
        ("push", "PUSH  ►",  C_GOLD,  "#1a1400"),
    ]

    def __init__(self, default: str = "push"):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._btns: dict[str, QPushButton] = {}
        n = len(self._OPTS)
        for i, (key, label, active_fg, active_bg) in enumerate(self._OPTS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            r_l = "5px" if i == 0     else "0px"
            r_r = "5px" if i == n - 1 else "0px"
            rw  = "1px" if i == n - 1 else "0px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    border-top-left-radius: {r_l}; border-bottom-left-radius: {r_l};
                    border-top-right-radius: {r_r}; border-bottom-right-radius: {r_r};
                    background: {C_BG2};
                    border: 1px solid {C_BORDER};
                    border-right-width: {rw};
                    color: {C_DIM};
                    font-size: 13px; font-weight: bold; letter-spacing: 1px;
                    min-width: 110px;
                }}
                QPushButton:checked {{
                    background: {active_bg};
                    border: 2px solid {active_fg};
                    border-right-width: 2px;
                    color: {active_fg};
                }}
            """)
            btn.clicked.connect(lambda _, k=key: self._select(k))
            self._btns[key] = btn
            lay.addWidget(btn)
        self._select(default, emit=False)

    def _select(self, key: str, emit: bool = True):
        self._current = key
        for k, btn in self._btns.items():
            btn.setChecked(k == key)
        if emit:
            self.changed.emit(key)

    def value(self) -> str:
        return self._current

    def set_value(self, key: str):
        self._select(key, emit=False)


# ── Flow control (replaces DirectionSelector) ─────────────────────────────────
class FlowControl(QGroupBox):
    changed = pyqtSignal()

    _BOX_H = 54

    def __init__(self, title: str, left_label: str, right_label: str, default: str = "push"):
        super().__init__(title)
        self._left_label  = left_label
        self._right_label = right_label
        self._build(default)

    def _build(self, default: str):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 16, 12, 10)
        outer.setSpacing(10)

        # ── Flow diagram ──
        flow = QHBoxLayout()
        flow.setSpacing(0)

        self._left_box = self._make_box(self._left_label)
        flow.addWidget(self._left_box, 3)

        self._arrow_lbl = QLabel("→")
        self._arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._arrow_lbl.setFixedWidth(90)
        self._arrow_lbl.setStyleSheet(
            f"color: {C_GOLD}; font-size: 44px; font-weight: 900; background: transparent;"
        )
        flow.addWidget(self._arrow_lbl)

        self._right_box = self._make_box(self._right_label)
        flow.addWidget(self._right_box, 3)
        outer.addLayout(flow)

        # ── Segmented control ──
        self._seg = SegmentedControl(default)
        self._seg.changed.connect(self._on_seg_changed)
        outer.addWidget(self._seg)

        # ── Recommendation ──
        self._rec_lbl = QLabel("")
        self._rec_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rec_lbl.setStyleSheet(f"color: {C_AMBER}; font-size: 11px;")
        outer.addWidget(self._rec_lbl)

        self._apply_state(default)

    def _make_box(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setFixedHeight(self._BOX_H)
        lbl.setStyleSheet(
            f"color: {C_TEXT}; background: {C_BG2}; "
            f"border: 1px solid {C_BORDER}; border-radius: 6px; "
            f"padding: 8px 14px; font-size: 12px; font-weight: bold; letter-spacing: 1px;"
        )
        return lbl

    def _on_seg_changed(self, key: str):
        self._apply_state(key)
        self.changed.emit()

    _INACTIVE = (
        "color: #6a7585; background: #1a1e28; border: 1px solid #353b4d; "
        "border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: bold; letter-spacing: 1px;"
    )
    _SKIP = (
        "color: #4a5565; background: #161820; border: 1px dashed #2a2f3d; "
        "border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: bold; letter-spacing: 1px;"
    )

    def _apply_state(self, d: str):
        if d == "pull":
            arrow, arrow_col = "←", C_GREEN
            self._left_box.setStyleSheet(
                f"color: {C_GREEN}; background: {C_GREEN_DIM}; border: 2px solid {C_GREEN}; "
                f"border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: bold; letter-spacing: 1px;"
            )
            self._right_box.setStyleSheet(self._INACTIVE)
        elif d == "push":
            arrow, arrow_col = "→", C_GOLD
            self._left_box.setStyleSheet(self._INACTIVE)
            self._right_box.setStyleSheet(
                f"color: {C_GOLD}; background: {C_GOLD_DIM}; border: 2px solid {C_GOLD}; "
                f"border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: bold; letter-spacing: 1px;"
            )
        else:  # skip
            arrow, arrow_col = "—", C_DIM
            self._left_box.setStyleSheet(self._SKIP)
            self._right_box.setStyleSheet(self._SKIP)

        self._arrow_lbl.setText(arrow)
        self._arrow_lbl.setStyleSheet(
            f"color: {arrow_col}; font-size: 44px; font-weight: 900; background: transparent;"
        )

    def direction(self) -> str:
        return self._seg.value()

    def set_direction(self, d: str):
        self._seg.set_value(d)
        self._apply_state(d)

    def set_recommendation(self, text: str, colour: str = C_AMBER):
        self._rec_lbl.setText(text)
        self._rec_lbl.setStyleSheet(f"color: {colour}; font-size: 11px;")


# ── Steam account row ─────────────────────────────────────────────────────────
ROW_TAG_WIDTH = 70
ROW_TAG_HEIGHT = 26

class SteamAccountRow(QWidget):
    removed = pyqtSignal(object)

    def __init__(self, steam_id: str = "", label: str = "", is_master: bool = False):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 3, 0, 3)
        lay.setSpacing(8)

        if is_master:
            tag = QLabel("MASTER")
            tag.setFixedSize(ROW_TAG_WIDTH, ROW_TAG_HEIGHT)
            tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tag.setStyleSheet(
                f"min-width:{ROW_TAG_WIDTH}px; max-width:{ROW_TAG_WIDTH}px;"
                f"min-height:{ROW_TAG_HEIGHT}px; max-height:{ROW_TAG_HEIGHT}px;"
                f"color:{C_GOLD}; font-size:10px; font-weight:bold; "
                f"letter-spacing:1px; border:1px solid #3a3010; "
                f"border-radius:3px; padding:0px;"
            )
            lay.addWidget(tag)
        else:
            del_btn = QPushButton("✕")
            del_btn.setObjectName("del_btn")
            del_btn.setFixedSize(ROW_TAG_WIDTH, ROW_TAG_HEIGHT)
            del_btn.clicked.connect(lambda: self.removed.emit(self))
            lay.addWidget(del_btn)

        self.id_edit = QLineEdit(steam_id)
        self.id_edit.setPlaceholderText("Steam ID  (e.g. 12345678)")
        self.id_edit.setFixedWidth(170)

        self.path_display = QLineEdit(build_steam_path(steam_id))
        self.path_display.setReadOnly(True)
        self.path_display.setStyleSheet(
            f"color: #4a5060; background: {C_BG}; border: 1px solid #1e2230;"
        )
        self.id_edit.textChanged.connect(
            lambda t: self.path_display.setText(build_steam_path(t))
        )
        lay.addWidget(self.id_edit)
        lay.addWidget(self.path_display, 1)

    def get_path(self) -> str:
        return build_steam_path(self.id_edit.text())


# ── Cfg file row ──────────────────────────────────────────────────────────────
class CfgFileRow(QWidget):
    removed = pyqtSignal(object)

    def __init__(self, filename: str = "", cfg_dir: str = ""):
        super().__init__()
        self._cfg_dir = cfg_dir
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(6)

        self.name_edit = QLineEdit(filename)
        self.name_edit.setPlaceholderText("filename.cfg  —  or use Browse")

        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("browse_btn")
        browse_btn.clicked.connect(self._browse)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("del_btn")
        del_btn.setFixedWidth(28)
        del_btn.clicked.connect(lambda: self.removed.emit(self))

        lay.addWidget(self.name_edit, 1)
        lay.addWidget(browse_btn)
        lay.addWidget(del_btn)

    def _browse(self):
        start = self._cfg_dir or str(Path.home())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .cfg file", start, "CFG files (*.cfg);;All files (*)"
        )
        if path:
            self.name_edit.setText(Path(path).name)

    def get_filename(self) -> str:
        return self.name_edit.text().strip()


# ── Setup Wizard ──────────────────────────────────────────────────────────────
class SetupWizard(QDialog):
    PAGES = ["Welcome", "Situation", "Master Account", "Extra Accounts",
             "Backup Folder", "CFG Files", "Done"]

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("CS2 Config Manager — First Time Setup")
        self.setMinimumSize(680, 580)
        self.resize(740, 620)
        self.setStyleSheet(WIZARD_STYLE)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._extra_accounts: list[QLineEdit] = []
        self._cfg_rows_wiz: list[QLineEdit]   = []
        self._situation: str = "restore"   # default
        self._build_ui()
        self._go_to(0)

    # ── Shell ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Progress bar
        self._progress_track = QFrame()
        self._progress_track.setObjectName("wiz_sep")
        self._progress_track.setFixedHeight(2)
        root.addWidget(self._progress_track)

        # Step indicator
        step_row = QHBoxLayout()
        step_row.setContentsMargins(20, 10, 20, 4)
        self._step_labels: list[QLabel] = []
        for i, name in enumerate(self.PAGES):
            lbl = QLabel(name.upper())
            lbl.setObjectName("step_indicator")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._step_labels.append(lbl)
            step_row.addWidget(lbl)
            if i < len(self.PAGES) - 1:
                dot = QLabel("·")
                dot.setObjectName("step_indicator")
                dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dot.setFixedWidth(12)
                step_row.addWidget(dot)
        root.addLayout(step_row)

        sep = QFrame(); sep.setObjectName("wiz_sep"); root.addWidget(sep)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._page_welcome())
        self._stack.addWidget(self._page_situation())
        self._stack.addWidget(self._page_master())
        self._stack.addWidget(self._page_second())
        self._stack.addWidget(self._page_backup())
        self._stack.addWidget(self._page_cfgfiles())
        self._stack.addWidget(self._page_done())
        root.addWidget(self._stack, 1)

        sep2 = QFrame(); sep2.setObjectName("wiz_sep"); root.addWidget(sep2)

        nav = QHBoxLayout()
        nav.setContentsMargins(28, 14, 28, 18)
        self._btn_back = QPushButton("← Back")
        self._btn_back.clicked.connect(self._go_back)
        self._btn_skip = QPushButton("Skip")
        self._btn_skip.clicked.connect(self._go_next)
        self._btn_next = QPushButton("Next →")
        self._btn_next.setObjectName("btn_next")
        self._btn_next.clicked.connect(self._go_next)
        nav.addWidget(self._btn_back)
        nav.addWidget(self._btn_skip)
        nav.addStretch()
        nav.addWidget(self._btn_next)
        root.addLayout(nav)
        self._current_page = 0

    # ── Pages ──────────────────────────────────────────────────────────────────
    def _page_welcome(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(16)
        lay.addWidget(_wlabel("WELCOME", "page_title"))
        lay.addWidget(_wlabel("CS2 CONFIG MANAGER — FIRST TIME SETUP", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addWidget(_wlabel(
            "This wizard will configure the app for your situation.\n\n"
            "CS2 uses two different types of files that behave differently:\n\n"
            "  •  Game Options  (.vcfg)  — video, audio, in-game settings.\n"
            "     CS2 generates these files when you configure the game.\n"
            "     You capture them ONCE from the machine you set up, then\n"
            "     restore them to every other machine or account after that.\n\n"
            "  •  CFG Scripts  (.cfg)  — your autoexec, practice scripts, binds.\n"
            "     Players often write these by themselves. They live in your\n"
            "     backup and get pushed OUT to wherever CS2 is installed.\n\n"
            "The direction of travel is different for each. The next page will\n"
            "ask which situation you're in so the app can recommend correctly."
        ))
        lay.addStretch()
        return w

    def _page_situation(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(14)
        lay.addWidget(_wlabel("WHAT ARE YOU DOING TODAY?", "page_title"))
        lay.addWidget(_wlabel("STEP 1 OF 5", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        lay.addWidget(_wlabel(
            "This helps the app pre-configure the right directions for each file type.\n"
            "You can always change them manually in the main app.",
            "field_hint"
        ))
        lay.addSpacing(12)

        self._sit_group = QButtonGroup(w)
        situations = [
            ("capture",
             "I just set up CS2 and want to SAVE my settings\n"
             "→  Pull game options into backup.  Push your scripts to the game.",
             C_GREEN),
            ("restore",
             "I'm restoring a fresh CS2 install from my existing backup\n"
             "→  Push everything from backup into the new install.",
             C_GOLD),
            ("sync",
             "I'm syncing between multiple Steam accounts on this PC\n"
             "→  Pull from master account, push to secondary accounts.",
             C_AMBER),
            ("refresh",
             "CS2 had an update — I want to refresh my backup with new settings\n"
             "→  Pull game options to capture any new settings CS2 has added.",
             "#6a9aaa"),
        ]
        for i, (key, text, colour) in enumerate(situations):
            btn = QRadioButton(text)
            btn.setObjectName("mode_btn")
            btn.setProperty("sit_key", key)
            btn.setStyleSheet(
                f"QRadioButton#mode_btn {{ color: {C_TEXT}; padding: 10px 14px; "
                f"border: 1px solid {C_BORDER}; border-radius: 4px; background: {C_BG2}; }}"
                f"QRadioButton#mode_btn:checked {{ border-color: {colour}; "
                f"color: {colour}; background: {C_BG}; }}"
            )
            if key == "restore":
                btn.setChecked(True)
            self._sit_group.addButton(btn, i)
            lay.addWidget(btn)

        lay.addStretch()
        return w

    def _page_master(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(12)
        lay.addWidget(_wlabel("MASTER STEAM ACCOUNT", "page_title"))
        lay.addWidget(_wlabel("STEP 2 OF 5", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        lay.addWidget(_wlabel("What is your main Steam user number?", "field_label"))
        lay.addWidget(_wlabel(
            f"Browse to your Steam userdata folder:\n"
            f"  {DEFAULT_STEAM_BASE}\n"
            f"You'll see folders with numeric names — your main account\n"
            f"is the one you play on most. Enter that number below.",
            "field_hint"
        ))
        lay.addSpacing(4)
        self._master_id = QLineEdit()
        self._master_id.setPlaceholderText("e.g.  6942069")
        self._master_id.setMaxLength(20)
        lay.addWidget(self._master_id)
        lay.addSpacing(8)
        self._master_path_display = QLineEdit()
        self._master_path_display.setReadOnly(True)
        self._master_path_display.setPlaceholderText("Full path will appear here as you type...")
        self._master_id.textChanged.connect(
            lambda t: self._master_path_display.setText(build_steam_path_masked(t))
        )
        lay.addWidget(self._master_path_display)
        lay.addStretch()
        return w

    def _page_second(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(12)
        lay.addWidget(_wlabel("ADDITIONAL STEAM ACCOUNTS", "page_title"))
        lay.addWidget(_wlabel("STEP 3 OF 5  (optional)", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        lay.addWidget(_wlabel(
            "Do you want to sync settings to a second Steam account on this PC?\n\n"
            "Useful if you share the PC or have a smurf account.\n"
            "If you only have one account, click Next to skip.",
            "field_hint"
        ))
        lay.addSpacing(8)
        self._extra_accounts_lay = QVBoxLayout()
        self._extra_accounts_lay.setSpacing(6)
        lay.addLayout(self._extra_accounts_lay)
        add_btn = QPushButton("+ Add an account")
        add_btn.setObjectName("btn_add")
        add_btn.clicked.connect(self._add_extra_account)
        lay.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch()
        return w

    def _add_extra_account(self):
        row = QHBoxLayout()
        edit = QLineEdit()
        edit.setPlaceholderText("Steam ID  (e.g. 6942069)")
        edit.setFixedWidth(200)
        path_disp = QLineEdit()
        path_disp.setReadOnly(True)
        path_disp.setPlaceholderText("path will appear here...")
        edit.textChanged.connect(lambda t: path_disp.setText(build_steam_path_masked(t)))
        rem = QPushButton("✕")
        rem.setObjectName("btn_remove")
        rem.setFixedWidth(32)
        row_widget = QWidget()
        row_widget.setLayout(row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(edit)
        row.addWidget(path_disp, 1)
        row.addWidget(rem)
        rem.clicked.connect(lambda: self._remove_extra_account(row_widget, edit))
        self._extra_accounts_lay.addWidget(row_widget)
        self._extra_accounts.append(edit)

    def _remove_extra_account(self, widget: QWidget, edit: QLineEdit):
        if edit in self._extra_accounts:
            self._extra_accounts.remove(edit)
        self._extra_accounts_lay.removeWidget(widget)
        widget.deleteLater()

    def _page_backup(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(12)
        lay.addWidget(_wlabel("CONFIG BACKUP FOLDER", "page_title"))
        lay.addWidget(_wlabel("STEP 4 OF 5", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        lay.addWidget(_wlabel("Where do you want to store your config backups?", "field_label"))
        lay.addWidget(_wlabel(
            "This is the folder where CS2 Config Manager keeps master copies of all\n"
            "your config files — both the game-generated .vcfg settings AND your\n"
            "hand-crafted .cfg scripts.\n\n"
            "Think of it as a safe. The app pulls the latest game settings into here,\n"
            "and pushes your scripts out from here.\n\n"
            "A cloud-synced drive (OneDrive, Dropbox, Google Drive) means your backup\n"
            "travels with you automatically to every machine you own.",
            "field_hint"
        ))
        lay.addSpacing(8)
        row = QHBoxLayout()
        self._backup_folder = QLineEdit()
        self._backup_folder.setPlaceholderText(r"e.g.  D:\Backups\CS2 Config")
        browse = QPushButton("Browse…")
        browse.setObjectName("browse_btn")
        browse.clicked.connect(self._browse_backup)
        row.addWidget(self._backup_folder, 1)
        row.addWidget(browse)
        lay.addLayout(row)
        lay.addStretch()
        return w

    def _browse_backup(self):
        d = QFileDialog.getExistingDirectory(self, "Select backup folder", self._backup_folder.text())
        if d:
            self._backup_folder.setText(d)

    def _page_cfgfiles(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(12)
        lay.addWidget(_wlabel("YOUR CFG SCRIPTS", "page_title"))
        lay.addWidget(_wlabel("STEP 5 OF 5", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        lay.addWidget(_wlabel("Which .cfg files do you want to sync?", "field_label"))
        lay.addWidget(_wlabel(
            f"These are the scripts YOU write that live in:\n"
            f"  {DEFAULT_CSGO_CFG}\n\n"
            "Common examples:\n"
            "  •  autoexec.cfg  — loads automatically when CS2 starts\n"
            "  •  prac.cfg      — practice server setup, buy binds, sv_cheats etc.\n\n"
            "Just the filename — no full path needed. These will be pushed FROM\n"
            "your backup folder INTO the CS2 game folder on this machine.",
            "field_hint"
        ))
        lay.addSpacing(8)
        self._cfg_list_wiz_lay = QVBoxLayout()
        self._cfg_list_wiz_lay.setSpacing(6)
        lay.addLayout(self._cfg_list_wiz_lay)
        self._add_cfg_row_wiz("autoexec.cfg")
        add_btn = QPushButton("+ Add another .cfg file")
        add_btn.setObjectName("btn_add")
        add_btn.clicked.connect(lambda: self._add_cfg_row_wiz(""))
        lay.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch()
        return w

    def _add_cfg_row_wiz(self, filename: str = ""):
        row = QHBoxLayout()
        edit = QLineEdit(filename)
        edit.setPlaceholderText("filename.cfg  —  or use Browse")
        browse = QPushButton("Browse…")
        browse.setObjectName("browse_btn")
        browse.clicked.connect(lambda: self._browse_cfg_wiz(edit))
        rem = QPushButton("✕")
        rem.setObjectName("btn_remove")
        rem.setFixedWidth(32)
        row_widget = QWidget()
        row_widget.setLayout(row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(edit, 1)
        row.addWidget(browse)
        row.addWidget(rem)
        rem.clicked.connect(lambda: self._remove_cfg_row_wiz(row_widget, edit))
        self._cfg_list_wiz_lay.addWidget(row_widget)
        self._cfg_rows_wiz.append(edit)

    def _browse_cfg_wiz(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .cfg file", DEFAULT_CSGO_CFG, "CFG files (*.cfg);;All files (*)"
        )
        if path:
            edit.setText(Path(path).name)

    def _remove_cfg_row_wiz(self, widget: QWidget, edit: QLineEdit):
        if edit in self._cfg_rows_wiz:
            self._cfg_rows_wiz.remove(edit)
        self._cfg_list_wiz_lay.removeWidget(widget)
        widget.deleteLater()

    def _page_done(self) -> QWidget:
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 20); lay.setSpacing(16)
        lay.addWidget(_wlabel("ALL SET", "page_title"))
        lay.addWidget(_wlabel("SETUP COMPLETE", "page_sub"))
        sep = QFrame(); sep.setObjectName("wiz_sep"); lay.addWidget(sep)
        lay.addSpacing(8)
        self._summary_label = _wlabel("", "field_hint")
        lay.addWidget(self._summary_label)
        lay.addSpacing(12)
        lay.addWidget(_wlabel(
            "Click Finish to open the main app.\n"
            "The directions have been pre-configured for your situation.\n"
            "Everything can be changed at any time in the main app.",
            "field_hint"
        ))
        lay.addStretch()
        return w

    def _update_summary(self):
        checked = self._sit_group.checkedButton()
        sit_key = checked.property("sit_key") if checked else "restore"
        sit_map = {
            "capture": "Capture my settings from this PC",
            "restore": "Restore a fresh install",
            "sync":    "Sync between accounts",
            "refresh": "Refresh backup after CS2 update",
        }
        backup = self._backup_folder.text().strip() or "(not set)"
        cfgs   = [e.text().strip() for e in self._cfg_rows_wiz if e.text().strip()]
        lines = [
            f"Situation:      {sit_map.get(sit_key, '—')}",
            f"Backup folder:  {backup}",
            f"CFG files:      {', '.join(cfgs) if cfgs else 'none'}",
        ]
        self._summary_label.setText("\n".join(lines))

    # ── Navigation ─────────────────────────────────────────────────────────────
    def _go_to(self, index: int):
        self._current_page = index
        self._stack.setCurrentIndex(index)
        total = len(self.PAGES)
        for i, lbl in enumerate(self._step_labels):
            lbl.setStyleSheet(
                f"color:{C_GOLD}; font-weight:bold;" if i == index
                else f"color:#2a3040;"
            )
        self._btn_back.setVisible(index > 0)
        is_last = index == total - 1
        self._btn_next.setText("Finish" if is_last else "Next →")
        self._btn_skip.setVisible(index == 3)  # only skip on extra accounts
        if is_last:
            self._update_summary()

    def _go_next(self):
        if self._current_page == len(self.PAGES) - 1:
            self._save_wizard()
            self.accept()
        else:
            self._go_to(self._current_page + 1)

    def _go_back(self):
        if self._current_page > 0:
            self._go_to(self._current_page - 1)

    def _situation_key(self) -> str:
        checked = self._sit_group.checkedButton()
        return checked.property("sit_key") if checked else "restore"

    # ── Save ───────────────────────────────────────────────────────────────────
    def _save_wizard(self):
        s = self.settings
        sit = self._situation_key()

        master_id = self._master_id.text().strip()
        extras    = [e.text().strip() for e in self._extra_accounts if e.text().strip()]
        accounts  = [("", master_id)] + [("", eid) for eid in extras]
        s.setValue("steam_accounts", json.dumps(accounts))

        backup = self._backup_folder.text().strip()
        if backup:
            s.setValue("master_dir", backup)

        cfgs = [e.text().strip() for e in self._cfg_rows_wiz if e.text().strip()]
        s.setValue("cfg_files", json.dumps(cfgs))

        # Pre-configure directions based on situation
        settings_dir, scripts_dir = {
            "capture": ("pull",  "push"),
            "restore": ("push",  "push"),
            "sync":    ("pull",  "push"),
            "refresh": ("pull",  "none"),
        }.get(sit, ("push", "push"))

        s.setValue("settings_direction", settings_dir)
        s.setValue("scripts_direction",  scripts_dir)
        s.setValue("wizard_done", True)


# ── Main window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS2 CONFIG MANAGER")
        self.setMinimumSize(1100, 700)
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self._steam_rows: list[SteamAccountRow] = []
        self._cfg_rows:   list[CfgFileRow]       = []
        self._build_ui()
        self._load_settings()
        self.showMaximized()
        # Auto-refresh status after paths load
        QTimer.singleShot(200, self._refresh_status)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(STYLE)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 10, 16, 10)
        root.setSpacing(8)

        # Header
        hdr_row = QHBoxLayout()
        hdr = QLabel("CS2 CONFIG MANAGER")
        hdr.setStyleSheet(f"font-size:22px; font-weight:bold; color:{C_GOLD}; letter-spacing:4px;")
        wiz_btn = QPushButton("⚙  Setup Wizard")
        wiz_btn.setStyleSheet(
            f"color:{C_DIM}; border:1px solid {C_BORDER}; padding:4px 12px; font-size:11px;"
        )
        wiz_btn.clicked.connect(self._run_wizard)
        hdr_row.addWidget(hdr)
        hdr_row.addStretch()
        hdr_row.addWidget(wiz_btn)
        root.addLayout(hdr_row)

        sep = QFrame(); sep.setObjectName("separator"); root.addWidget(sep)

        # ── Main splitter: LEFT = setup+action  |  RIGHT = log ──
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        h_splitter.setChildrenCollapsible(False)
        h_splitter.setHandleWidth(1)
        h_splitter.setStyleSheet("QSplitter::handle { background: #2a2f3d; }")

        # ── LEFT: scrollable column ──
        left_inner = QWidget()
        left_lay = QVBoxLayout(left_inner)
        left_lay.setContentsMargins(0, 4, 12, 4)
        left_lay.setSpacing(8)

        left_lay.addWidget(self._section_divider("SETUP"))
        left_lay.addWidget(self._build_paths_panel())
        left_lay.addWidget(self._build_accounts_panel())
        left_lay.addWidget(self._build_cfg_panel())

        left_lay.addWidget(self._section_divider("SYNC"))
        left_lay.addWidget(self._build_directions_panel())
        left_lay.addWidget(self._build_status_panel(), 1)
        left_lay.addWidget(self._build_run_panel())

        left_scroll = QScrollArea()
        left_scroll.setWidget(left_inner)
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h_splitter.addWidget(left_scroll)

        # ── RIGHT: log only ──
        h_splitter.addWidget(self._build_log_panel())

        h_splitter.setStretchFactor(0, 2)
        h_splitter.setStretchFactor(1, 1)
        h_splitter.setSizes([980, 380])

        root.addWidget(h_splitter, 1)

    def _build_paths_panel(self) -> QGroupBox:
        box = QGroupBox("FOLDERS")
        lay = QVBoxLayout(box)
        lay.setSpacing(6)

        def field_label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setFixedWidth(90)
            lbl.setStyleSheet(f"color: {C_DIM}; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            return lbl

        row1 = QHBoxLayout(); row1.setSpacing(8)
        self.master_dir_edit = QLineEdit()
        self.master_dir_edit.setPlaceholderText("Your backup folder — where all files are kept safe")
        self.master_dir_edit.textChanged.connect(self._on_path_changed)
        b1 = QPushButton("Browse…"); b1.setObjectName("browse_btn")
        b1.clicked.connect(lambda: self._browse_to(self.master_dir_edit))
        row1.addWidget(field_label("BACKUP"))
        row1.addWidget(self.master_dir_edit, 1)
        row1.addWidget(b1)
        lay.addLayout(row1)

        row2 = QHBoxLayout(); row2.setSpacing(8)
        self.csgo_cfg_edit = QLineEdit(DEFAULT_CSGO_CFG)
        self.csgo_cfg_edit.textChanged.connect(self._on_path_changed)
        b2 = QPushButton("Browse…"); b2.setObjectName("browse_btn")
        b2.clicked.connect(lambda: self._browse_to(self.csgo_cfg_edit))
        row2.addWidget(field_label("CS2 GAME"))
        row2.addWidget(self.csgo_cfg_edit, 1)
        row2.addWidget(b2)
        lay.addLayout(row2)

        return box

    def _build_accounts_panel(self) -> QGroupBox:
        box = QGroupBox("STEAM ACCOUNTS  (FIRST = MAIN ACCOUNT)")
        outer = QVBoxLayout(box)
        self._steam_list_lay = QVBoxLayout()
        self._steam_list_lay.setSpacing(2)
        outer.addLayout(self._steam_list_lay)
        add_sa = QPushButton("+ Add Steam Account")
        add_sa.clicked.connect(lambda: self._add_steam_row())
        outer.addWidget(add_sa, alignment=Qt.AlignmentFlag.AlignLeft)

        # Settings sync toggle
        self.sync_settings_chk = QCheckBox(
            "Keep game options identical across all accounts?  (.vcfg — video · audio · in-game settings)"
        )
        self.sync_settings_chk.setChecked(True)
        self.sync_settings_chk.stateChanged.connect(self._on_path_changed)
        outer.addSpacing(6)
        outer.addWidget(self.sync_settings_chk)
        return box

    def _build_cfg_panel(self) -> QGroupBox:
        box = QGroupBox("CFG SCRIPTS  (autoexec · prac · bot binds)")
        outer = QVBoxLayout(box)
        self._cfg_list_lay = QVBoxLayout()
        self._cfg_list_lay.setSpacing(2)
        outer.addLayout(self._cfg_list_lay)
        add_cfg = QPushButton("+ Add .cfg file")
        add_cfg.clicked.connect(lambda: self._add_cfg_row(""))
        outer.addWidget(add_cfg, alignment=Qt.AlignmentFlag.AlignLeft)
        return box

    def _section_divider(self, title: str) -> QWidget:
        w = QWidget()
        w.setFixedHeight(24)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        line_l = QFrame(); line_l.setObjectName("separator")
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color: {C_DIM}; font-size: 10px; font-weight: bold; letter-spacing: 2px;"
        )
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        line_r = QFrame(); line_r.setObjectName("separator")
        lay.addWidget(line_l, 1)
        lay.addWidget(lbl)
        lay.addWidget(line_r, 1)
        return w

    def _build_directions_panel(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self._settings_dir = FlowControl(
            "GAME OPTIONS",
            left_label="BACKUP FOLDER",
            right_label="STEAM ACCOUNTS",
            default="push",
        )
        self._settings_dir.changed.connect(self._refresh_status)

        self._scripts_dir = FlowControl(
            "CFG SCRIPTS",
            left_label="BACKUP FOLDER",
            right_label="CS2 GAME FOLDER",
            default="push",
        )
        self._scripts_dir.changed.connect(self._refresh_status)

        lay.addWidget(self._settings_dir, 1)
        lay.addWidget(self._scripts_dir, 1)
        return w

    def _build_status_panel(self) -> FileStatusPanel:
        self._status_panel = FileStatusPanel()
        return self._status_panel

    def _build_run_panel(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        refresh_btn = QPushButton("↻  Refresh Status")
        refresh_btn.clicked.connect(self._refresh_status)
        refresh_btn.setToolTip("Re-scan all files and update the status panel")

        self.run_btn = QPushButton("▶  RUN SYNC")
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setFixedHeight(36)
        self.run_btn.setFixedWidth(180)
        self.run_btn.clicked.connect(self._run_sync)

        lay.addWidget(refresh_btn)
        lay.addStretch()
        lay.addWidget(self.run_btn)
        return w

    def _build_log_panel(self) -> QGroupBox:
        box = QGroupBox("LOG")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(10, 14, 10, 10)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        lay.addWidget(self.log_view)
        return box

    # ── Row helpers ────────────────────────────────────────────────────────────
    def _add_steam_row(self, steam_id="", label="", is_master=False):
        row = SteamAccountRow(steam_id, label, is_master)
        row.removed.connect(self._remove_steam_row)
        self._steam_rows.append(row)
        self._steam_list_lay.addWidget(row)

    def _remove_steam_row(self, row):
        if row in self._steam_rows:
            self._steam_rows.remove(row)
            self._steam_list_lay.removeWidget(row)
            row.deleteLater()
        QTimer.singleShot(50, self._refresh_status)

    def _add_cfg_row(self, filename=""):
        row = CfgFileRow(filename, cfg_dir=self.csgo_cfg_edit.text().strip())
        row.removed.connect(self._remove_cfg_row)
        self._cfg_rows.append(row)
        self._cfg_list_lay.addWidget(row)

    def _remove_cfg_row(self, row):
        if row in self._cfg_rows:
            self._cfg_rows.remove(row)
            self._cfg_list_lay.removeWidget(row)
            row.deleteLater()
        QTimer.singleShot(50, self._refresh_status)

    # ── Browse ────────────────────────────────────────────────────────────────
    def _browse_to(self, edit: QLineEdit):
        d = QFileDialog.getExistingDirectory(self, "Select folder", edit.text())
        if d:
            edit.setText(d)

    def _on_path_changed(self):
        QTimer.singleShot(300, self._refresh_status)

    # ── File status refresh ────────────────────────────────────────────────────
    def _build_file_statuses(self) -> list[FileStatus]:
        master_dir   = Path(self.master_dir_edit.text().strip())
        csgo_cfg_dir = Path(self.csgo_cfg_edit.text().strip())
        steam_dirs   = [Path(r.get_path()) for r in self._steam_rows if r.get_path()]
        master_steam = steam_dirs[0] if steam_dirs else None

        statuses = []

        if self.sync_settings_chk.isChecked() and master_steam:
            for fname in SETTINGS_FILES:
                statuses.append(FileStatus(
                    name         = fname,
                    backup_path  = master_dir / fname,
                    source_path  = master_steam / fname,
                    source_label = f"Steam ({master_steam.parents[2].name})",
                ))

        for row in self._cfg_rows:
            fname = row.get_filename()
            if fname:
                statuses.append(FileStatus(
                    name         = fname,
                    backup_path  = master_dir / fname,
                    source_path  = csgo_cfg_dir / fname,
                    source_label = "CS2 game folder",
                ))

        return statuses

    def _compute_recommendations(self, statuses: list[FileStatus]):
        settings_statuses = [s for s in statuses if s.name in SETTINGS_FILES]
        cfg_statuses      = [s for s in statuses if s.name not in SETTINGS_FILES]

        # Settings recommendation
        if settings_statuses:
            any_backup_missing = any(not s.backup_exists for s in settings_statuses)
            any_source_newer   = any(s.source_newer for s in settings_statuses)
            any_backup_newer   = any(s.backup_newer for s in settings_statuses)

            if any_backup_missing:
                self._settings_dir.set_recommendation(
                    "PULL — no backup yet. Capture your game options first.",
                    C_AMBER
                )
            elif any_source_newer:
                days = max((s.age_delta_days or 0) for s in settings_statuses if s.source_newer)
                self._settings_dir.set_recommendation(
                    f"Consider PULL — game files are {days}d newer (CS2 may have added new settings).",
                    C_AMBER
                )
            elif any_backup_newer:
                self._settings_dir.set_recommendation(
                    "PUSH looks good — your backup is newer than the game files.",
                    C_GREEN
                )
            else:
                self._settings_dir.set_recommendation(
                    "Files are in sync — no action needed unless restoring.",
                    C_GREEN
                )
        else:
            self._settings_dir.set_recommendation("", C_DIM)

        # Scripts recommendation
        if cfg_statuses:
            any_backup_missing = any(not s.backup_exists for s in cfg_statuses)
            all_backup_present = all(s.backup_exists for s in cfg_statuses)

            if any_backup_missing:
                self._scripts_dir.set_recommendation(
                    "Some scripts are NOT IN BACKUP — add them to the backup folder before pushing.",
                    C_RED
                )
            elif all_backup_present:
                self._scripts_dir.set_recommendation(
                    "PUSH — all scripts are in backup and ready to deploy.",
                    C_GREEN
                )
            else:
                self._scripts_dir.set_recommendation("", C_DIM)
        else:
            self._scripts_dir.set_recommendation("", C_DIM)

    def _refresh_status(self):
        statuses = self._build_file_statuses()
        for s in statuses:
            s.refresh()

        self._compute_recommendations(statuses)

        self._status_panel.refresh(
            statuses         = statuses,
            settings_dir     = self._settings_dir.direction(),
            scripts_dir      = self._scripts_dir.direction(),
            settings_files   = SETTINGS_FILES,
            cfg_files        = [r.get_filename() for r in self._cfg_rows if r.get_filename()],
        )

    # ── Wizard ────────────────────────────────────────────────────────────────
    def _run_wizard(self):
        wiz = SetupWizard(self.settings, parent=self)
        if wiz.exec() == QDialog.DialogCode.Accepted:
            for row in list(self._steam_rows):
                self._remove_steam_row(row)
            for row in list(self._cfg_rows):
                self._remove_cfg_row(row)
            self._load_settings()

    # ── Overwrite safety check ────────────────────────────────────────────────
    def _check_overwrites(self, statuses: list[FileStatus],
                           settings_dir: str, scripts_dir: str) -> bool:
        """
        Returns True (safe to proceed) or False (user cancelled).
        Warns for any case where we're about to overwrite a NEWER file with an OLDER one.
        """
        warnings = []

        for s in statuses:
            direction = settings_dir if s.name in SETTINGS_FILES else scripts_dir
            if direction in ("none", "skip"):
                continue

            if direction == "pull" and s.backup_exists and s.backup_newer:
                days = s.age_delta_days or 0
                warnings.append(
                    f"  {s.name}\n"
                    f"    Backup:  {_fmt_dt(s.backup_mtime)}  ← NEWER (by {days} days)\n"
                    f"    Source:  {_fmt_dt(s.source_mtime)}\n"
                    f"    Pulling this will OVERWRITE your newer backup with older data."
                )
            elif direction == "push" and s.source_exists and s.source_newer:
                days = s.age_delta_days or 0
                warnings.append(
                    f"  {s.name}\n"
                    f"    Source:  {_fmt_dt(s.source_mtime)}  ← NEWER (by {days} days)\n"
                    f"    Backup:  {_fmt_dt(s.backup_mtime)}\n"
                    f"    Pushing this will OVERWRITE newer game/steam files with older backup data.\n"
                    f"    (If CS2 added new settings, those will be lost.)"
                )

        if not warnings:
            return True

        msg = QMessageBox(self)
        msg.setWindowTitle("Overwrite Warning")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(
            f"<b>You are about to overwrite {len(warnings)} newer file(s) with older data.</b><br><br>"
            "This means some files are being copied in a direction that goes backwards in time.<br>"
            "Review the details below before proceeding."
        )
        details = "\n\n".join(warnings)
        msg.setDetailedText(details)
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        msg.button(QMessageBox.StandardButton.Ok).setText("Proceed Anyway")
        msg.button(QMessageBox.StandardButton.Cancel).setText("Cancel — Let Me Review")
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.setStyleSheet(STYLE)

        return msg.exec() == QMessageBox.StandardButton.Ok

    # ── Sync ──────────────────────────────────────────────────────────────────
    def _run_sync(self):
        if hasattr(self, "_worker") and self._worker.isRunning():
            return

        settings_dir = self._settings_dir.direction()
        scripts_dir  = self._scripts_dir.direction()

        if settings_dir in ("none", "skip") and scripts_dir in ("none", "skip"):
            QMessageBox.warning(self, "Nothing to do",
                                "Both file types are set to Skip.\n"
                                "Select a direction for at least one.")
            return

        master_dir = self.master_dir_edit.text().strip()
        if not master_dir:
            QMessageBox.warning(self, "No backup folder",
                                "Set the Config Backup Folder first.")
            return

        bad_ids = [r.id_edit.text().strip() for r in self._steam_rows
                   if r.id_edit.text().strip() and not is_valid_steam_id(r.id_edit.text())]
        if bad_ids:
            QMessageBox.warning(self, "Invalid Steam ID",
                                f"Steam IDs must be numbers only:\n{', '.join(bad_ids)}")
            return

        # Build statuses and check for overwrite risks
        statuses = self._build_file_statuses()
        for s in statuses:
            s.refresh()

        if not self._check_overwrites(statuses, settings_dir, scripts_dir):
            return

        steam_dirs = [r.get_path() for r in self._steam_rows if r.get_path()]
        cfg_files  = [r.get_filename() for r in self._cfg_rows if r.get_filename()]

        self._save_settings()
        self.log_view.clear()
        self.log_view.append(
            f"[{datetime.now():%H:%M:%S}]  Starting sync\n"
            f"  Game options:  {settings_dir.upper() if settings_dir not in ('none','skip') else 'SKIPPED'}\n"
            f"  CFG scripts:   {scripts_dir.upper() if scripts_dir not in ('none','skip') else 'SKIPPED'}\n"
        )

        config = {
            "master_dir":         master_dir,
            "steam_dirs":         steam_dirs,
            "csgo_cfg_dir":       self.csgo_cfg_edit.text().strip(),
            "settings_direction": settings_dir,
            "scripts_direction":  scripts_dir,
            "sync_settings":      self.sync_settings_chk.isChecked(),
            "cfg_files":          cfg_files,
        }

        self.run_btn.setEnabled(False)
        self._worker = SyncWorker(config)
        self._worker.log.connect(self.log_view.append)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, success: bool):
        self.run_btn.setEnabled(True)
        msg = "— All operations completed successfully —" if success else "— Completed with errors (see above) —"
        self.log_view.append(f"\n{msg}")
        QTimer.singleShot(500, self._refresh_status)

    # ── Persistence ───────────────────────────────────────────────────────────
    def _save_settings(self):
        s = self.settings
        s.setValue("master_dir",         self.master_dir_edit.text())
        s.setValue("csgo_cfg_dir",       self.csgo_cfg_edit.text())
        s.setValue("sync_settings",      self.sync_settings_chk.isChecked())
        s.setValue("settings_direction", self._settings_dir.direction())
        s.setValue("scripts_direction",  self._scripts_dir.direction())

        steam = [("", r.id_edit.text()) for r in self._steam_rows]
        s.setValue("steam_accounts", json.dumps(steam))

        cfgs = [r.get_filename() for r in self._cfg_rows]
        s.setValue("cfg_files", json.dumps(cfgs))

    def _load_settings(self):
        s = self.settings
        self.master_dir_edit.setText(s.value("master_dir", ""))
        self.csgo_cfg_edit.setText(s.value("csgo_cfg_dir", DEFAULT_CSGO_CFG))
        self.sync_settings_chk.setChecked(s.value("sync_settings", True, type=bool))

        settings_dir = s.value("settings_direction", "push")
        scripts_dir  = s.value("scripts_direction",  "push")
        self._settings_dir.set_direction(settings_dir)
        self._scripts_dir.set_direction(scripts_dir)

        steam_raw = s.value("steam_accounts", "[]")
        try:
            steam_list = json.loads(steam_raw)
        except Exception:
            steam_list = []

        if not steam_list:
            self._add_steam_row("", "Master", is_master=True)
            self._add_steam_row("", "Secondary")
        else:
            for i, (label, steam_id) in enumerate(steam_list):
                self._add_steam_row(steam_id, label, is_master=(i == 0))

        cfg_raw = s.value("cfg_files", "[]")
        try:
            cfg_list = json.loads(cfg_raw)
        except Exception:
            cfg_list = []

        for f in cfg_list:
            self._add_cfg_row(f)

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    settings = QSettings(ORG_NAME, APP_NAME)
    if not settings.value("wizard_done", False, type=bool):
        wizard = SetupWizard(settings)
        if wizard.exec() == QDialog.DialogCode.Rejected:
            sys.exit(0)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
