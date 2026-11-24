# DayPlan TUI

Aplikasi manajemen produktivitas berbasis terminal (Python + Textual + SQLite).
Offline-first, keyboard-driven, dan menyimpan seluruh data secara lokal.

## Fitur

- **Dashboard** — statistik aktif/selesai/terlambat, agenda hari ini, deadline mendatang, progres proyek.
- **Tasks** — CRUD lengkap, status (Inbox/Todo/In Progress/Waiting/Done/Archived), prioritas, deadline, jadwal kerja, tag, pencarian, filter, dan pengurutan.
- **Calendar** — tampilan Bulanan, Harian, dan Agenda; kegiatan kalender terpisah dari tugas; penanda deadline, jadwal, dan keterlambatan.
- **Projects** — pengelompokan tugas, progres per proyek; menghapus proyek tidak menghapus tugasnya.
- **Focus Mode** — timer Pomodoro (fokus/istirahat) dengan riwayat sesi tersimpan.
- **Statistics** — ringkasan, penyelesaian 7 hari, progres proyek.
- **Settings** — tema dark/light, format tanggal/jam, zona waktu, prioritas default, durasi Pomodoro, ekspor/impor JSON.
- **Help** — daftar seluruh shortcut keyboard.

## Kebutuhan

- Python 3.11 atau lebih baru
- Textual 8.x, Rich 13+

## Instalasi

```bash
pip install -e .
```

Untuk development:

```bash
pip install -e ".[dev]"
```

## Menjalankan

```bash
dayplan
```

Atau langsung dari folder proyek:

```bash
python main.py
```

## Database

Database dibuat otomatis saat pertama kali dijalankan. Secara default berada di:

- Windows: `%USERPROFILE%\.dayplan\dayplan.db`
- Linux/macOS: `~/.dayplan/dayplan.db`

Lokasi bisa diubah lewat environment variable `DAYPLAN_DATA_DIR`.

## Shortcut keyboard

| Tombol | Fungsi |
|---|---|
| `Q` | Keluar |
| `?` | Help |
| `Ctrl+N` | Tugas/proyek baru |
| `Ctrl+F` | Fokus ke pencarian |
| `Ctrl+S` | Simpan form/pengaturan |
| `D`, `T`, `C`, `P`, `F`, `S` | Dashboard, Tasks, Calendar, Projects, Focus, Settings |
| `Space` | Tandai selesai (Tasks) |
| `E` | Edit data terpilih |
| `Delete` | Hapus dengan konfirmasi |
| `R` | Refresh |
| `[` / `]` | Bulan sebelumnya / berikutnya (Calendar) |
| `G` | Kembali ke hari ini (Calendar) |
| `Esc` | Kembali / tutup modal |
| Arrow keys | Navigasi tabel |

Tombol huruf tidak memindahkan halaman saat fokus berada di kolom input.

## Backup

Settings → **Export JSON** menulis seluruh tabel ke satu file JSON.
**Import JSON** memulihkan backup tersebut (termasuk tugas, proyek, kegiatan, dan pengaturan).

## Pengujian

```bash
pytest
```

Tes mencakup database & migrasi, CRUD tugas, proyek, kalender & agenda,
statistik, backup/impor, fokus, serta alur UI headless dengan Textual Pilot
(pada ukuran terminal 120×40 dan 80×24).

## Struktur

```
src/dayplan/
  app.py            # aplikasi + container service
  config.py         # pengaturan tersimpan
  database/         # koneksi, schema, migrasi
  models/           # struktur data
  repositories/     # seluruh query SQLite
  services/         # business logic
  screens/          # halaman Textual
  widgets/          # komponen UI reusable
  styles/           # Textual CSS
  utils/            # tanggal, format, validasi
docs/user-guide.md  # panduan pemakaian lengkap
```

UI tidak pernah menjalankan query SQLite secara langsung; semua lewat service dan repository.

## Status pengembangan

MVP selesai: Dashboard, Todo CRUD, status/prioritas, deadline & scheduling,
Monthly/Daily/Agenda calendar, Calendar Events, Project Management dasar,
SQLite persistence, search/filter, ekspor JSON, navigasi keyboard, tema dark/light.

Fitur di luar MVP yang sudah ada: Focus Mode, Statistics, impor JSON.

Belum ada (disengaja, sesuai ruang lingkup MVP): weekly calendar, recurring
tasks, subtasks, in-app deadline alerts, cloud sync, integrasi kalender eksternal.
