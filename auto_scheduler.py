"""
Auto Scheduler — Advanced Feature #3
=====================================
Runs automatically in background:
  - 09:30 AM → Send WhatsApp absent alerts
  - 06:00 PM → Daily summary email
  - Every Friday 5PM → Weekly report
  - 1st of month → Monthly PDF report

HOW TO ADD TO YOUR APP:
    In main.py, after starting the login window, add:
        from auto_scheduler import AttendanceScheduler
        scheduler = AttendanceScheduler(db)
        scheduler.start()          # starts background thread
        # When app closes:
        scheduler.stop()

    OR add a Scheduler control panel to Settings page:
        from auto_scheduler import SchedulerPanel
        SchedulerPanel(self.content, self.db)

INSTALL (run once):
    pip install schedule
"""

import threading
import time
import logging
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

from database import DatabaseManager

BG       = '#FDFAF6'
BROWN    = '#6B2D0E'
BROWN_LT = '#C4783A'
GOLD     = '#D4A017'
WHITE    = '#FFFFFF'
DARK     = '#2C1A0E'
MUTED    = '#9E7B5A'
SUCCESS  = '#2E7D32'
INFO     = '#1565C0'
WARNING  = '#E65100'
DANGER   = '#C62828'
FONT     = 'Segoe UI'

# ── Logging setup ────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SCHEDULER] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('scheduler')


class AttendanceScheduler:
    """
    Background scheduler that runs daily tasks automatically.
    Uses Python's built-in time module — no external library needed.
    """

    def __init__(self, db: DatabaseManager):
        self.db           = db
        self._thread      = None
        self._running     = False
        self._last_run    = {}   # task_name → date last ran
        self.log_callback = None  # optional GUI callback: fn(msg, color)

        # ── Task schedule config ──────────────────────────
        # Format: (hour, minute) for daily tasks
        self.schedule = {
            'absent_alerts':    (9, 30),    # 9:30 AM every day
            'daily_summary':    (18, 0),    # 6:00 PM every day
            'weekly_report':    (17, 0),    # 5:00 PM every Friday (weekday=4)
            'monthly_report':   (8, 0),     # 8:00 AM on 1st of each month
            'auto_mark_absent': (11, 15),   # 11:15 AM — mark missing students absent
        }

        # ── Enable/disable individual tasks ──────────────
        self.enabled = {
            'absent_alerts':    True,
            'daily_summary':    False,   # needs email setup
            'weekly_report':    False,   # needs email setup
            'monthly_report':   False,   # needs fpdf2
            'auto_mark_absent': True,
        }

    def start(self):
        """Start the scheduler in a background daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        log.info("Scheduler started.")
        self._notify("🟢 Scheduler started", SUCCESS)

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        log.info("Scheduler stopped.")
        self._notify("⏹ Scheduler stopped", MUTED)

    def _notify(self, msg, color=None):
        """Send message to GUI if callback set."""
        if self.log_callback:
            try:
                self.log_callback(msg, color or DARK)
            except Exception:
                pass

    # ════════════════════════════════════════════════════
    #  MAIN LOOP
    # ════════════════════════════════════════════════════
    def _run_loop(self):
        """Check every minute if any task should run."""
        log.info("Scheduler loop running...")
        while self._running:
            now = datetime.now()
            today = date.today()

            for task_name, (h, m) in self.schedule.items():
                if not self.enabled.get(task_name, False):
                    continue

                # Check if it's time
                if now.hour == h and now.minute == m:
                    last = self._last_run.get(task_name)

                    # Skip if already ran today (or this week/month for weekly/monthly)
                    if task_name == 'weekly_report':
                        if now.weekday() != 4:   # Friday only
                            continue
                        if last and last >= today - timedelta(days=1):
                            continue
                    elif task_name == 'monthly_report':
                        if today.day != 1:        # 1st of month only
                            continue
                        if last and last.month == today.month:
                            continue
                    else:
                        if last and last >= today:
                            continue

                    # Run the task
                    self._last_run[task_name] = today
                    threading.Thread(
                        target=self._run_task,
                        args=(task_name,),
                        daemon=True
                    ).start()

            time.sleep(60)   # check every minute

    def _run_task(self, task_name):
        """Execute a specific task safely."""
        log.info(f"Running task: {task_name}")
        self._notify(f"⏳ Running: {task_name}...", WARNING)
        try:
            if task_name == 'absent_alerts':
                self._task_absent_alerts()
            elif task_name == 'daily_summary':
                self._task_daily_summary()
            elif task_name == 'weekly_report':
                self._task_weekly_report()
            elif task_name == 'monthly_report':
                self._task_monthly_report()
            elif task_name == 'auto_mark_absent':
                self._task_auto_mark_absent()
        except Exception as e:
            log.error(f"Task {task_name} failed: {e}")
            self._notify(f"❌ {task_name} failed: {e}", DANGER)

    # ════════════════════════════════════════════════════
    #  TASKS
    # ════════════════════════════════════════════════════

    def _task_absent_alerts(self):
        """Send WhatsApp/SMS to parents of absent students."""
        try:
            from notification_service import notify_absent
        except ImportError:
            log.warning("notification_service not found — skipping absent alerts")
            return

        today     = date.today()
        today_str = today.strftime('%d-%m-%Y')

        try:
            all_students  = self.db.get_all_students()
            today_records = self.db.get_attendance(filter_date=str(today))
        except Exception as e:
            log.error(f"DB error in absent_alerts: {e}")
            return

        present_ids = {
            r['student_id'] for r in today_records
            if r.get('status') in ('present', 'late')
        }

        absent_students = [
            s for s in all_students
            if s.get('status') == 'active'
            and s['student_id'] not in present_ids
        ]

        sent = failed = skipped = 0
        for s in absent_students:
            phone = s.get('phone', '')
            if not phone:
                skipped += 1
                continue
            try:
                ok, _ = notify_absent(
                    s['full_name'], s['student_id'],
                    s.get('class_name', ''), phone, today_str
                )
                if ok:
                    sent += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        msg = f"📲 Absent alerts: {sent} sent, {failed} failed, {skipped} skipped"
        log.info(msg)
        self._notify(msg, SUCCESS if failed == 0 else WARNING)

        try:
            self.db.log_activity("AUTO_SCHEDULER", "system",
                                  f"Absent alerts sent: {sent}, failed: {failed}")
        except Exception:
            pass

    def _task_auto_mark_absent(self):
        """Mark all students not present by 11:15 AM as absent."""
        today = date.today()
        try:
            all_students  = self.db.get_all_students()
            today_records = self.db.get_attendance(filter_date=str(today))
        except Exception as e:
            log.error(f"DB error in auto_mark_absent: {e}")
            return

        # Collect student_ids that already have ANY record today (present, late, or absent)
        present_ids = {r['student_id'] for r in today_records}
        marked = 0

        for s in all_students:
            if s.get('status') != 'active':
                continue
            if s['student_id'] not in present_ids:
                try:
                    # Use direct DB insert to force 'absent' status
                    # (mark_attendance auto-converts to 'late' after 9 AM)
                    self._force_mark_absent(
                        s['student_id'], s['full_name'],
                        s.get('class_name', '')
                    )
                    marked += 1
                except Exception:
                    pass

        msg = f"✅ Auto-marked {marked} students as absent"
        log.info(msg)
        self._notify(msg, INFO)

        try:
            self.db.log_activity("AUTO_SCHEDULER", "system",
                                  f"Auto-marked absent: {marked} students")
        except Exception:
            pass

    def _force_mark_absent(self, student_id, full_name, class_name):
        """
        Directly insert absent record, bypassing the late-time check in mark_attendance().
        Called by auto_mark_absent so students are marked ABSENT (not late).
        """
        from datetime import date, datetime
        import mysql.connector
        today = date.today()
        now   = datetime.now().strftime('%H:%M:%S')
        conn  = self.db.get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO attendance
                   (student_id, full_name, class_name, date, time_in, status)
                   VALUES (%s, %s, %s, %s, %s, 'absent')
                   ON DUPLICATE KEY UPDATE status=IF(status='absent','absent',status)""",
                (student_id, full_name, class_name, today, now)
            )
            conn.commit()
            return True
        except Exception as e:
            log.warning(f"force_mark_absent error for {student_id}: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def _task_daily_summary(self):
        """Send daily attendance summary email."""
        # Requires email_service.py (Email feature)
        try:
            from email_service import send_daily_summary_email
            send_daily_summary_email(self.db)
            self._notify("📧 Daily summary email sent", SUCCESS)
        except ImportError:
            log.info("email_service not available — skipping daily summary")
        except Exception as e:
            log.error(f"Daily summary failed: {e}")

    def _task_weekly_report(self):
        """Generate and email weekly attendance report."""
        try:
            from email_service import send_weekly_report_email
            send_weekly_report_email(self.db)
            self._notify("📧 Weekly report email sent", SUCCESS)
        except ImportError:
            log.info("email_service not available — skipping weekly report")
        except Exception as e:
            log.error(f"Weekly report failed: {e}")

    def _task_monthly_report(self):
        """Generate monthly PDF and save to reports folder."""
        try:
            import os
            reports_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'monthly_reports'
            )
            os.makedirs(reports_dir, exist_ok=True)

            today    = date.today()
            # Report for previous month
            first_day = today.replace(day=1) - timedelta(days=1)
            month_str = first_day.strftime('%Y-%m')
            fname     = os.path.join(reports_dir, f"monthly_{month_str}.pdf")

            from pdf_reports import PDFReportGenerator
            gen = PDFReportGenerator(self.db)
            gen._generate_monthly(fname, month_str, None)

            msg = f"📄 Monthly PDF generated: {fname}"
            log.info(msg)
            self._notify(msg, SUCCESS)
        except Exception as e:
            log.error(f"Monthly report failed: {e}")
            self._notify(f"❌ Monthly report failed: {e}", DANGER)

    # ════════════════════════════════════════════════════
    #  MANUAL TRIGGER
    # ════════════════════════════════════════════════════
    def run_now(self, task_name):
        """Manually trigger a task immediately."""
        threading.Thread(
            target=self._run_task,
            args=(task_name,),
            daemon=True
        ).start()


# ════════════════════════════════════════════════════════
#  SCHEDULER CONTROL PANEL (add to Settings page)
# ════════════════════════════════════════════════════════
class SchedulerPanel:
    """
    GUI control panel for the scheduler.
    Add to your Settings page:
        from auto_scheduler import SchedulerPanel
        SchedulerPanel(content_frame, db)
    """

    def __init__(self, parent, db: DatabaseManager, scheduler=None):
        self.parent    = parent
        self.db        = db
        self.scheduler = scheduler or AttendanceScheduler(db)
        self.scheduler.log_callback = self._add_log
        self._build_ui()

    def _build_ui(self):
        # Header
        tk.Frame(self.parent, bg=BROWN, height=4).pack(fill='x')
        hdr = tk.Frame(self.parent, bg=BROWN)
        hdr.pack(fill='x')
        tk.Label(hdr, text="⏰  Auto Scheduler",
                 font=(FONT, 13, 'bold'), bg=BROWN, fg=WHITE).pack(side='left', padx=15, pady=10)

        self.status_badge = tk.Label(hdr, text="● STOPPED",
                                      font=(FONT, 10, 'bold'),
                                      bg=BROWN, fg='#FF8888')
        self.status_badge.pack(side='right', padx=15)

        body = tk.Frame(self.parent, bg=BG)
        body.pack(fill='both', expand=True, padx=20, pady=12)

        # Start/Stop buttons
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill='x', pady=(0, 12))
        tk.Button(btn_row, text="▶  Start Scheduler",
                  command=self._start, bg=SUCCESS, fg=WHITE,
                  font=(FONT, 11, 'bold'), relief='flat',
                  padx=16, pady=8, cursor='hand2').pack(side='left', padx=(0, 8))
        tk.Button(btn_row, text="⏹  Stop Scheduler",
                  command=self._stop, bg=DANGER, fg=WHITE,
                  font=(FONT, 11, 'bold'), relief='flat',
                  padx=16, pady=8, cursor='hand2').pack(side='left')

        # Schedule table
        tk.Label(body, text="Scheduled Tasks:",
                 font=(FONT, 11, 'bold'), bg=BG, fg=BROWN).pack(anchor='w', pady=(8, 4))

        tasks_frame = tk.Frame(body, bg=WHITE, relief='solid', bd=1)
        tasks_frame.pack(fill='x', pady=(0, 12))

        # Header row
        hdr_row = tk.Frame(tasks_frame, bg=BROWN)
        hdr_row.pack(fill='x')
        for txt, w in [("Task", 25), ("Schedule", 15), ("Enabled", 8), ("Run Now", 10)]:
            tk.Label(hdr_row, text=txt, font=(FONT, 9, 'bold'),
                     bg=BROWN, fg=WHITE, width=w, anchor='w').pack(side='left', padx=6, pady=4)

        task_info = [
            ('Absent Alerts',    'absent_alerts',    'Every day 9:30 AM'),
            ('Auto Mark Absent', 'auto_mark_absent', 'Every day 11:15 AM'),
            ('Daily Summary',    'daily_summary',    'Every day 6:00 PM'),
            ('Weekly Report',    'weekly_report',    'Every Friday 5:00 PM'),
            ('Monthly Report',   'monthly_report',   'Every 1st at 8:00 AM'),
        ]
        self._vars = {}
        for i, (label, key, schedule) in enumerate(task_info):
            bg = '#FFF8F0' if i % 2 == 0 else WHITE
            row = tk.Frame(tasks_frame, bg=bg)
            row.pack(fill='x')

            tk.Label(row, text=label.replace('_', ' ').title(),
                     font=(FONT, 10), bg=bg, fg=DARK,
                     width=25, anchor='w').pack(side='left', padx=6, pady=5)
            tk.Label(row, text=schedule,
                     font=(FONT, 9), bg=bg, fg=MUTED,
                     width=15, anchor='w').pack(side='left', padx=6)

            var = tk.BooleanVar(value=self.scheduler.enabled.get(key, False))
            self._vars[key] = var

            def _toggle(k=key, v=var):
                self.scheduler.enabled[k] = v.get()

            tk.Checkbutton(row, variable=var, command=_toggle,
                           bg=bg, activebackground=bg,
                           cursor='hand2').pack(side='left', padx=20)

            tk.Button(row, text="▶ Run",
                      command=lambda k=key: self._run_now(k),
                      bg=INFO, fg=WHITE, font=(FONT, 9),
                      relief='flat', padx=8, pady=2,
                      cursor='hand2').pack(side='left', padx=8)

        # Log box
        tk.Label(body, text="Scheduler Log:",
                 font=(FONT, 11, 'bold'), bg=BG, fg=BROWN).pack(anchor='w', pady=(8, 4))

        log_frame = tk.Frame(body, bg='#1a1a1a', relief='flat')
        log_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(log_frame, bg='#1a1a1a', fg='#00FF88',
                                 font=('Consolas', 9), height=10,
                                 relief='flat', state='disabled',
                                 insertbackground='white')
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.log_text.pack(fill='both', expand=True, padx=4, pady=4)

        self._add_log("Scheduler ready. Click ▶ Start to begin.", SUCCESS)

    def _add_log(self, msg, color=None):
        """Add message to log box."""
        try:
            ts  = datetime.now().strftime('%H:%M:%S')
            txt = f"[{ts}] {msg}\n"
            self.log_text.config(state='normal')
            self.log_text.insert('end', txt)
            self.log_text.see('end')
            self.log_text.config(state='disabled')
        except Exception:
            pass

    def _start(self):
        self.scheduler.start()
        self.status_badge.config(text="● RUNNING", fg='#88FF88')

    def _stop(self):
        self.scheduler.stop()
        self.status_badge.config(text="● STOPPED", fg='#FF8888')

    def _run_now(self, task_name):
        self._add_log(f"⚡ Manually running: {task_name}...", WARNING)
        self.scheduler.run_now(task_name)