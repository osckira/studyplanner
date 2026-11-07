import sqlite3
from datetime import datetime, date

DATABASE = 'study_planner.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabel Jadwal Belajar Mingguan/Harian (Rutin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,     -- Senin, Selasa, dst.
            start_time TEXT NOT NULL,       -- HH:MM
            end_time TEXT NOT NULL,         -- HH:MM
            subject TEXT NOT NULL,
            topic TEXT,
            notes TEXT
        )
    ''')
    
    # Tabel Tugas & Deadline
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            deadline DATE NOT NULL,
            priority TEXT DEFAULT 'Sedang', -- Rendah, Sedang, Tinggi
            status TEXT DEFAULT 'Belum Selesai', -- Belum Selesai, Selesai
            completed_at TIMESTAMP
        )
    ''')
    
    # Tabel Target Harian
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_date DATE NOT NULL,
            title TEXT NOT NULL,
            target_minutes INTEGER DEFAULT 60,
            status TEXT DEFAULT 'Belum Selesai',
            completed_at TIMESTAMP
        )
    ''')
    
    # Tabel Log Sesi Belajar (Untuk Rekap Progress Mingguan)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL,
            subject TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Tambahkan contoh data jika tabel masih kosong
    cursor.execute("SELECT COUNT(*) FROM study_schedules")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO study_schedules (day_of_week, start_time, end_time, subject, topic, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            ('Senin', '08:00', '10:00', 'Matematika Dasar', 'Kalkulus & Limit', 'Mengerjakan latihan bab 3'),
            ('Senin', '13:30', '15:00', 'Pemrograman Python', 'Struktur Data & Algoritma', 'Latihan List, Dict, dan OOP'),
            ('Selasa', '09:00', '11:00', 'Bahasa Inggris', 'TOEFL Preparation', 'Reading comprehension & vocab'),
            ('Rabu', '10:00', '12:00', 'Basis Data', 'SQL Relational & Normalisasi', 'Desain ERD dan tabel'),
            ('Kamis', '14:00', '16:00', 'Jaringan Komputer', 'Model OSI & TCP/IP', 'Review subnetting'),
            ('Jumat', '08:30', '10:30', 'Kecerdasan Buatan', 'Machine Learning Dasar', 'Supervised Learning'),
            ('Sabtu', '09:00', '11:00', 'Review & Proyek Mandiri', 'Portfolio Project', 'Selesaikan mini web app')
        ])
        
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        today_str = date.today().strftime('%Y-%m-%d')
        cursor.executemany('''
            INSERT INTO tasks (title, subject, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Resume Bab 4 Limit Fungsi', 'Matematika Dasar', today_str, 'Tinggi', 'Belum Selesai'),
            ('Tugas Mini Project Flask', 'Pemrograman Python', today_str, 'Tinggi', 'Belum Selesai'),
            ('Latihan Essay Argumen 300 kata', 'Bahasa Inggris', today_str, 'Sedang', 'Belum Selesai')
        ])
        
    cursor.execute("SELECT COUNT(*) FROM daily_goals")
    if cursor.fetchone()[0] == 0:
        today_str = date.today().strftime('%Y-%m-%d')
        cursor.executemany('''
            INSERT INTO daily_goals (goal_date, title, target_minutes, status)
            VALUES (?, ?, ?, ?)
        ''', [
            (today_str, 'Membaca materi Python OOP', 60, 'Selesai'),
            (today_str, 'Menyelesaikan 10 soal latihan kalkulus', 90, 'Belum Selesai'),
            (today_str, 'Latihan listening bahasa Inggris 2 sesi', 45, 'Belum Selesai')
        ])
        
    cursor.execute("SELECT COUNT(*) FROM study_logs")
    if cursor.fetchone()[0] == 0:
        today_str = date.today().strftime('%Y-%m-%d')
        cursor.executemany('''
            INSERT INTO study_logs (log_date, subject, duration_minutes, notes)
            VALUES (?, ?, ?, ?)
        ''', [
            (today_str, 'Pemrograman Python', 75, 'Belajar Flask dan routing SQLite'),
            (today_str, 'Matematika Dasar', 60, 'Membahas turunan dan diferensial')
        ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database SQLite berhasil diinisialisasi!")
