from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime, date, timedelta
import calendar
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'study_planner_super_secret_key_2026'

DAYS_OF_WEEK = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

def get_indonesian_day_name(d):
    idx = d.weekday() # 0 = Monday
    return DAYS_OF_WEEK[idx]

@app.route('/')
def index():
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    today_day_name = get_indonesian_day_name(today)

    conn = get_db()
    cursor = conn.cursor()

    # 1. Jadwal belajar hari ini
    cursor.execute('''
        SELECT * FROM study_schedules
        WHERE day_of_week = ?
        ORDER BY start_time ASC
    ''', (today_day_name,))
    today_schedules = cursor.fetchall()

    # 2. Target Harian Hari Ini
    cursor.execute('''
        SELECT * FROM daily_goals
        WHERE goal_date = ?
        ORDER BY id DESC
    ''', (today_str,))
    today_goals = cursor.fetchall()

    # 3. Tugas mendatang & aktif
    cursor.execute('''
        SELECT * FROM tasks
        ORDER BY CASE status WHEN 'Belum Selesai' THEN 1 ELSE 2 END,
                 deadline ASC
    ''')
    all_tasks = cursor.fetchall()

    # Hitung Tugas & Target Selesai
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t['status'] == 'Selesai')
    task_progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    total_goals = len(today_goals)
    completed_goals = sum(1 for g in today_goals if g['status'] == 'Selesai')
    goal_progress = int((completed_goals / total_goals * 100)) if total_goals > 0 else 0

    # 4. Pengingat Mendekati Deadline (Deadline hari ini atau besok dan belum selesai)
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM tasks
        WHERE status = 'Belum Selesai' AND deadline IN (?, ?)
        ORDER BY deadline ASC
    ''', (today_str, tomorrow_str))
    urgent_tasks = cursor.fetchall()

    # 5. Progress Belajar Mingguan (7 hari terakhir)
    start_week = today - timedelta(days=6)
    cursor.execute('''
        SELECT log_date, SUM(duration_minutes) as total_min
        FROM study_logs
        WHERE log_date BETWEEN ? AND ?
        GROUP BY log_date
    ''', (start_week.strftime('%Y-%m-%d'), today_str))
    weekly_logs_map = {row['log_date']: row['total_min'] for row in cursor.fetchall()}

    weekly_progress = []
    total_week_minutes = 0
    for i in range(7):
        cur_d = start_week + timedelta(days=i)
        cur_d_str = cur_d.strftime('%Y-%m-%d')
        mins = weekly_logs_map.get(cur_d_str, 0)
        total_week_minutes += mins
        weekly_progress.append({
            'date': cur_d_str,
            'day_name': get_indonesian_day_name(cur_d),
            'short_date': cur_d.strftime('%d/%m'),
            'minutes': mins,
            'hours': round(mins / 60.0, 1),
            'is_today': cur_d == today
        })

    # Subjek teratas mingguan
    cursor.execute('''
        SELECT subject, SUM(duration_minutes) as total_min
        FROM study_logs
        WHERE log_date BETWEEN ? AND ?
        GROUP BY subject
        ORDER BY total_min DESC
    ''', (start_week.strftime('%Y-%m-%d'), today_str))
    top_subjects = cursor.fetchall()

    conn.close()

    return render_template(
        'index.html',
        today_str=today_str,
        today_day_name=today_day_name,
        today_formatted=today.strftime('%d %B %Y'),
        today_schedules=today_schedules,
        today_goals=today_goals,
        all_tasks=all_tasks,
        urgent_tasks=urgent_tasks,
        task_progress=task_progress,
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
        goal_progress=goal_progress,
        completed_goals=completed_goals,
        total_goals=total_goals,
        weekly_progress=weekly_progress,
        total_week_hours=round(total_week_minutes / 60.0, 1),
        top_subjects=top_subjects,
        days_of_week=DAYS_OF_WEEK
    )

# --- JADWAL BELAJAR ---
@app.route('/schedules')
def schedules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM study_schedules ORDER BY start_time ASC')
    rows = cursor.fetchall()
    
    # Kelompokkan jadwal per hari
    schedules_by_day = {day: [] for day in DAYS_OF_WEEK}
    for row in rows:
        if row['day_of_week'] in schedules_by_day:
            schedules_by_day[row['day_of_week']].append(row)
            
    conn.close()
    return render_template('schedules.html', schedules_by_day=schedules_by_day, days_of_week=DAYS_OF_WEEK)

@app.route('/schedules/add', methods=['POST'])
def add_schedule():
    day_of_week = request.form.get('day_of_week')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    notes = request.form.get('notes')

    if not day_of_week or not start_time or not end_time or not subject:
        flash('Mohon lengkapi data jadwal yang wajib diisi.', 'warning')
        return redirect(request.referrer or url_for('schedules'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_schedules (day_of_week, start_time, end_time, subject, topic, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (day_of_week, start_time, end_time, subject, topic, notes))
    conn.commit()
    conn.close()
    flash('Jadwal belajar berhasil ditambahkan!', 'success')
    return redirect(request.referrer or url_for('schedules'))

@app.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM study_schedules WHERE id = ?', (schedule_id,))
    conn.commit()
    conn.close()
    flash('Jadwal belajar berhasil dihapus.', 'info')
    return redirect(request.referrer or url_for('schedules'))

# --- TUGAS & DEADLINE ---
@app.route('/tasks')
def tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks
        ORDER BY CASE status WHEN 'Belum Selesai' THEN 1 ELSE 2 END,
                 deadline ASC
    ''')
    all_tasks = cursor.fetchall()
    conn.close()
    return render_template('tasks.html', tasks=all_tasks, today=date.today().strftime('%Y-%m-%d'))

@app.route('/tasks/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    subject = request.form.get('subject')
    deadline = request.form.get('deadline')
    priority = request.form.get('priority', 'Sedang')

    if not title or not deadline:
        flash('Judul tugas dan batas waktu (deadline) wajib diisi.', 'warning')
        return redirect(request.referrer or url_for('tasks'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, subject, deadline, priority, status)
        VALUES (?, ?, ?, ?, 'Belum Selesai')
    ''', (title, subject, deadline, priority))
    conn.commit()
    conn.close()
    flash('Tugas baru berhasil disimpan!', 'success')
    return redirect(request.referrer or url_for('tasks'))

@app.route('/tasks/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    if task:
        new_status = 'Selesai' if task['status'] == 'Belum Selesai' else 'Belum Selesai'
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status == 'Selesai' else None
        cursor.execute('UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?', (new_status, completed_at, task_id))
        conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('tasks'))

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    flash('Tugas telah dihapus.', 'info')
    return redirect(request.referrer or url_for('tasks'))

# --- TARGET HARIAN ---
@app.route('/goals/add', methods=['POST'])
def add_goal():
    title = request.form.get('title')
    target_minutes = request.form.get('target_minutes', 60, type=int)
    goal_date = request.form.get('goal_date', date.today().strftime('%Y-%m-%d'))

    if not title:
        flash('Judul target tidak boleh kosong.', 'warning')
        return redirect(request.referrer or url_for('index'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daily_goals (goal_date, title, target_minutes, status)
        VALUES (?, ?, ?, 'Belum Selesai')
    ''', (goal_date, title, target_minutes))
    conn.commit()
    conn.close()
    flash('Target harian berhasil ditambahkan!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/goals/toggle/<int:goal_id>', methods=['POST'])
def toggle_goal(goal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM daily_goals WHERE id = ?', (goal_id,))
    goal = cursor.fetchone()
    if goal:
        new_status = 'Selesai' if goal['status'] == 'Belum Selesai' else 'Belum Selesai'
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status == 'Selesai' else None
        cursor.execute('UPDATE daily_goals SET status = ?, completed_at = ? WHERE id = ?', (new_status, completed_at, goal_id))
        conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/goals/delete/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM daily_goals WHERE id = ?', (goal_id,))
    conn.commit()
    conn.close()
    flash('Target berhasil dihapus.', 'info')
    return redirect(request.referrer or url_for('index'))

# --- LOG PROGRESS / CATAT SESI BELAJAR ---
@app.route('/logs/add', methods=['POST'])
def add_log():
    log_date = request.form.get('log_date', date.today().strftime('%Y-%m-%d'))
    subject = request.form.get('subject')
    duration_minutes = request.form.get('duration_minutes', type=int)
    notes = request.form.get('notes')

    if not subject or not duration_minutes:
        flash('Subjek dan durasi belajar wajib diisi.', 'warning')
        return redirect(request.referrer or url_for('index'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_logs (log_date, subject, duration_minutes, notes)
        VALUES (?, ?, ?, ?)
    ''', (log_date, subject, duration_minutes, notes))
    conn.commit()
    conn.close()
    flash(f'Log belajar {duration_minutes} menit berhasil dicatat!', 'success')
    return redirect(request.referrer or url_for('index'))

# --- KALENDER & PENGINGAT ---
@app.route('/calendar')
def view_calendar():
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # Ambil semua tugas di bulan tersebut
    first_day = date(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks
        WHERE deadline BETWEEN ? AND ?
        ORDER BY deadline ASC
    ''', (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))
    tasks_in_month = cursor.fetchall()

    tasks_by_date = {}
    for t in tasks_in_month:
        d = t['deadline']
        if d not in tasks_by_date:
            tasks_by_date[d] = []
        tasks_by_date[d].append(t)

    # Ambil info jadwal rutin mingguan
    cursor.execute('SELECT * FROM study_schedules ORDER BY start_time ASC')
    all_schedules = cursor.fetchall()
    schedules_by_day = {day: [] for day in DAYS_OF_WEEK}
    for s in all_schedules:
        schedules_by_day[s['day_of_week']].append(s)

    conn.close()

    cal = calendar.Calendar(firstweekday=0) # Mulai dari Senin
    month_weeks = cal.monthdatescalendar(year, month)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_names_id = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    return render_template(
        'calendar.html',
        year=year,
        month=month,
        month_name=month_names_id[month],
        month_weeks=month_weeks,
        today=date.today(),
        tasks_by_date=tasks_by_date,
        schedules_by_day=schedules_by_day,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        days_of_week=DAYS_OF_WEEK,
        get_indonesian_day_name=get_indonesian_day_name
    )

if __name__ == '__main__':
    init_db()
    print("Menjalankan Study Planner...")
    print("Akses lokal: http://127.0.0.1:5000")
    print("Akses kawan (1 jaringan Wi-Fi): http://10.233.32.171:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
