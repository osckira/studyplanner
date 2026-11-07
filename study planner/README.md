# Study Planner Web App (Python & Flask)

Aplikasi web Study Planner berbasis Python dan SQLite untuk menyusun dan memantau rencana belajar, tugas, dan target harian.

## Fitur Utama

1. **Jadwal Belajar Per Hari dan Jam**:
   - Pengaturan jadwal rutin mingguan (Senin - Minggu) lengkap dengan jam mulai, jam selesai, mata kuliah/subjek, modul topik, dan catatan.
2. **Daftar Tugas & Deadline**:
   - Pencatatan tugas, mata kuliah, batas waktu (deadline), dan tingkat prioritas (Tinggi, Sedang, Rendah).
3. **Status Selesai / Belum Selesai**:
   - One-click toggle status untuk menandai tugas dan target harian yang sudah tuntas atau belum tuntas.
4. **Pengingat & Kalender Sederhana**:
   - Kalender bulanan yang menampilkan tanggal penting, deadline tugas (dengan indikator status), jadwal rutin per hari, serta banner alert otomatis untuk tugas yang mendekati deadline (hari ini / besok).
5. **Progress Belajar Mingguan**:
   - Pencatatan sesi belajar (jam/menit) dan visualisasi rekap grafik aktivitas belajar selama 7 hari terakhir beserta ringkasan subjek yang paling banyak dipelajari.

## Struktur File

```
study planner/
├── app.py                # Server web Flask & routing aplikasi
├── database.py           # Inisialisasi & skema database SQLite (study_planner.db)
├── requirements.txt      # Dependensi Python (Flask)
├── README.md             # Panduan penggunaan
└── templates/
    ├── base.html         # Template layout utama & navbar (Tailwind CSS & Lucide Icons)
    ├── index.html        # Dashboard utama (Progress mingguan, target harian, jadwal hari ini)
    ├── schedules.html    # Halaman manajemen jadwal per hari dan jam
    ├── tasks.html        # Halaman daftar tugas, deadline & filter status
    └── calendar.html     # Kalender bulanan interaktif & penanda deadline
```

## Cara Menjalankan

1. Buka terminal di folder project ini:
   ```bash
   cd "c:\Users\Louiz Antony\.vscode\study planner"
   ```

2. Jalankan aplikasi web:
   ```bash
   py app.py
   ```
   *(atau `python app.py`)*

3. Buka browser dan kunjungi:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)
