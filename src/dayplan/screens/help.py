"""In-app help, shortcut reference and about box."""

from __future__ import annotations

from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static

from dayplan import __version__
from dayplan.screens.base import BaseScreen

SHORTCUTS = [
    ("Q", "Keluar aplikasi"),
    ("?", "Bantuan ini"),
    ("Ctrl+N", "Tugas / proyek baru"),
    ("Ctrl+F", "Cari tugas"),
    ("Ctrl+S", "Simpan pengaturan / form"),
    ("D / T / C / P / F / S", "Pindah halaman"),
    ("Enter", "Pilih atau buka"),
    ("Space", "Tandai selesai (Tasks)"),
    ("E", "Edit data terpilih"),
    ("Delete", "Hapus data terpilih"),
    ("Esc", "Kembali / tutup modal"),
    ("[ / ]", "Bulan sebelumnya / berikutnya"),
    ("G", "Kembali ke hari ini (Calendar)"),
    ("R", "Refresh daftar / statistik"),
    ("Arrow Keys", "Navigasi elemen"),
]


class HelpScreen(BaseScreen):
    TITLE = "Help & Shortcuts"

    def build_content(self) -> ComposeResult:
        with VerticalScroll() as container:
            with Vertical(classes="panel"):
                yield Static("DAYPLAN TUI", classes="panel-title")
                yield Static(
                    f"Versi {__version__} • Python + Textual + SQLite\n"
                    "Productivity manager offline-first untuk terminal.\n"
                    "Data disimpan lokal di dayplan.db — tidak memerlukan internet."
                )
            with Vertical(classes="panel"):
                yield Static("KEYBOARD SHORTCUTS", classes="panel-title")
                yield Static(self._shortcuts_table())
        return container

    @staticmethod
    def _shortcuts_table() -> Table:
        table = Table(box=box.SIMPLE, show_header=True, expand=True)
        table.add_column("Tombol", width=26)
        table.add_column("Fungsi")
        for key, description in SHORTCUTS:
            table.add_row(key, description)
        return table
