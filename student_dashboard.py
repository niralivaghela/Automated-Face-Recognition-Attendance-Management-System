"""
Student Dashboard — Vanita Vishram Women's University
======================================================
Student self-service portal:
  🏠  Home Dashboard  — summary cards + today's status
  📅  Daily           — search any single day
  📆  Weekly          — 7-day calendar strip with nav
  🗓️  Monthly         — full calendar grid with nav
  📝  My Results      — subject marks, grades, GPA
  👤  My Profile      — personal info + all summaries
  💰  Fee Details     — fee status, payment history
  📥  Download PDF    — full student report PDF
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import calendar
from datetime import datetime, date, timedelta
from PIL import Image, ImageTk
from database import DatabaseManager

BG       = '#FDFAF6'
BROWN    = '#6B2D0E'
BROWN2   = '#8B3A10'
BROWN_LT = '#C4783A'
CREAM    = '#FFF8F0'
GOLD     = '#D4A017'
WHITE    = '#FFFFFF'
DARK     = '#2C1A0E'
MUTED    = '#9E7B5A'
SUCCESS  = '#2E7D32'
INFO     = '#1565C0'
WARNING  = '#E65100'
DANGER   = '#C62828'
PURPLE   = '#6A1B9A'
STUDENT  = '#2E7D32'
FONT     = 'Segoe UI'

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'college_logo.png')


class StudentDashboard:
    def __init__(self, root, student_info):
        self.root    = root
        self.student = student_info
        self.sid     = student_info['student_id']
        self.db      = DatabaseManager()
        self._logo_img = None
        self._week_offset  = 0
        self._month_year   = date.today().year
        self._month_month  = date.today().month
        self._load_summary()
        self.setup_window()
        self.build_layout()
        self.nav_click('home', self.show_home)

    def _load_summary(self):
        try:
            self._summary = self.db.get_student_attendance_summary(self.sid)
        except Exception:
            self._summary = {'records':[], 'total':0, 'present':0, 'absent':0, 'percentage':0.0}

    def setup_window(self):
        name = self.student.get('full_name', 'Student')
        self.root.title(f"Student Portal — {name} | Vanita Vishram Women's University")
        self.root.geometry("1280x760")
        self.root.configure(bg=BG)
        try: self.root.state('zoomed')
        except Exception: pass

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=BROWN, width=235)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        try:
            img = Image.open(LOGO_PATH).resize((65, 65), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.sidebar, image=self._logo_img, bg=BROWN).pack(pady=(16, 3))
        except Exception:
            tk.Label(self.sidebar, text="🎓", font=(FONT+' Emoji', 30), bg=BROWN, fg=GOLD).pack(pady=(16, 3))

        tk.Label(self.sidebar, text="Vanita Vishram", font=(FONT, 11, 'bold'), bg=BROWN, fg=WHITE).pack()
        tk.Label(self.sidebar, text="Women's University", font=(FONT, 8), bg=BROWN, fg=GOLD).pack()

        badge = tk.Frame(self.sidebar, bg=STUDENT)
        badge.pack(fill='x', padx=10, pady=6)
        tk.Label(badge, text="🟢  STUDENT PORTAL", font=(FONT, 9, 'bold'), bg=STUDENT, fg=WHITE).pack(pady=4)

        name = self.student.get('full_name', '')
        cls  = self.student.get('class_name', '')
        tk.Label(self.sidebar, text=name, font=(FONT, 10, 'bold'), bg=BROWN, fg=WHITE, wraplength=200).pack(pady=(4, 0))
        tk.Label(self.sidebar, text=f"ID: {self.sid}" + (f"  |  {cls}" if cls else ""),
                 font=(FONT, 8), bg=BROWN, fg=GOLD).pack()

        tk.Frame(self.sidebar, bg=GOLD, height=2).pack(fill='x', padx=12, pady=6)

        pct = self._summary.get('percentage', 0)
        pc  = SUCCESS if pct >= 75 else (WARNING if pct >= 60 else DANGER)
        pill = tk.Frame(self.sidebar, bg=pc)
        pill.pack(fill='x', padx=12, pady=2)
        tk.Label(pill, text=f"📊  Attendance: {pct}%", font=(FONT, 10, 'bold'), bg=pc, fg=WHITE).pack(pady=5)

        if pct < 75:
            wf = tk.Frame(self.sidebar, bg='#7B3F00')
            wf.pack(fill='x', padx=12, pady=2)
            tk.Label(wf, text=f"⚠  Below 75% — {round(75-pct,1)}% shortage",
                     font=(FONT, 8, 'bold'), bg='#7B3F00', fg='#FFD54F', wraplength=200).pack(pady=4)

        tk.Frame(self.sidebar, bg=GOLD, height=1).pack(fill='x', padx=12, pady=5)

        self.nav_buttons = {}
        navs = [
            ("🏠  Home Dashboard",   'home',    self.show_home),
            ("📅  Daily Attendance", 'daily',   self.show_daily),
            ("📆  Weekly View",      'weekly',  self.show_weekly),
            ("🗓️  Monthly View",     'monthly', self.show_monthly),
            ("📝  My Results",       'results', self.show_results),
            ("👤  My Profile",       'profile', self.show_profile),
            ("💰  Fee Details",      'fees',    self.show_fees),
        ]
        for label, key, cmd in navs:
            btn = tk.Button(self.sidebar, text=label,
                            command=lambda c=cmd, k=key: self.nav_click(k, c),
                            bg=BROWN, fg=WHITE, font=(FONT, 10),
                            relief='flat', anchor='w', padx=16,
                            cursor='hand2', activebackground=BROWN_LT, activeforeground=WHITE)
            btn.pack(fill='x', pady=1, ipady=6)
            self.nav_buttons[key] = btn

        tk.Frame(self.sidebar, bg=GOLD, height=1).pack(fill='x', padx=12, pady=6)
        tk.Button(self.sidebar, text="📥  Download Full PDF",
                  command=self._download_pdf,
                  bg=PURPLE, fg=WHITE, font=(FONT, 10, 'bold'),
                  relief='flat', cursor='hand2').pack(fill='x', padx=12, pady=3, ipady=6)

        tk.Frame(self.sidebar, bg=GOLD, height=2).pack(fill='x', padx=12, pady=4, side='bottom')
        tk.Button(self.sidebar, text="🚪  Logout", command=self.logout,
                  bg=DANGER, fg=WHITE, font=(FONT, 11, 'bold'),
                  relief='flat', cursor='hand2').pack(side='bottom', fill='x', padx=12, pady=8)

        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(side='left', fill='both', expand=True)

        topbar = tk.Frame(self.main_frame, bg=WHITE, height=55)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=STUDENT, width=4).pack(side='left', fill='y')
        self.page_title = tk.Label(topbar, text="Home", font=(FONT, 16, 'bold'), bg=WHITE, fg=BROWN)
        self.page_title.pack(side='left', padx=20, pady=12)
        tk.Label(topbar, text="🟢 STUDENT", font=(FONT, 9, 'bold'), bg=STUDENT, fg=WHITE,
                 padx=10, pady=3).pack(side='right', padx=15, pady=13)
        self.clock_lbl = tk.Label(topbar, font=(FONT, 10), bg=WHITE, fg=MUTED)
        self.clock_lbl.pack(side='right', padx=10)
        tk.Frame(topbar, bg=GOLD, height=2).pack(side='bottom', fill='x')
        self.update_clock()

        self.content = tk.Frame(self.main_frame, bg=BG)
        self.content.pack(fill='both', expand=True, padx=18, pady=15)

    def update_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime("%A, %d %B %Y  |  %I:%M:%S %p"))
        self.root.after(1000, self.update_clock)

    def nav_click(self, key, cmd):
        for k, b in self.nav_buttons.items():
            b.config(bg=BROWN, fg=WHITE, font=(FONT, 10))
        if key in self.nav_buttons:
            self.nav_buttons[key].config(bg=BROWN_LT, fg=WHITE, font=(FONT, 10, 'bold'))
        cmd()

    def clear_content(self):
        for w in self.content.winfo_children(): w.destroy()

    # ── helpers ───────────────────────────────────────────
    def _stat_card(self, parent, title, value, icon, color):
        card = tk.Frame(parent, bg=WHITE)
        card.pack(side='left', expand=True, fill='both', padx=5, pady=4)
        tk.Frame(card, bg=color, height=5).pack(fill='x')
        tk.Label(card, text=icon, font=(FONT+' Emoji', 20), bg=WHITE).pack(pady=(10, 2))
        tk.Label(card, text=str(value), font=(FONT, 22, 'bold'), bg=WHITE, fg=color).pack()
        tk.Label(card, text=title, font=(FONT, 9), bg=WHITE, fg=MUTED).pack(pady=(2, 10))

    def _section_hdr(self, text, color=BROWN):
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill='x', pady=(10, 5))
        tk.Frame(row, bg=color, width=5, height=22).pack(side='left', fill='y')
        tk.Label(row, text=f"  {text}", font=(FONT, 13, 'bold'), bg=BG, fg=BROWN).pack(side='left')

    def _tree(self, parent, cols, widths, height=10):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("S.Treeview", background=WHITE, foreground=DARK,
                        rowheight=26, fieldbackground=WHITE, font=(FONT, 10))
        style.configure("S.Treeview.Heading", background=BROWN,
                        foreground=WHITE, font=(FONT, 10, 'bold'))
        style.map("S.Treeview", background=[('selected', BROWN_LT)])
        tree = ttk.Treeview(frame, columns=cols, show='headings',
                             style="S.Treeview", height=height)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')
        sy = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side='right', fill='y')
        sx.pack(side='bottom', fill='x')
        tree.pack(fill='both', expand=True)
        tree.tag_configure('present', foreground=SUCCESS)
        tree.tag_configure('late',    foreground=WARNING)
        tree.tag_configure('absent',  foreground=DANGER)
        return tree

    def _btn(self, parent, text, cmd, color, side='left', padx=4):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=WHITE, font=(FONT, 10, 'bold'),
                      relief='flat', padx=12, pady=6, cursor='hand2')
        b.pack(side=side, padx=padx)
        return b

    def _grade(self, marks, max_marks):
        pct = (marks / max_marks * 100) if max_marks > 0 else 0
        if pct >= 90: return 'A+'
        elif pct >= 80: return 'A'
        elif pct >= 70: return 'B'
        elif pct >= 60: return 'C'
        elif pct >= 50: return 'D'
        else: return 'F'

    # ══════════════════════════════════════════════════════
    #  🏠 HOME
    # ══════════════════════════════════════════════════════
    def show_home(self):
        self.page_title.config(text="🏠  My Attendance Dashboard")
        self.clear_content()
        self._load_summary()
        s = self._summary

        # Student info card
        info = tk.Frame(self.content, bg=WHITE)
        info.pack(fill='x', pady=(0, 10))
        tk.Frame(info, bg=STUDENT, height=5).pack(fill='x')
        row = tk.Frame(info, bg=WHITE)
        row.pack(fill='x', padx=20, pady=12)

        try:
            pp = self.student.get('photo_path')
            if pp and os.path.exists(pp):
                img = Image.open(pp).resize((75, 85), Image.LANCZOS)
                ph  = ImageTk.PhotoImage(img)
                lbl = tk.Label(row, image=ph, bg=WHITE)
                lbl.image = ph
                lbl.pack(side='left', padx=(0, 18))
            else: raise Exception()
        except Exception:
            tk.Label(row, text="👤", font=(FONT+' Emoji', 32), bg=WHITE, fg=MUTED).pack(side='left', padx=(0,18))

        det = tk.Frame(row, bg=WHITE)
        det.pack(side='left')
        tk.Label(det, text=self.student.get('full_name',''), font=(FONT, 17, 'bold'), bg=WHITE, fg=BROWN).pack(anchor='w')
        tk.Label(det, text=f"ID: {self.sid}  |  Class: {self.student.get('class_name','')}  |  Section: {self.student.get('section','')}",
                 font=(FONT, 9), bg=WHITE, fg=MUTED).pack(anchor='w', pady=2)
        tk.Label(det, text=f"📧 {self.student.get('email','') or '—'}    📱 {self.student.get('phone','') or '—'}",
                 font=(FONT, 9), bg=WHITE, fg=MUTED).pack(anchor='w')

        today_recs = [r for r in s['records'] if r.get('date') == date.today()]
        if today_recs:
            ts = today_recs[0].get('status','absent')
            tc = SUCCESS if ts=='present' else (WARNING if ts=='late' else DANGER)
            txt = f"Today: {ts.upper()}  •  Time In: {today_recs[0].get('time_in','') or '—'}"
        else:
            tc, txt = MUTED, "Today: Not yet marked"
        tk.Label(det, text=txt, font=(FONT, 10, 'bold'), bg=WHITE, fg=tc).pack(anchor='w', pady=(4,0))

        pct = s['percentage']
        pc  = SUCCESS if pct >= 75 else (WARNING if pct >= 60 else DANGER)
        badge = tk.Frame(row, bg=pc, width=95, height=72)
        badge.pack(side='right', padx=10)
        badge.pack_propagate(False)
        tk.Label(badge, text=f"{pct}%", font=(FONT, 20, 'bold'), bg=pc, fg=WHITE).pack(expand=True)
        tk.Label(badge, text="Attendance", font=(FONT, 8), bg=pc, fg=WHITE).pack(pady=(0,5))

        # Stat cards
        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill='x', pady=(0, 8))
        late = sum(1 for r in s['records'] if r.get('status')=='late')
        self._stat_card(cards, "Total Classes", s['total'], "📅", INFO)
        self._stat_card(cards, "Present",        s['present'], "✅", SUCCESS)
        self._stat_card(cards, "Late",            late,   "⏰", WARNING)
        self._stat_card(cards, "Absent",          s['absent'], "❌", DANGER)
        self._stat_card(cards, "Attendance %",    f"{pct}%", "📊", pc)

        # Alert
        if pct < 75:
            needed = max(0, int((0.75*s['total'] - s['present']) / 0.25) + 1) if s['total'] else 0
            box = tk.Frame(self.content, bg='#FFF3E0', relief='solid', bd=1)
            box.pack(fill='x', pady=(0, 8))
            tk.Label(box, text=f"⚠️  Below 75%! Need ~{needed} more consecutive classes to reach 75%.",
                     font=(FONT, 10, 'bold'), bg='#FFF3E0', fg=WARNING).pack(padx=15, pady=8, anchor='w')
        else:
            box = tk.Frame(self.content, bg='#E8F5E9', relief='solid', bd=1)
            box.pack(fill='x', pady=(0, 8))
            tk.Label(box, text="✅  Attendance above 75% — Keep it up!",
                     font=(FONT, 10, 'bold'), bg='#E8F5E9', fg=SUCCESS).pack(padx=15, pady=8, anchor='w')

        # Quick actions
        act = tk.Frame(self.content, bg=BG)
        act.pack(fill='x', pady=(0, 10))
        for label, key, cmd, color in [
            ("📅 Daily",  'daily',   self.show_daily,   INFO),
            ("📆 Weekly", 'weekly',  self.show_weekly,  STUDENT),
            ("🗓️ Monthly",'monthly', self.show_monthly, BROWN),
            ("📝 Results",'results', self.show_results, PURPLE),
            ("👤 Profile",'profile', self.show_profile, BROWN_LT),
            ("💰 Fees",   'fees',    self.show_fees,    DANGER),
            ("📥 PDF",    None,      self._download_pdf,'#5D4037'),
        ]:
            tk.Button(act, text=label,
                      command=(lambda k=key, c=cmd: self.nav_click(k, c) if k else c()),
                      bg=color, fg=WHITE, font=(FONT, 9, 'bold'),
                      relief='flat', padx=4, pady=7, cursor='hand2').pack(
                          side='left', expand=True, fill='x', padx=2)

        # Recent records
        self._section_hdr("Recent Attendance")
        recent = sorted(s['records'], key=lambda x: x.get('date', date.min), reverse=True)[:6]
        tree = self._tree(self.content, ('Date','Day','Time In','Time Out','Status'),
                          [110, 90, 100, 100, 90], height=6)
        for r in recent:
            d = r.get('date')
            st = r.get('status','')
            tree.insert('','end', values=(
                str(d) if d else '', d.strftime('%a') if d else '',
                str(r.get('time_in','') or '—'), str(r.get('time_out','') or '—'),
                st.upper()
            ), tags=(st,))

    # ══════════════════════════════════════════════════════
    #  📅 DAILY
    # ══════════════════════════════════════════════════════
    def show_daily(self):
        self.page_title.config(text="📅  Daily Attendance")
        self.clear_content()

        pick = tk.Frame(self.content, bg=WHITE)
        pick.pack(fill='x', pady=(0, 10))
        tk.Frame(pick, bg=INFO, height=4).pack(fill='x')
        row = tk.Frame(pick, bg=WHITE)
        row.pack(fill='x', padx=15, pady=10)
        tk.Label(row, text="Select Date:", font=(FONT, 11, 'bold'), bg=WHITE, fg=DARK).pack(side='left', padx=(0,8))
        date_var = tk.StringVar(value=str(date.today()))
        frm = tk.Frame(row, bg=WHITE, relief='solid', bd=1)
        tk.Entry(frm, textvariable=date_var, font=(FONT, 12), width=14,
                 bg=WHITE, fg=DARK, relief='flat', bd=6).pack()
        frm.pack(side='left')
        tk.Label(row, text="YYYY-MM-DD", font=(FONT, 9), bg=WHITE, fg=MUTED).pack(side='left', padx=6)

        result_frame = tk.Frame(self.content, bg=BG)
        result_frame.pack(fill='both', expand=True)

        def load_day():
            for w in result_frame.winfo_children(): w.destroy()
            try:
                d = datetime.strptime(date_var.get().strip(), '%Y-%m-%d').date()
            except ValueError:
                tk.Label(result_frame, text="❌ Invalid date. Use YYYY-MM-DD",
                         bg=BG, fg=DANGER, font=(FONT, 11)).pack(pady=20)
                return

            all_recs = self._summary.get('records', [])
            recs     = [r for r in all_recs if r.get('date') == d]

            hdr = tk.Frame(result_frame, bg=WHITE)
            hdr.pack(fill='x', pady=(0, 10))
            tk.Frame(hdr, bg=INFO, height=4).pack(fill='x')
            tk.Label(hdr, text=f"  📅  {d.strftime('%A, %d %B %Y')}",
                     font=(FONT, 13, 'bold'), bg=WHITE, fg=BROWN).pack(anchor='w', padx=15, pady=8)

            if recs:
                r  = recs[0]
                st = r.get('status','absent')
                sc = SUCCESS if st=='present' else (WARNING if st=='late' else DANGER)
                icon = {"present":"✅","late":"⏰","absent":"❌"}.get(st,"❓")

                big = tk.Frame(result_frame, bg=WHITE)
                big.pack(fill='x', pady=6)
                tk.Frame(big, bg=sc, height=5).pack(fill='x')
                inner = tk.Frame(big, bg=WHITE)
                inner.pack(fill='x', padx=20, pady=15)
                tk.Label(inner, text=f"{icon}  {st.upper()}",
                         font=(FONT, 30, 'bold'), bg=WHITE, fg=sc).pack(anchor='w')

                det_row = tk.Frame(inner, bg=WHITE)
                det_row.pack(anchor='w', pady=(10, 0))
                for lbl, val in [
                    ("Time In",   str(r.get('time_in','') or '—')),
                    ("Time Out",  str(r.get('time_out','') or '—')),
                    ("Class",     str(r.get('class_name','') or '—')),
                    ("Marked By", str(r.get('marked_by','') or 'System')),
                ]:
                    tk.Label(det_row, text=f"  {lbl}: ", font=(FONT, 11, 'bold'), bg=WHITE, fg=DARK).pack(side='left')
                    tk.Label(det_row, text=f"{val}    ", font=(FONT, 11), bg=WHITE, fg=MUTED).pack(side='left')
            else:
                msg = ("📅 Future date." if d > date.today() else
                       "🏖️ Sunday — no classes." if d.weekday()==6 else
                       "❌ No attendance record for this date.")
                clr = INFO if d > date.today() else (MUTED if d.weekday()==6 else DANGER)
                box = tk.Frame(result_frame, bg='#F5F5F5', relief='solid', bd=1)
                box.pack(fill='x', pady=10)
                tk.Label(box, text=msg, font=(FONT, 13, 'bold'), bg='#F5F5F5', fg=clr).pack(padx=20, pady=20)

        tk.Button(row, text="🔍 Search", command=load_day,
                  bg=INFO, fg=WHITE, font=(FONT, 10, 'bold'),
                  relief='flat', padx=14, pady=5, cursor='hand2').pack(side='left', padx=8)

        for label, delta in [("Today", 0), ("Yesterday", -1)]:
            d_t = date.today() + timedelta(days=delta)
            tk.Button(row, text=label,
                      command=lambda d=d_t: [date_var.set(str(d)), load_day()],
                      bg=CREAM, fg=BROWN, font=(FONT, 9, 'bold'),
                      relief='solid', bd=1, cursor='hand2').pack(side='left', padx=3, ipady=4, ipadx=6)

        load_day()

    # ══════════════════════════════════════════════════════
    #  📆 WEEKLY
    # ══════════════════════════════════════════════════════
    def show_weekly(self):
        self.page_title.config(text="📆  Weekly Attendance")
        self.clear_content()

        def render(offset):
            self._week_offset = offset
            self.clear_content()

            today      = date.today()
            week_end   = today + timedelta(days=offset * 7)
            week_start = week_end - timedelta(days=6)

            # Nav
            nav = tk.Frame(self.content, bg=WHITE)
            nav.pack(fill='x', pady=(0, 10))
            tk.Frame(nav, bg=STUDENT, height=4).pack(fill='x')
            ni = tk.Frame(nav, bg=WHITE)
            ni.pack(fill='x', padx=15, pady=8)
            tk.Button(ni, text="◀ Prev", command=lambda: render(offset-1),
                      bg=CREAM, fg=BROWN, font=(FONT, 10, 'bold'),
                      relief='solid', bd=1, cursor='hand2').pack(side='left', ipady=4, ipadx=10)
            tk.Label(ni, text=f"  {week_start.strftime('%d %b')} — {week_end.strftime('%d %b %Y')}  ",
                     font=(FONT, 13, 'bold'), bg=WHITE, fg=BROWN).pack(side='left', expand=True)
            if offset < 0:
                tk.Button(ni, text="Next ▶", command=lambda: render(offset+1),
                          bg=CREAM, fg=BROWN, font=(FONT, 10, 'bold'),
                          relief='solid', bd=1, cursor='hand2').pack(side='right', ipady=4, ipadx=10)

            rec_map = {}
            for r in self._summary.get('records', []):
                d = r.get('date')
                if d: rec_map[d] = r

            # 7-day strip
            strip = tk.Frame(self.content, bg=BG)
            strip.pack(fill='x', pady=(0, 12))
            wp = wl = wa = 0

            for i in range(7):
                d        = week_start + timedelta(days=i)
                rec      = rec_map.get(d)
                is_today = (d == today)
                is_fut   = (d > today)
                is_sun   = (d.weekday() == 6)

                if is_fut or is_sun:
                    bg_c, fg_c, icon, lbl = '#F5F5F5', MUTED, '—', 'No Class' if is_sun else '—'
                elif rec:
                    st = rec.get('status','')
                    if st == 'present':
                        bg_c, fg_c, icon, lbl = '#E8F5E9', SUCCESS, '✅', 'Present'
                    elif st == 'late':
                        bg_c, fg_c, icon, lbl = '#FFF8E1', WARNING, '⏰', 'Late'
                    else:
                        bg_c, fg_c, icon, lbl = '#FFEBEE', DANGER, '❌', 'Absent'
                else:
                    bg_c, fg_c, icon, lbl = '#FFF3E0', MUTED, '—', 'No Data'

                border = GOLD if is_today else '#DDDDDD'
                cell = tk.Frame(strip, bg=bg_c, highlightbackground=border,
                                highlightthickness=2 if is_today else 1)
                cell.pack(side='left', expand=True, fill='both', padx=3, pady=2)
                tk.Label(cell, text=d.strftime('%a'), font=(FONT,9,'bold'), bg=bg_c, fg=MUTED).pack(pady=(8,0))
                tk.Label(cell, text=d.strftime('%d'), font=(FONT,18,'bold'), bg=bg_c,
                         fg=GOLD if is_today else DARK).pack()
                tk.Label(cell, text=d.strftime('%b'), font=(FONT,8), bg=bg_c, fg=MUTED).pack()
                tk.Label(cell, text=icon, font=(FONT+' Emoji',14), bg=bg_c).pack()
                tk.Label(cell, text=lbl, font=(FONT,8,'bold'), bg=bg_c, fg=fg_c).pack(pady=(2,8))
                if rec:
                    ti = str(rec.get('time_in','') or '')[:5]
                    if ti: tk.Label(cell, text=ti, font=(FONT,7), bg=bg_c, fg=MUTED).pack(pady=(0,3))

            # Recalculate properly
            week_recs = [rec_map[week_start+timedelta(days=i)]
                         for i in range(7) if (week_start+timedelta(days=i)) in rec_map]
            wp2 = sum(1 for r in week_recs if r.get('status')=='present')
            wl2 = sum(1 for r in week_recs if r.get('status')=='late')
            wa2 = sum(1 for r in week_recs if r.get('status')=='absent')
            wpct = round((wp2+wl2)/7*100)

            sum_box = tk.Frame(self.content, bg=WHITE)
            sum_box.pack(fill='x', pady=(0, 10))
            tk.Frame(sum_box, bg=STUDENT, height=4).pack(fill='x')
            tk.Label(sum_box, text=f"   Week: ✅ Present: {wp2}   ⏰ Late: {wl2}   ❌ Absent: {wa2}   📊 Rate: {wpct}%",
                     font=(FONT, 11, 'bold'), bg=WHITE, fg=DARK).pack(anchor='w', pady=8)

            if week_recs:
                self._section_hdr("Detailed Records", STUDENT)
                cols = ('Date','Day','Time In','Time Out','Status','Marked By')
                tree = self._tree(self.content, cols, [110,110,100,100,90,140], height=8)
                for r in sorted(week_recs, key=lambda x: x.get('date',date.min), reverse=True):
                    d = r.get('date'); st = r.get('status','')
                    tree.insert('','end', values=(
                        str(d) if d else '', d.strftime('%A') if d else '',
                        str(r.get('time_in','') or '—'), str(r.get('time_out','') or '—'),
                        st.upper(), str(r.get('marked_by','') or 'System')
                    ), tags=(st,))

        render(self._week_offset)

    # ══════════════════════════════════════════════════════
    #  🗓️ MONTHLY
    # ══════════════════════════════════════════════════════
    def show_monthly(self):
        self.page_title.config(text="🗓️  Monthly Attendance")
        self.clear_content()

        def render(year, month):
            self._month_year  = year
            self._month_month = month
            self.clear_content()
            today = date.today()

            prev_m = month-1 or 12
            prev_y = year-(1 if month==1 else 0)
            next_m = (month%12)+1
            next_y = year+(1 if month==12 else 0)

            nav = tk.Frame(self.content, bg=WHITE)
            nav.pack(fill='x', pady=(0,10))
            tk.Frame(nav, bg=BROWN, height=4).pack(fill='x')
            ni = tk.Frame(nav, bg=WHITE)
            ni.pack(fill='x', padx=15, pady=8)
            tk.Button(ni, text="◀ Prev", command=lambda: render(prev_y, prev_m),
                      bg=CREAM, fg=BROWN, font=(FONT,10,'bold'),
                      relief='solid', bd=1, cursor='hand2').pack(side='left', ipady=4, ipadx=10)
            tk.Label(ni, text=f"  {calendar.month_name[month]}  {year}  ",
                     font=(FONT,14,'bold'), bg=WHITE, fg=BROWN).pack(side='left', expand=True)
            if date(next_y, next_m, 1) <= today.replace(day=1):
                tk.Button(ni, text="Next ▶", command=lambda: render(next_y, next_m),
                          bg=CREAM, fg=BROWN, font=(FONT,10,'bold'),
                          relief='solid', bd=1, cursor='hand2').pack(side='right', ipady=4, ipadx=10)

            all_recs = self._summary.get('records', [])
            rec_map  = {}
            for r in all_recs:
                d = r.get('date')
                if d and d.year==year and d.month==month:
                    rec_map[d.day] = r

            days_in  = calendar.monthrange(year, month)[1]
            mp = sum(1 for r in rec_map.values() if r.get('status')=='present')
            ml = sum(1 for r in rec_map.values() if r.get('status')=='late')
            ma = sum(1 for r in rec_map.values() if r.get('status')=='absent')
            mpct = round((mp+ml)/days_in*100, 1)
            pc   = SUCCESS if mpct>=75 else (WARNING if mpct>=60 else DANGER)

            stat_row = tk.Frame(self.content, bg=BG)
            stat_row.pack(fill='x', pady=(0,8))
            for title, val, color in [("Present", mp, SUCCESS), ("Late", ml, WARNING),
                                       ("Absent", ma, DANGER), ("Attendance Rate", f"{mpct}%", pc)]:
                c = tk.Frame(stat_row, bg=WHITE)
                c.pack(side='left', expand=True, fill='both', padx=4)
                tk.Frame(c, bg=color, height=4).pack(fill='x')
                tk.Label(c, text=str(val),   font=(FONT,20,'bold'), bg=WHITE, fg=color).pack(pady=(8,2))
                tk.Label(c, text=str(title), font=(FONT,9),  bg=WHITE, fg=MUTED).pack(pady=(0,8))

            # Calendar grid
            grid = tk.Frame(self.content, bg=WHITE, relief='solid', bd=1)
            grid.pack(fill='both', expand=True, pady=(0,6))

            day_hdr = tk.Frame(grid, bg=BROWN)
            day_hdr.pack(fill='x')
            for dn in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:
                tk.Label(day_hdr, text=dn, font=(FONT,10,'bold'),
                         bg=BROWN, fg=WHITE, width=6).pack(side='left', expand=True, fill='x', pady=5)

            for week in calendar.monthcalendar(year, month):
                wrow = tk.Frame(grid, bg=WHITE)
                wrow.pack(fill='x')
                for dn in week:
                    cell = tk.Frame(wrow, bg=WHITE, highlightbackground='#EEEEEE',
                                    highlightthickness=1, width=70, height=52)
                    cell.pack(side='left', expand=True, fill='both')
                    cell.pack_propagate(False)
                    if dn == 0:
                        tk.Label(cell, text='', bg='#F9F9F9').pack(fill='both', expand=True)
                        continue
                    this_d  = date(year, month, dn)
                    rec     = rec_map.get(dn)
                    is_td   = (this_d == today)
                    is_fut  = (this_d > today)
                    if is_fut:
                        bg_c, fg_c, dot = WHITE, MUTED, ''
                    elif rec:
                        st = rec.get('status','')
                        if st=='present':  bg_c,fg_c,dot = '#E8F5E9',SUCCESS,'●'
                        elif st=='late':   bg_c,fg_c,dot = '#FFF8E1',WARNING,'●'
                        else:              bg_c,fg_c,dot = '#FFEBEE',DANGER, '●'
                    else:
                        bg_c,fg_c,dot = '#F5F5F5',MUTED,''
                    cell.config(bg=bg_c,
                                highlightbackground=GOLD if is_td else '#EEEEEE',
                                highlightthickness=2 if is_td else 1)
                    tk.Label(cell, text=str(dn), font=(FONT,11,'bold'), bg=bg_c,
                             fg=GOLD if is_td else DARK).pack(anchor='nw', padx=4, pady=(3,0))
                    if dot:
                        tk.Label(cell, text=dot, font=(FONT,13), bg=bg_c, fg=fg_c).pack()

            leg = tk.Frame(self.content, bg=BG)
            leg.pack(fill='x', pady=3)
            for lbl, color in [("● Present",SUCCESS),("● Late",WARNING),("● Absent",DANGER),("  No Record/Future",MUTED)]:
                tk.Label(leg, text=lbl, font=(FONT,9,'bold'), bg=BG, fg=color).pack(side='left', padx=10)

        render(self._month_year, self._month_month)

    # ══════════════════════════════════════════════════════
    #  📝 RESULTS
    # ══════════════════════════════════════════════════════
    def show_results(self):
        self.page_title.config(text="📝  My Academic Results")
        self.clear_content()

        try:
            results = self.db.get_student_results(self.sid)
        except Exception:
            results = []

        if results:
            total_m = sum(float(r.get('marks') or 0) for r in results)
            max_m   = sum(float(r.get('max_marks') or 100) for r in results)
            ov_pct  = round(total_m/max_m*100, 1) if max_m else 0
            ov_grd  = self._grade(ov_pct, 100)
            gc      = SUCCESS if ov_pct>=60 else DANGER

            sum_card = tk.Frame(self.content, bg=WHITE)
            sum_card.pack(fill='x', pady=(0, 10))
            tk.Frame(sum_card, bg=PURPLE, height=5).pack(fill='x')
            row = tk.Frame(sum_card, bg=WHITE)
            row.pack(fill='x', padx=20, pady=12)
            for title, val, color in [
                ("Subjects", len(results), PURPLE),
                ("Total Marks", f"{total_m:.0f}/{max_m:.0f}", INFO),
                ("Overall %", f"{ov_pct}%", gc),
                ("Grade", ov_grd, gc),
            ]:
                c = tk.Frame(row, bg=WHITE)
                c.pack(side='left', expand=True, fill='both')
                tk.Label(c, text=str(val), font=(FONT,22,'bold'), bg=WHITE, fg=color).pack(pady=(6,2))
                tk.Label(c, text=title, font=(FONT,9), bg=WHITE, fg=MUTED).pack(pady=(0,8))

            sems = sorted(set(r.get('semester','') or 'N/A' for r in results))
            ff   = tk.Frame(self.content, bg=BG)
            ff.pack(fill='x', pady=(0,6))
            tk.Label(ff, text="Filter Semester:", font=(FONT,10,'bold'), bg=BG, fg=DARK).pack(side='left', padx=(0,8))
            sem_var = tk.StringVar(value='All')
            for sem in ['All']+sems:
                tk.Radiobutton(ff, text=sem, variable=sem_var, value=sem,
                               bg=BG, fg=DARK, font=(FONT,9), activebackground=BG).pack(side='left', padx=6)

            self._section_hdr("Subject-wise Results", PURPLE)
            cols  = ('Subject','Exam Type','Marks','Max','Grade','Semester','Date')
            tree  = self._tree(self.content, cols, [160,110,80,70,60,90,110], height=12)

            def load_res(*_):
                tree.delete(*tree.get_children())
                sf = sem_var.get()
                for r in results:
                    sem = r.get('semester','') or 'N/A'
                    if sf!='All' and sem!=sf: continue
                    m = float(r.get('marks') or 0)
                    mx= float(r.get('max_marks') or 100)
                    g = r.get('grade') or self._grade(m, mx)
                    tree.insert('','end', values=(
                        r.get('subject',''), r.get('exam_type','Internal'),
                        f"{m:.1f}", f"{mx:.0f}", g,
                        r.get('semester',''), str(r.get('result_date',''))[:10]
                    ), tags=(g,))
                tree.tag_configure('A+', foreground=SUCCESS)
                tree.tag_configure('A',  foreground=SUCCESS)
                tree.tag_configure('B',  foreground=INFO)
                tree.tag_configure('C',  foreground=WARNING)
                tree.tag_configure('D',  foreground=WARNING)
                tree.tag_configure('F',  foreground=DANGER)
            sem_var.trace('w', load_res)
            load_res()
        else:
            empty = tk.Frame(self.content, bg=WHITE)
            empty.pack(fill='both', expand=True)
            tk.Frame(empty, bg=PURPLE, height=5).pack(fill='x')
            tk.Label(empty, text="📝\n\nNo academic results found.\nAsk your teacher or admin to add your marks.",
                     font=(FONT,13), bg=WHITE, fg=MUTED, justify='center').pack(expand=True, pady=60)

        btn_row = tk.Frame(self.content, bg=BG)
        btn_row.pack(fill='x', pady=6)
        self._btn(btn_row, "📥 Download Report PDF", self._download_pdf, PURPLE)

    # ══════════════════════════════════════════════════════
    #  👤 PROFILE
    # ══════════════════════════════════════════════════════
    def show_profile(self):
        self.page_title.config(text="👤  My Profile")
        self.clear_content()

        canvas = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        sb     = ttk.Scrollbar(self.content, orient='vertical', command=canvas.yview)
        sf     = tk.Frame(canvas, bg=BG)
        sf.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0), window=sf, anchor='nw')
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)

        # Profile card
        hdr = tk.Frame(sf, bg=WHITE)
        hdr.pack(fill='x', pady=(0,12))
        tk.Frame(hdr, bg=STUDENT, height=6).pack(fill='x')
        row = tk.Frame(hdr, bg=WHITE)
        row.pack(fill='x', padx=25, pady=20)

        pl = tk.Label(row, bg=CREAM, width=12, height=8, text="No\nPhoto",
                      fg=MUTED, font=(FONT,9), relief='solid', bd=1)
        try:
            pp = self.student.get('photo_path')
            if pp and os.path.exists(pp):
                img = Image.open(pp).resize((110,130), Image.LANCZOS)
                ph  = ImageTk.PhotoImage(img)
                pl.config(image=ph, text='', width=110, height=130, bd=0)
                pl.image = ph
        except Exception: pass
        pl.pack(side='left', padx=(0,25))

        info = tk.Frame(row, bg=WHITE)
        info.pack(side='left', fill='both', expand=True)
        tk.Label(info, text=self.student.get('full_name',''), font=(FONT,20,'bold'), bg=WHITE, fg=BROWN).pack(anchor='w')
        sc = SUCCESS if self.student.get('status')=='active' else DANGER
        tk.Label(info, text=f"● {(self.student.get('status','active')).upper()}",
                 font=(FONT,10,'bold'), bg=WHITE, fg=sc).pack(anchor='w', pady=3)
        for lbl, val in [
            ("🪪 Student ID",  self.sid),
            ("🏫 Class",       f"{self.student.get('class_name','')} — {self.student.get('section','')}"),
            ("📧 Email",       self.student.get('email','') or '—'),
            ("📱 Phone",       self.student.get('phone','') or '—'),
            ("📅 Registered",  str(self.student.get('registered_at',''))[:10]),
        ]:
            r2 = tk.Frame(info, bg=WHITE); r2.pack(anchor='w', pady=2)
            tk.Label(r2, text=f"{lbl}: ", font=(FONT,10,'bold'), bg=WHITE, fg=DARK, width=16, anchor='w').pack(side='left')
            tk.Label(r2, text=val, font=(FONT,10), bg=WHITE, fg=MUTED).pack(side='left')

        # Attendance summary
        for card_title, color, content_fn in [
            ("📊  Attendance Summary", INFO,   self._profile_att_section),
            ("📝  Academic Summary",   PURPLE, self._profile_res_section),
            ("💰  Fee Summary",        DANGER, self._profile_fee_section),
        ]:
            card = tk.Frame(sf, bg=WHITE); card.pack(fill='x', pady=(0,12))
            tk.Frame(card, bg=color, height=5).pack(fill='x')
            tk.Label(card, text=f"  {card_title}", font=(FONT,12,'bold'), bg=WHITE, fg=BROWN).pack(anchor='w', padx=15, pady=8)
            content_fn(card)

        br = tk.Frame(sf, bg=BG); br.pack(fill='x', pady=8)
        self._btn(br, "📥 Download Full PDF Report", self._download_pdf, PURPLE)

    def _profile_att_section(self, parent):
        s   = self._summary
        pct = s['percentage']
        pc  = SUCCESS if pct>=75 else (WARNING if pct>=60 else DANGER)
        row = tk.Frame(parent, bg=WHITE); row.pack(fill='x', padx=15, pady=(0,15))
        for title, val, color in [("Total",s['total'],INFO),("Present",s['present'],SUCCESS),
                                   ("Absent",s['absent'],DANGER),(f"{pct}%","Attendance",pc)]:
            c = tk.Frame(row, bg=CREAM); c.pack(side='left', expand=True, fill='both', padx=5)
            tk.Label(c, text=str(val), font=(FONT,18,'bold'), bg=CREAM, fg=color).pack(pady=(10,2))
            tk.Label(c, text=title,   font=(FONT,8),  bg=CREAM, fg=MUTED).pack(pady=(0,10))

    def _profile_res_section(self, parent):
        try:    results = self.db.get_student_results(self.sid)
        except: results = []
        if results:
            tm = sum(float(r.get('marks') or 0) for r in results)
            mx = sum(float(r.get('max_marks') or 100) for r in results)
            op = round(tm/mx*100,1) if mx else 0
            tk.Label(parent, text=f"   {len(results)} subjects  |  {tm:.0f}/{mx:.0f}  |  {op}%  |  {self._grade(op,100)}",
                     font=(FONT,11), bg=WHITE, fg=DARK).pack(anchor='w', padx=15, pady=(0,12))
        else:
            tk.Label(parent, text="   No results recorded yet.", font=(FONT,10), bg=WHITE, fg=MUTED).pack(anchor='w', padx=15, pady=(0,12))

    def _profile_fee_section(self, parent):
        try:    fs = self.db.get_fees_summary(self.sid)
        except: fs = {'total_amount':0,'total_paid':0,'total_due':0,'paid_count':0,'pending_count':0}
        dc  = DANGER if fs['total_due']>0 else SUCCESS
        row = tk.Frame(parent, bg=WHITE); row.pack(fill='x', padx=15, pady=(0,15))
        for title, val, color in [
            ("Total",   f"₹{fs['total_amount']:,.0f}", INFO),
            ("Paid",    f"₹{fs['total_paid']:,.0f}",   SUCCESS),
            ("Due",     f"₹{fs['total_due']:,.0f}",    dc),
            ("Pending", str(fs['pending_count']),       WARNING),
        ]:
            c = tk.Frame(row, bg=CREAM); c.pack(side='left', expand=True, fill='both', padx=5)
            tk.Label(c, text=val,   font=(FONT,15,'bold'), bg=CREAM, fg=color).pack(pady=(10,2))
            tk.Label(c, text=title, font=(FONT,8),  bg=CREAM, fg=MUTED).pack(pady=(0,10))

    # ══════════════════════════════════════════════════════
    #  💰 FEES
    # ══════════════════════════════════════════════════════
    def show_fees(self):
        self.page_title.config(text="💰  My Fee Details")
        self.clear_content()

        try:    fs = self.db.get_fees_summary(self.sid)
        except: fs = {'fees':[],'total_amount':0,'total_paid':0,'total_due':0,'paid_count':0,'pending_count':0}
        fees = fs.get('fees', [])

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill='x', pady=(0,10))
        dc = DANGER if fs['total_due']>0 else SUCCESS
        for title, val, icon, color in [
            ("Total Fees",    f"₹{fs['total_amount']:,.2f}", "💰", INFO),
            ("Amount Paid",   f"₹{fs['total_paid']:,.2f}",   "✅", SUCCESS),
            ("Amount Due",    f"₹{fs['total_due']:,.2f}",    "⏳", dc),
            ("Paid Items",    str(fs['paid_count']),          "✔️", SUCCESS),
            ("Pending Items", str(fs['pending_count']),       "⚠️", WARNING),
        ]:
            self._stat_card(cards, title, val, icon, color)

        if fs['total_due'] > 0:
            alert = tk.Frame(self.content, bg='#FFEBEE', relief='solid', bd=1)
            alert.pack(fill='x', pady=(0,10))
            tk.Label(alert, text=f"⚠️  ₹{fs['total_due']:,.2f} pending! Please contact the accounts office.",
                     font=(FONT,10,'bold'), bg='#FFEBEE', fg=DANGER).pack(padx=15, pady=8, anchor='w')
        else:
            ok = tk.Frame(self.content, bg='#E8F5E9', relief='solid', bd=1)
            ok.pack(fill='x', pady=(0,10))
            tk.Label(ok, text="✅  All fees are paid!",
                     font=(FONT,10,'bold'), bg='#E8F5E9', fg=SUCCESS).pack(padx=15, pady=8, anchor='w')

        ff = tk.Frame(self.content, bg=BG); ff.pack(fill='x', pady=(0,6))
        tk.Label(ff, text="Filter:", font=(FONT,10,'bold'), bg=BG, fg=DARK).pack(side='left', padx=(0,8))
        fee_f = tk.StringVar(value='All')
        for opt in ['All','Paid','Pending','Partial','Overdue']:
            tk.Radiobutton(ff, text=opt, variable=fee_f, value=opt,
                           bg=BG, fg=DARK, font=(FONT,9), activebackground=BG).pack(side='left', padx=6)

        self._section_hdr("Fee Records", DANGER)
        cols   = ('Fee Type','Amount (₹)','Paid (₹)','Due (₹)','Due Date','Paid Date','Status','Receipt No','Semester')
        widths = [150,100,90,90,100,100,85,110,90]
        tree   = self._tree(self.content, cols, widths, height=12)

        def load_fees(*_):
            tree.delete(*tree.get_children())
            fv = fee_f.get().lower()
            for f in fees:
                st = (f.get('status') or 'pending').lower()
                if fv!='all' and st!=fv: continue
                amt = float(f.get('amount') or 0)
                pd  = float(f.get('paid_amount') or 0)
                tree.insert('','end', values=(
                    f.get('fee_type',''), f"₹{amt:,.2f}", f"₹{pd:,.2f}", f"₹{(amt-pd):,.2f}",
                    str(f.get('due_date','') or '—')[:10], str(f.get('paid_date','') or '—')[:10],
                    st.upper(), f.get('receipt_no','') or '—', f.get('semester','') or '—'
                ), tags=(st,))
            tree.tag_configure('paid',    foreground=SUCCESS)
            tree.tag_configure('pending', foreground=WARNING)
            tree.tag_configure('overdue', foreground=DANGER)
            tree.tag_configure('partial', foreground=INFO)

        fee_f.trace('w', load_fees)
        load_fees()

        if not fees:
            tk.Label(self.content, text="No fee records found. Contact admin to add fee details.",
                     bg=BG, fg=MUTED, font=(FONT,11)).pack(pady=20)

        br = tk.Frame(self.content, bg=BG); br.pack(fill='x', pady=8)
        self._btn(br, "📥 Download Fee Report PDF", self._download_pdf, DANGER)
        self._btn(br, "📥 Full Report PDF",          self._download_pdf, PURPLE)

    # ══════════════════════════════════════════════════════
    #  📥 PDF DOWNLOAD
    # ══════════════════════════════════════════════════════
    def _download_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF Files', '*.pdf')],
            initialfile=f"student_report_{self.sid}_{date.today()}.pdf")
        if not path: return

        try:
            from pdf_reports import generate_student_report
            generate_student_report(self.db, path, self.sid)
            messagebox.showinfo("✅ Downloaded",
                f"Your full student report has been downloaded!\n\n{path}")
            self._open_file(path)
        except ImportError:
            messagebox.showerror("Missing", "pdf_reports.py not found in project folder.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _open_file(self, path):
        try:
            import subprocess, sys
            if sys.platform == 'win32':    os.startfile(path)
            elif sys.platform == 'darwin': subprocess.call(['open', path])
            else:                          subprocess.call(['xdg-open', path])
        except Exception: pass

    # ══════════════════════════════════════════════════════
    #  LOGOUT
    # ══════════════════════════════════════════════════════
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.log_activity("LOGOUT", self.sid, "Student logged out")
            self.root.destroy()
            import tkinter as tk
            from login import LoginWindow
            r = tk.Tk()
            LoginWindow(r)
            r.mainloop()