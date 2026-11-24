# Panduan Pengguna DayPlan TUI

## Memulai

Jalankan `dayplan` (atau `python main.py`). Layar pertama adalah **Dashboard**.
Navigasi utama ada di sidebar kiri; Anda juga bisa memakai tombol huruf
`D`, `T`, `C`, `P`, `F`, `S`, dan `?`.

Tekan `Q` untuk keluar. Data tersimpan otomatis di SQLite, jadi tidak ada tombol
"Save" untuk tugas — perubahan langsung tersimpan.

## Menambahkan tugas

1. Di **Tasks** atau **Dashboard**, tekan `Ctrl+N`.
2. Isi judul (wajib). Kolom lain opsional:
   - **Deadline** — `YYYY-MM-DD`, jam deadline opsional `HH:MM`.
   - **Mulai/Selesai kerja** — `YYYY-MM-DDTHH:MM` (jadwal pengerjaan, berbeda dengan deadline).
   - **Estimasi** — durasi dalam menit.
   - **Proyek** dan **Tag** — tag dipisahkan koma.
3. Tekan `Ctrl+S` untuk menyimpan atau `Esc` untuk membatalkan.

Tugas baru berstatus **Inbox** dan prioritas sesuai pengaturan default (Medium).

## Mengelola tugas

Di **Tasks**, gunakan kolom pencarian dan tiga dropdown filter (status, prioritas,
urutan). Urutan yang tersedia: Terbaru, Deadline, Prioritas.

| Aksi | Cara |
|---|---|
| Edit | Pilih baris, tekan `E` |
| Selesai / batal selesai | Pilih baris, tekan `Space` |
| Hapus | Pilih baris, tekan `Delete`, lalu konfirmasi |
| Cari | `Ctrl+F`, lalu ketik |
| Refresh | `R` |

Tugas selesai mendapat `completed_at`; menekan `Space` lagi mengembalikannya ke
status Todo dan menghapus `completed_at`. Tugas terlambat ditandai `!` pada kolom
Deadline tetapi tidak dihapus atau diselesaikan otomatis.

## Kalender

Halaman **Calendar** punya tiga tab:

- **Bulanan** — indikator `◆` = kegiatan, `●` = tugas/deadline, `!` = ada yang terlambat.
  Tanggal hari ini ditandai terang.
- **Harian** — agenda tanggal terpilih, menggabungkan kegiatan, jadwal kerja, dan
  deadline dalam urutan waktu.
- **Agenda** — ringkasan tujuh hari ke depan.

Navigasi: `[` dan `]` mengganti bulan, `G` kembali ke hari ini. Untuk memilih
tanggal, ketik `YYYY-MM-DD` pada kolom tanggal lalu tekan `Enter` atau tombol
**Pilih**; tab Harian akan otomatis terbuka.

Tekan `N` untuk membuat kegiatan kalender. Isi waktu mulai dan selesai dengan
format `YYYY-MM-DDTHH:MM`. Kegiatan berbeda dari tugas: kegiatan adalah komitmen
waktu (misalnya kuliah 08.00–10.00), sedangkan tugas adalah pekerjaan yang harus
diselesaikan. Keduanya tetap tampil di kalender.

## Proyek

Di **Projects**, tekan `Ctrl+N` untuk membuat proyek. Pilih baris untuk melihat
tugas di dalamnya. Menghapus proyek **tidak** menghapus tugas — tugas tersebut
tetap ada tanpa proyek.

## Focus Mode

Pilih tugas (opsional), lalu tekan **Mulai**. Timer menghitung mundur dan sesi
dicatat saat selesai. Tombol **Jeda**, **Lanjut**, **Ulang**, dan **Selesai**
tersedia. Durasi diatur di Settings; nilai awal 25/5/15 menit. Focus Mode bersifat
opsional dan tidak memengaruhi tugas maupun kalender.

## Pengaturan

- **Tema** — Dark / Light.
- **Format tanggal / jam** — dipakai di Dashboard, Calendar, dan Statistics.
- **Zona waktu** — nama IANA seperti `Asia/Jakarta`; kosongkan untuk zona lokal.
- **Prioritas default** — dipakai saat membuat tugas baru.
- **Durasi Pomodoro** — dalam menit, harus lebih dari nol.
- **Data & Backup** — ekspor seluruh database ke JSON dan pulihkan kembali.

## Format data

Semua tanggal memakai ISO 8601. Tanggal saja: `YYYY-MM-DD`. Waktu:
`YYYY-MM-DDTHH:MM`. Cap waktu (`created_at`, `updated_at`, `completed_at`)
menggunakan UTC dengan offset.

## Tips

- Jika terminal lebih kecil dari ~80×24, perlebar jendela; panel dapat tumpang tindih.
- Hampir semua aksi bisa dilakukan tanpa mouse; footer menampilkan shortcut utama.
- `?` membuka daftar lengkap shortcut kapan saja.
