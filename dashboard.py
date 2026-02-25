"""
Dashboard - Vanita Vishram Women's University
White & Brown Theme | Full Student Profile System
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime, date
from PIL import Image, ImageTk
from database import DatabaseManager

# ── Brand Colors ───────────────────────────────────────────
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
FONT     = 'Segoe UI'

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'college_logo.png')


class Dashboard:
    def __init__(self, root, admin_info):
        self.root  = root
        self.admin = admin_info
        self.role  = admin_info.get('role', 'admin') or 'admin'
        self.db    = DatabaseManager()
        self._logo_img = None
        self.setup_window()
        self.build_layout()
        self.nav_click('home', self.show_home)

    def setup_window(self):
        self.root.title("Vanita Vishram Women's University - Attendance System")
        self.root.geometry("1280x750")
        self.root.configure(bg=BG)
        try: self.root.state('zoomed')
        except Exception: pass

    # ════════════════════════════════════════════════════
    #  LAYOUT
    # ════════════════════════════════════════════════════
    def build_layout(self):
        # ── Sidebar ──────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=BROWN, width=230)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Logo + university name
        logo_frame = tk.Frame(self.sidebar, bg=BROWN)
        logo_frame.pack(fill='x', pady=(20, 5))
        try:
            img = Image.open(LOGO_PATH).resize((70, 70), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(logo_frame, image=self._logo_img, bg=BROWN).pack()
        except Exception:
            tk.Label(logo_frame, text="🎓", font=(FONT+' Emoji', 32),
                     bg=BROWN, fg=GOLD).pack()

        tk.Label(self.sidebar, text="Vanita Vishram",
                 font=(FONT, 12, 'bold'), bg=BROWN, fg=WHITE).pack()
        tk.Label(self.sidebar, text="Women's University",
                 font=(FONT, 9), bg=BROWN, fg=GOLD).pack()

        tk.Frame(self.sidebar, bg=GOLD, height=2).pack(fill='x', padx=15, pady=10)

        # Nav items — role-based
        self.nav_buttons = {}

        # All navs with minimum required role
        # format: (label, key, cmd, allowed_roles)
        all_navs = [
            ("🏠  Home",              'home',       self.show_home,                 ['admin']),
            ("📸  Take Attendance",   'attend',     self.show_attendance,           ['admin']),
            ("👥  Students",          'students',   self.show_students,             ['admin']),
            ("📊  Reports",           'reports',    self.show_reports,              ['admin']),
            ("👤  Student Profile",   'profile',    self.show_student_profile_search,['admin']),
            ("🏫  Manage Teachers",   'teachers',   self.show_manage_teachers,      ['admin']),
            ("💰  Manage Fees",       'fees',       self.show_manage_fees,          ['admin']),
            ("📋  Activity Log",      'log',        self.show_activity_log,         ['admin']),
            ("⚙️  Settings",          'settings',   self.show_settings,             ['admin']),
        ]
        for label, key, cmd, roles in all_navs:
            if self.role in roles:
                btn = tk.Button(self.sidebar, text=label,
                                command=lambda c=cmd, k=key: self.nav_click(k, c),
                                bg=BROWN, fg=WHITE, font=(FONT, 11),
                                relief='flat', anchor='w', padx=18,
                                cursor='hand2', activebackground=BROWN_LT,
                                activeforeground=WHITE)
                btn.pack(fill='x', pady=1, ipady=6)
                self.nav_buttons[key] = btn

        tk.Frame(self.sidebar, bg=GOLD, height=2).pack(fill='x', padx=15, pady=8, side='bottom')
        tk.Button(self.sidebar, text="🚪  Logout", command=self.logout,
                  bg=DANGER, fg=WHITE, font=(FONT, 11, 'bold'),
                  relief='flat', cursor='hand2').pack(side='bottom', fill='x', padx=15, pady=10)
        tk.Label(self.sidebar, text=f"👤 {self.admin['username']}",
                 bg=BROWN, fg=GOLD, font=(FONT, 9)).pack(side='bottom', pady=3)

        # ── Main area ─────────────────────────────────────
        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(side='left', fill='both', expand=True)

        # Top bar
        topbar = tk.Frame(self.main_frame, bg=WHITE, height=55)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=BROWN, width=4).pack(side='left', fill='y')
        self.page_title = tk.Label(topbar, text="Dashboard",
                                    font=(FONT, 16, 'bold'), bg=WHITE, fg=BROWN)
        self.page_title.pack(side='left', padx=20, pady=12)
        self.clock_lbl = tk.Label(topbar, font=(FONT, 10), bg=WHITE, fg=MUTED)
        self.clock_lbl.pack(side='right', padx=20)
        tk.Frame(topbar, bg=GOLD, height=2).pack(side='bottom', fill='x')
        self.update_clock()

        # Content
        self.content = tk.Frame(self.main_frame, bg=BG)
        self.content.pack(fill='both', expand=True, padx=18, pady=15)

    def update_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime("%A, %d %B %Y  |  %I:%M:%S %p"))
        self.root.after(1000, self.update_clock)

    def nav_click(self, key, cmd):
        for k, b in self.nav_buttons.items():
            b.config(bg=BROWN, fg=WHITE, font=(FONT, 11))
        self.nav_buttons[key].config(bg=BROWN_LT, fg=WHITE, font=(FONT, 11, 'bold'))
        cmd()

    def clear_content(self):
        for w in self.content.winfo_children(): w.destroy()

    # ── Style helpers ─────────────────────────────────────
    def _stat_card(self, parent, title, value, icon, color):
        card = tk.Frame(parent, bg=WHITE, relief='flat', bd=0)
        card.pack(side='left', expand=True, fill='both', padx=6, pady=4)
        tk.Frame(card, bg=color, height=5).pack(fill='x')
        tk.Label(card, text=icon, font=(FONT+' Emoji', 26), bg=WHITE).pack(pady=(14, 4))
        tk.Label(card, text=str(value), font=(FONT, 30, 'bold'), bg=WHITE, fg=color).pack()
        tk.Label(card, text=title, font=(FONT, 10), bg=WHITE, fg=MUTED).pack(pady=(2, 16))

    def _section_title(self, text):
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill='x', pady=(10, 6))
        tk.Frame(row, bg=BROWN, width=5, height=22).pack(side='left', fill='y')
        tk.Label(row, text=f"  {text}", font=(FONT, 13, 'bold'), bg=BG, fg=BROWN).pack(side='left')

    def _section_hdr(self, text, color=None):
        """Alias for _section_title — used by fees and other pages."""
        c = color or BROWN
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill='x', pady=(10, 6))
        tk.Frame(row, bg=c, width=5, height=22).pack(side='left', fill='y')
        tk.Label(row, text=f"  {text}", font=(FONT, 13, 'bold'), bg=BG, fg=c).pack(side='left')

    def _make_treeview(self, parent, cols, widths, height=12):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Uni.Treeview", background=WHITE, foreground=DARK,
                        rowheight=28, fieldbackground=WHITE, font=(FONT, 10))
        style.configure("Uni.Treeview.Heading", background=BROWN,
                        foreground=WHITE, font=(FONT, 10, 'bold'))
        style.map("Uni.Treeview", background=[('selected', BROWN_LT)])
        tree = ttk.Treeview(frame, columns=cols, show='headings',
                             style="Uni.Treeview", height=height)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')
        sy = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side='right', fill='y')
        sx.pack(side='bottom', fill='x')
        tree.pack(fill='both', expand=True)
        return tree

    def _action_btn(self, parent, text, cmd, color=None, side='left'):
        c = color or BROWN
        b = tk.Button(parent, text=text, command=cmd,
                      bg=c, fg=WHITE, font=(FONT, 10, 'bold'),
                      relief='flat', padx=12, pady=7, cursor='hand2',
                      activebackground=BROWN2, activeforeground=WHITE)
        b.pack(side=side, padx=4)
        return b

    # ════════════════════════════════════════════════════
    #  HOME
    # ════════════════════════════════════════════════════
    def show_home(self):
        self.page_title.config(text="🏠  Dashboard Overview")
        self.clear_content()

        try:    stats = self.db.get_attendance_stats()
        except Exception as e:
            stats = {'total_students':0,'present_today':0,'absent_today':0,'late_today':0}
            tk.Label(self.content, text=f"⚠️  DB: {e}", bg=BG, fg=DANGER,
                     font=(FONT, 9)).pack(anchor='w')

        cards_row = tk.Frame(self.content, bg=BG)
        cards_row.pack(fill='x', pady=(0, 12))
        self._stat_card(cards_row, "Total Students",  stats['total_students'],  "👥", INFO)
        self._stat_card(cards_row, "Present Today",   stats['present_today'],   "✅", SUCCESS)
        self._stat_card(cards_row, "Absent Today",    stats['absent_today'],    "❌", DANGER)
        self._stat_card(cards_row, "Late Today",      stats['late_today'],      "⏰", WARNING)

        # Quick actions
        act_row = tk.Frame(self.content, bg=BG)
        act_row.pack(fill='x', pady=(0, 12))
        actions = [
            ("📸 Take Attendance",  BROWN,   lambda: self.nav_click('attend',   self.show_attendance)),
            ("➕ Add Student",      SUCCESS, lambda: self.nav_click('students',  self.show_students)),
            ("📊 Reports",          INFO,    lambda: self.nav_click('reports',   self.show_reports)),
            ("👤 Student Profile",  BROWN_LT,lambda: self.nav_click('profile',  self.show_student_profile_search)),
        ]
        for label, color, cmd in actions:
            tk.Button(act_row, text=label, command=cmd,
                      bg=color, fg=WHITE, font=(FONT, 11, 'bold'),
                      relief='flat', padx=10, pady=10, cursor='hand2',
                      activebackground=BROWN2, activeforeground=WHITE
                      ).pack(side='left', expand=True, fill='x', padx=5)

        self._section_title("Today's Attendance")
        try:    records = self.db.get_today_attendance()
        except Exception: records = []
        self._build_attendance_table(records)

    def _build_attendance_table(self, records):
        cols = ('Student ID','Full Name','Class','Date','Time In','Time Out','Status')
        tree = self._make_treeview(self.content, cols,
                                   [100,160,100,100,90,90,90], height=10)
        for rec in records:
            s = rec.get('status','')
            tag = s
            tree.insert('', 'end', values=(
                rec.get('student_id',''), rec.get('full_name',''),
                rec.get('class_name',''), str(rec.get('date','')),
                str(rec.get('time_in','') or ''), str(rec.get('time_out','') or ''),
                s.upper()
            ), tags=(tag,))
        tree.tag_configure('present', foreground=SUCCESS)
        tree.tag_configure('late',    foreground=WARNING)
        tree.tag_configure('absent',  foreground=DANGER)

    # ════════════════════════════════════════════════════
    #  ATTENDANCE (face recognition)
    # ════════════════════════════════════════════════════
    def show_attendance(self):
        self.page_title.config(text="📸  Face Recognition Attendance")
        self.clear_content()
        from attendance_module import AttendancePage
        AttendancePage(self.content, self.db, self.admin['username'])

    # ════════════════════════════════════════════════════
    #  STUDENTS
    # ════════════════════════════════════════════════════
    def show_students(self):
        self.page_title.config(text="👥  Student Management")
        self.clear_content()
        from students_module import StudentsPage
        StudentsPage(self.content, self.db, self.admin['username'])

    # ════════════════════════════════════════════════════
    #  REPORTS
    # ════════════════════════════════════════════════════
    def show_reports(self):
        self.page_title.config(text="📊  Attendance Reports")
        self.clear_content()
        from reports_module import ReportsPage
        ReportsPage(self.content, self.db)

    # ════════════════════════════════════════════════════
    #  STUDENT PROFILE SEARCH
    # ════════════════════════════════════════════════════
    def show_student_profile_search(self):
        self.page_title.config(text="👤  Student Profile")
        self.clear_content()

        # Search bar
        search_row = tk.Frame(self.content, bg=BG)
        search_row.pack(fill='x', pady=(0, 12))
        tk.Label(search_row, text="Search Student:", bg=BG, fg=DARK,
                 font=(FONT, 11, 'bold')).pack(side='left', padx=(0, 8))
        sv = tk.StringVar()
        frm = tk.Frame(search_row, bg=WHITE, relief='solid', bd=1)
        search_ent = tk.Entry(frm, textvariable=sv, font=(FONT, 12),
                               bg=WHITE, fg=DARK, insertbackground=BROWN,
                               relief='flat', bd=6, width=25)
        search_ent.pack(fill='x')
        frm.pack(side='left')
        search_ent.focus()

        # Results list
        results_frame = tk.Frame(self.content, bg=BG)
        results_frame.pack(fill='both', expand=True)

        left_panel = tk.Frame(results_frame, bg=BG, width=300)
        left_panel.pack(side='left', fill='y')
        left_panel.pack_propagate(False)

        self.profile_panel = tk.Frame(results_frame, bg=BG)
        self.profile_panel.pack(side='left', fill='both', expand=True, padx=(15, 0))

        # Student list
        tk.Label(left_panel, text="Students", font=(FONT, 11, 'bold'),
                 bg=BG, fg=BROWN).pack(anchor='w', pady=(0, 5))

        cols = ('ID', 'Name', 'Class')
        style = ttk.Style()
        style.configure("Stu.Treeview", background=WHITE, foreground=DARK,
                        rowheight=30, fieldbackground=WHITE, font=(FONT, 10))
        style.configure("Stu.Treeview.Heading", background=BROWN,
                        foreground=WHITE, font=(FONT, 10, 'bold'))
        style.map("Stu.Treeview", background=[('selected', BROWN_LT)])

        list_frame = tk.Frame(left_panel, bg=BG)
        list_frame.pack(fill='both', expand=True)
        self.stu_list = ttk.Treeview(list_frame, columns=cols, show='headings',
                                      style="Stu.Treeview", height=20)
        for col, w in zip(cols, [90, 130, 80]):
            self.stu_list.heading(col, text=col)
            self.stu_list.column(col, width=w, anchor='center')
        sy = ttk.Scrollbar(list_frame, orient='vertical', command=self.stu_list.yview)
        self.stu_list.configure(yscrollcommand=sy.set)
        sy.pack(side='right', fill='y')
        self.stu_list.pack(fill='both', expand=True)

        self._all_students = self.db.get_all_students()
        self._populate_student_list(self._all_students)

        def on_search(*args):
            q = sv.get().lower()
            filtered = [s for s in self._all_students if
                        q in s['student_id'].lower() or
                        q in s['full_name'].lower() or
                        q in (s['class_name'] or '').lower()]
            self._populate_student_list(filtered)

        sv.trace('w', on_search)
        self.stu_list.bind('<<TreeviewSelect>>', self._on_student_select)

        # Show placeholder
        tk.Label(self.profile_panel, text="← Select a student to view full profile",
                 bg=BG, fg=MUTED, font=(FONT, 13)).pack(expand=True)

    def _populate_student_list(self, students):
        self.stu_list.delete(*self.stu_list.get_children())
        for s in students:
            self.stu_list.insert('', 'end', values=(
                s['student_id'], s['full_name'], s['class_name'] or ''
            ))

    def _on_student_select(self, event):
        sel = self.stu_list.selection()
        if not sel: return
        sid = self.stu_list.item(sel[0])['values'][0]
        self._show_student_profile(str(sid))

    def _show_student_profile(self, student_id):
        for w in self.profile_panel.winfo_children(): w.destroy()

        student = self.db.get_student_by_id(student_id)
        if not student:
            tk.Label(self.profile_panel, text="Student not found.",
                     bg=BG, fg=DANGER, font=(FONT, 12)).pack(pady=20)
            return

        # ── Profile Card ──────────────────────────────────
        canvas = tk.Canvas(self.profile_panel, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.profile_panel, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG)
        scroll_frame.bind('<Configure>',
                          lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)

        # Top profile section
        top = tk.Frame(scroll_frame, bg=WHITE)
        top.pack(fill='x', pady=(0, 10))
        tk.Frame(top, bg=BROWN, height=6).pack(fill='x')

        info_row = tk.Frame(top, bg=WHITE)
        info_row.pack(fill='x', padx=20, pady=15)

        # Photo
        photo_frame = tk.Frame(info_row, bg=WHITE)
        photo_frame.pack(side='left', padx=(0, 20))
        photo_lbl = tk.Label(photo_frame, bg=CREAM, width=12, height=7,
                              text="No\nPhoto", fg=MUTED, font=(FONT, 9),
                              relief='solid', bd=1)
        photo_lbl.pack()

        # Try to load photo
        try:
            if student.get('photo_path') and os.path.exists(student['photo_path']):
                img = Image.open(student['photo_path']).resize((110, 130), Image.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                photo_lbl.config(image=photo_img, text='', width=110, height=130, bd=0)
                photo_lbl.image = photo_img
        except Exception:
            pass

        # Change photo button
        def change_photo():
            path = filedialog.askopenfilename(
                filetypes=[("Image", "*.jpg *.jpeg *.png")],
                parent=self.root)
            if path:
                self.db.update_student_photo(student_id, path)
                self._show_student_profile(student_id)

        tk.Button(photo_frame, text="📷 Change Photo", command=change_photo,
                  bg=BROWN_LT, fg=WHITE, font=(FONT, 8),
                  relief='flat', cursor='hand2').pack(pady=3, fill='x')

        # Details
        details = tk.Frame(info_row, bg=WHITE)
        details.pack(side='left', fill='both', expand=True)

        name = student.get('full_name', '')
        tk.Label(details, text=name, font=(FONT, 18, 'bold'),
                 bg=WHITE, fg=BROWN).pack(anchor='w')
        tk.Label(details, text=f"ID: {student.get('student_id','')}",
                 font=(FONT, 11), bg=WHITE, fg=MUTED).pack(anchor='w')

        status = student.get('status', 'active')
        sc = SUCCESS if status == 'active' else DANGER
        tk.Label(details, text=f"● {status.upper()}",
                 font=(FONT, 10, 'bold'), bg=WHITE, fg=sc).pack(anchor='w', pady=3)

        info_items = [
            ("🏫 Class",   f"{student.get('class_name','')} - {student.get('section','')}"),
            ("📧 Email",   student.get('email','') or '—'),
            ("📱 Phone",   student.get('phone','') or '—'),
            ("📅 Joined",  str(student.get('registered_at',''))[:10]),
        ]
        for icon_lbl, val in info_items:
            r = tk.Frame(details, bg=WHITE)
            r.pack(anchor='w', pady=2)
            tk.Label(r, text=icon_lbl + ":", font=(FONT, 10, 'bold'),
                     bg=WHITE, fg=DARK, width=12, anchor='w').pack(side='left')
            tk.Label(r, text=val, font=(FONT, 10),
                     bg=WHITE, fg=MUTED).pack(side='left')

        # Action buttons row
        btn_row = tk.Frame(top, bg=WHITE)
        btn_row.pack(fill='x', padx=20, pady=(0, 15))
        self._action_btn(btn_row, "✏️ Edit",   lambda: self._edit_student(student_id), BROWN)
        self._action_btn(btn_row, "📷 Re-Capture Face", lambda: self._recapture(student_id), INFO)
        self._action_btn(btn_row, "🗑️ Delete", lambda: self._delete_student(student_id), DANGER)

        # ── Tabs: Attendance | Result ──────────────────────
        tabs_bar = tk.Frame(scroll_frame, bg=CREAM)
        tabs_bar.pack(fill='x', pady=(8, 0))
        self._profile_tab = tk.StringVar(value='attendance')
        attend_tab_content = tk.Frame(scroll_frame, bg=BG)
        result_tab_content = tk.Frame(scroll_frame, bg=BG)

        def show_tab(t):
            self._profile_tab.set(t)
            if t == 'attendance':
                at_btn.config(bg=BROWN, fg=WHITE)
                rs_btn.config(bg=CREAM, fg=MUTED)
                result_tab_content.pack_forget()
                attend_tab_content.pack(fill='both', expand=True)
            else:
                rs_btn.config(bg=BROWN, fg=WHITE)
                at_btn.config(bg=CREAM, fg=MUTED)
                attend_tab_content.pack_forget()
                result_tab_content.pack(fill='both', expand=True)

        at_btn = tk.Button(tabs_bar, text="📅  Attendance History",
                            command=lambda: show_tab('attendance'),
                            bg=BROWN, fg=WHITE, font=(FONT, 10, 'bold'),
                            relief='flat', cursor='hand2')
        at_btn.pack(side='left', expand=True, fill='x', ipady=8)

        rs_btn = tk.Button(tabs_bar, text="📝  Results & Grades",
                            command=lambda: show_tab('results'),
                            bg=CREAM, fg=MUTED, font=(FONT, 10),
                            relief='flat', cursor='hand2')
        rs_btn.pack(side='left', expand=True, fill='x', ipady=8)

        # ── Attendance History ─────────────────────────────
        self._build_student_attendance(attend_tab_content, student_id)

        # ── Results ───────────────────────────────────────
        self._build_student_results(result_tab_content, student_id, student)

        attend_tab_content.pack(fill='both', expand=True)

    def _build_student_attendance(self, parent, student_id):
        # Summary stats
        try:
            records = self.db.get_attendance(filter_student=student_id)
        except Exception:
            records = []

        total   = len(records)
        present = sum(1 for r in records if r.get('status') in ('present', 'late'))
        pct     = int((present / total * 100)) if total > 0 else 0

        stat_row = tk.Frame(parent, bg=BG)
        stat_row.pack(fill='x', pady=8)

        for title, val, color in [
            ("Total Classes", total, INFO),
            ("Present", present, SUCCESS),
            ("Absent", total - present, DANGER),
            ("Attendance %", f"{pct}%", BROWN if pct >= 75 else DANGER),
        ]:
            c = tk.Frame(stat_row, bg=WHITE)
            c.pack(side='left', expand=True, fill='both', padx=4)
            tk.Frame(c, bg=color, height=4).pack(fill='x')
            tk.Label(c, text=str(val), font=(FONT, 20, 'bold'),
                     bg=WHITE, fg=color).pack(pady=(8, 2))
            tk.Label(c, text=title, font=(FONT, 9), bg=WHITE, fg=MUTED).pack(pady=(0, 8))

        if pct < 75:
            tk.Label(parent, text="⚠️  Attendance below 75% — Attendance shortage",
                     bg='#FFF3E0', fg=WARNING, font=(FONT, 10, 'bold')).pack(fill='x', pady=4, padx=4)

        # Table
        cols = ('Date', 'Time In', 'Time Out', 'Status', 'Marked By')
        tree = self._make_treeview(parent, cols, [120, 100, 100, 100, 130], height=10)
        for rec in records:
            s = rec.get('status', '')
            tree.insert('', 'end', values=(
                str(rec.get('date', '')),
                str(rec.get('time_in', '') or ''),
                str(rec.get('time_out', '') or ''),
                s.upper(), rec.get('marked_by', '')
            ), tags=(s,))
        tree.tag_configure('present', foreground=SUCCESS)
        tree.tag_configure('late',    foreground=WARNING)
        tree.tag_configure('absent',  foreground=DANGER)

        # Export
        def export_att():
            path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                initialfile=f"attendance_{student_id}.csv",
                filetypes=[("CSV", "*.csv")])
            if path:
                import pandas as pd
                pd.DataFrame(records).to_csv(path, index=False)
                messagebox.showinfo("Exported", f"Saved to {path}")

        tk.Button(parent, text="📥 Export CSV", command=export_att,
                  bg=SUCCESS, fg=WHITE, font=(FONT, 10, 'bold'),
                  relief='flat', cursor='hand2').pack(anchor='e', padx=4, pady=5, ipady=5, ipadx=8)

    def _build_student_results(self, parent, student_id, student):
        # Results header
        hdr = tk.Frame(parent, bg=WHITE)
        hdr.pack(fill='x', pady=8)
        tk.Frame(hdr, bg=BROWN, height=4).pack(fill='x')
        tk.Label(hdr, text="📝  Academic Results & Grades",
                 font=(FONT, 12, 'bold'), bg=WHITE, fg=BROWN).pack(anchor='w', padx=15, pady=8)

        # Try to fetch results
        try:
            results = self.db.get_student_results(student_id)
        except Exception:
            results = []

        if results:
            cols = ('Subject', 'Exam Type', 'Marks', 'Max Marks', 'Grade', 'Semester', 'Date')
            tree = self._make_treeview(parent, cols,
                                       [150, 120, 80, 90, 70, 90, 110], height=8)
            total_marks = 0; max_total = 0
            for r in results:
                marks = r.get('marks', 0) or 0
                max_m = r.get('max_marks', 100) or 100
                total_marks += marks; max_total += max_m
                grade = r.get('grade') or self._calc_grade(marks, max_m)
                tree.insert('', 'end', values=(
                    r.get('subject', ''), r.get('exam_type', ''),
                    marks, max_m, grade,
                    r.get('semester', ''), str(r.get('result_date', ''))[:10]
                ), tags=(grade,))
            tree.tag_configure('A+', foreground=SUCCESS)
            tree.tag_configure('A',  foreground=SUCCESS)
            tree.tag_configure('B',  foreground=INFO)
            tree.tag_configure('C',  foreground=WARNING)
            tree.tag_configure('F',  foreground=DANGER)

            # Overall percentage
            pct = int(total_marks / max_total * 100) if max_total > 0 else 0
            sum_frame = tk.Frame(parent, bg=WHITE)
            sum_frame.pack(fill='x', pady=5)
            tk.Label(sum_frame, text=f"Overall: {total_marks}/{max_total} = {pct}%  |  Grade: {self._calc_grade(pct, 100)}",
                     font=(FONT, 12, 'bold'), bg=WHITE,
                     fg=SUCCESS if pct >= 60 else DANGER).pack(pady=8)
        else:
            # Empty state + add result button
            tk.Label(parent, text="No results found for this student.",
                     bg=BG, fg=MUTED, font=(FONT, 11)).pack(pady=15)

        # Add Result button
        tk.Button(parent, text="➕ Add Result",
                  command=lambda: self._add_result_dialog(student_id),
                  bg=BROWN, fg=WHITE, font=(FONT, 10, 'bold'),
                  relief='flat', cursor='hand2').pack(anchor='w', padx=4, pady=5, ipady=6, ipadx=10)

    def _calc_grade(self, marks, max_marks):
        pct = (marks / max_marks * 100) if max_marks > 0 else 0
        if pct >= 90: return 'A+'
        elif pct >= 80: return 'A'
        elif pct >= 70: return 'B'
        elif pct >= 60: return 'C'
        elif pct >= 50: return 'D'
        else: return 'F'

    def _add_result_dialog(self, student_id):
        win = tk.Toplevel(self.root)
        win.title("Add Result")
        win.geometry("420x500")
        win.configure(bg=BG)
        win.grab_set()

        tk.Frame(win, bg=BROWN, height=6).pack(fill='x')
        tk.Label(win, text="➕ Add Academic Result",
                 font=(FONT, 13, 'bold'), bg=BG, fg=BROWN).pack(pady=(15, 10))

        body = tk.Frame(win, bg=BG)
        body.pack(fill='x', padx=30)

        fields = {}
        for label, key in [("Subject *", 'subject'), ("Exam Type", 'exam_type'),
                            ("Marks Obtained *", 'marks'), ("Max Marks", 'max_marks'),
                            ("Semester", 'semester'), ("Date (YYYY-MM-DD)", 'result_date')]:
            tk.Label(body, text=label, bg=BG, fg=DARK, font=(FONT, 10, 'bold')).pack(anchor='w', pady=(8, 2))
            var = tk.StringVar()
            frm = tk.Frame(body, bg=WHITE, relief='solid', bd=1)
            tk.Entry(frm, textvariable=var, font=(FONT, 11),
                     bg=WHITE, fg=DARK, insertbackground=BROWN,
                     relief='flat', bd=5).pack(fill='x')
            frm.pack(fill='x')
            fields[key] = var

        fields['max_marks'].set('100')
        fields['result_date'].set(str(date.today()))

        def save():
            subject = fields['subject'].get().strip()
            if not subject:
                messagebox.showerror("Error", "Subject is required!", parent=win); return
            try:
                marks = float(fields['marks'].get() or 0)
                max_m = float(fields['max_marks'].get() or 100)
            except ValueError:
                messagebox.showerror("Error", "Marks must be numbers!", parent=win); return
            grade = self._calc_grade(marks, max_m)
            self.db.add_student_result(
                student_id, subject,
                fields['exam_type'].get(), marks, max_m, grade,
                fields['semester'].get(), fields['result_date'].get()
            )
            messagebox.showinfo("✅ Saved", "Result added successfully!", parent=win)
            win.destroy()
            self._show_student_profile(student_id)

        tk.Button(win, text="💾  Save Result", command=save,
                  bg=BROWN, fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2').pack(fill='x', padx=30, pady=15, ipady=10)

    def _edit_student(self, student_id):
        from students_module import StudentsPage
        # Open edit dialog via students module
        student = self.db.get_student_by_id(student_id)
        if student:
            from students_module import StudentsPage
            sp = StudentsPage.__new__(StudentsPage)
            sp.parent = self.content
            sp.db = self.db
            sp.admin_user = self.admin['username']
            sp._student_form_dialog(student)

    def _recapture(self, student_id):
        from students_module import StudentsPage
        student = self.db.get_student_by_id(student_id)
        if student:
            sp = StudentsPage.__new__(StudentsPage)
            sp.parent = self.content
            sp.db = self.db
            sp.admin_user = self.admin['username']
            sp._student_form_dialog(student)

    def _delete_student(self, student_id):
        if messagebox.askyesno("Confirm", f"Delete student {student_id} and all records?"):
            self.db.delete_student(student_id)
            self.db.log_activity("DELETE", self.admin['username'], f"Deleted {student_id}")
            self.show_student_profile_search()

    # ════════════════════════════════════════════════════
    #  MANAGE TEACHERS (Admin only)
    # ════════════════════════════════════════════════════
    def show_manage_teachers(self):
        self.page_title.config(text="🏫  Manage Teachers")
        self.clear_content()

        # Action bar
        act = tk.Frame(self.content, bg=BG)
        act.pack(fill='x', pady=(0, 10))
        self._action_btn(act, "➕ Add Teacher", self._add_teacher_dialog, SUCCESS)

        self._section_title("Teacher Accounts")

        # Table
        try:
            teachers = self.db.get_all_teachers()
        except Exception:
            teachers = []

        cols = ('Username', 'Full Name', 'Email', 'Phone', 'Created At')
        tree = self._make_treeview(self.content, cols, [140, 180, 200, 130, 160], height=15)
        for t in teachers:
            tree.insert('', 'end', values=(
                t.get('username',''), t.get('full_name',''),
                t.get('email',''), t.get('phone','') or '—',
                str(t.get('created_at',''))[:16]
            ))

        if not teachers:
            tk.Label(self.content,
                     text="No teachers registered yet. Click '➕ Add Teacher' to create one.",
                     bg=BG, fg=MUTED, font=(FONT, 11)).pack(pady=20)

        # Info box
        info = tk.Frame(self.content, bg='#FFF8E1', relief='solid', bd=1)
        info.pack(fill='x', pady=10)
        tk.Label(info,
                 text="ℹ️  Teachers can: Take Attendance, View Students, View & Export Reports.\n"
                      "Teachers cannot: Add/Delete Students, Manage Settings, or View Activity Log.",
                 bg='#FFF8E1', fg='#795548', font=(FONT, 9),
                 justify='left').pack(padx=12, pady=8, anchor='w')

    def _add_teacher_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Teacher Account")
        win.geometry("420x480")
        win.configure(bg=BG)
        win.grab_set()

        tk.Frame(win, bg='#E65100', height=6).pack(fill='x')
        hdr = tk.Frame(win, bg='#E65100', height=55)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🟡  Add Teacher Account",
                 font=(FONT, 13, 'bold'), bg='#E65100', fg=WHITE).pack(expand=True)
        tk.Frame(win, bg=GOLD, height=2).pack(fill='x')

        body = tk.Frame(win, bg=BG)
        body.pack(fill='x', padx=30)

        fields = {}
        for label, key, secret in [
            ("Full Name *",  'name',  False),
            ("Username *",   'user',  False),
            ("Email *",      'email', False),
            ("Phone",        'phone', False),
            ("Password *",   'pw',    True),
        ]:
            tk.Label(body, text=label, bg=BG, fg=DARK,
                     font=(FONT, 10, 'bold')).pack(anchor='w', pady=(10, 2))
            var = tk.StringVar()
            kw  = {'show': '●'} if secret else {}
            frm = tk.Frame(body, bg=WHITE, relief='solid', bd=1)
            tk.Entry(frm, textvariable=var, font=(FONT, 11),
                     bg=WHITE, fg=DARK, insertbackground=BROWN,
                     relief='flat', bd=5, **kw).pack(fill='x')
            frm.pack(fill='x')
            fields[key] = var

        def save():
            name  = fields['name'].get().strip()
            user  = fields['user'].get().strip()
            email = fields['email'].get().strip()
            phone = fields['phone'].get().strip()
            pw    = fields['pw'].get()
            if not name or not user or not email or not pw:
                messagebox.showerror("Error", "Name, Username, Email & Password are required!", parent=win)
                return
            if len(pw) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters.", parent=win)
                return
            try:
                success, msg = self.db.add_teacher(user, pw, name, email, phone)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)
                return
            if success:
                self.db.log_activity("ADD_TEACHER", self.admin['username'],
                                     f"Added teacher: {user}")
                messagebox.showinfo("✅ Added",
                    f"Teacher account created!\n\n"
                    f"Username: {user}\n"
                    f"They can now login via the 🟡 Teacher tab.", parent=win)
                win.destroy()
                self.show_manage_teachers()
            else:
                messagebox.showerror("Failed", msg, parent=win)

        tk.Button(win, text="✅  Create Teacher Account", command=save,
                  bg='#E65100', fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2').pack(fill='x', padx=30, pady=18, ipady=10)

    # ════════════════════════════════════════════════════
    #  MANAGE FEES (Admin only)
    # ════════════════════════════════════════════════════
    def show_manage_fees(self):
        self.page_title.config(text="💰  Manage Student Fees")
        self.clear_content()

        # Top actions
        act = tk.Frame(self.content, bg=BG)
        act.pack(fill='x', pady=(0, 10))
        self._action_btn(act, "➕ Add Fee Entry",  self._add_fee_dialog,    '#C62828')
        self._action_btn(act, "✅ Mark as Paid",   self._mark_fee_paid,     SUCCESS)

        # Search
        search_row = tk.Frame(self.content, bg=BG)
        search_row.pack(fill='x', pady=(0, 8))
        tk.Label(search_row, text="Search Student:", bg=BG, fg=DARK,
                 font=(FONT, 10, 'bold')).pack(side='left', padx=(0, 6))
        sv = tk.StringVar()
        frm = tk.Frame(search_row, bg=WHITE, relief='solid', bd=1)
        tk.Entry(frm, textvariable=sv, font=(FONT, 11), bg=WHITE, fg=DARK,
                 insertbackground=BROWN, relief='flat', bd=6, width=22).pack(fill='x')
        frm.pack(side='left')

        # Filter by status
        fee_filter = tk.StringVar(value='All')
        tk.Label(search_row, text="   Status:", bg=BG, fg=DARK,
                 font=(FONT, 10, 'bold')).pack(side='left', padx=(10, 6))
        for opt in ['All', 'Pending', 'Paid', 'Partial', 'Overdue']:
            tk.Radiobutton(search_row, text=opt, variable=fee_filter, value=opt,
                           bg=BG, fg=DARK, font=(FONT, 9),
                           activebackground=BG).pack(side='left', padx=4)

        self._section_hdr("All Fee Records")

        cols   = ('ID', 'Student ID', 'Student Name', 'Fee Type', 'Amount (₹)',
                  'Paid (₹)', 'Due (₹)', 'Due Date', 'Status', 'Semester')
        widths = [50, 100, 150, 140, 100, 90, 90, 100, 90, 90]
        self.fees_tree = self._make_treeview(self.content, cols, widths, height=14)

        # Load all fees
        try:
            students  = self.db.get_all_students()
            all_fees  = []
            name_map  = {s['student_id']: s['full_name'] for s in students}
            for s in students:
                for f in self.db.get_student_fees(s['student_id']):
                    f['_name'] = s['full_name']
                    all_fees.append(f)
        except Exception:
            all_fees = []
            name_map = {}

        self._all_fees_cache = all_fees

        def load_fees(*_):
            self.fees_tree.delete(*self.fees_tree.get_children())
            q   = sv.get().lower()
            flt = fee_filter.get().lower()
            for f in all_fees:
                st   = (f.get('status') or 'pending').lower()
                name = f.get('_name', '')
                sid  = f.get('student_id', '')
                if q and q not in sid.lower() and q not in name.lower(): continue
                if flt != 'all' and st != flt: continue
                amt  = float(f.get('amount') or 0)
                paid = float(f.get('paid_amount') or 0)
                due  = amt - paid
                self.fees_tree.insert('', 'end', iid=str(f['id']), values=(
                    f['id'], sid, name,
                    f.get('fee_type', ''),
                    f"₹{amt:,.2f}", f"₹{paid:,.2f}", f"₹{due:,.2f}",
                    str(f.get('due_date', '') or '—')[:10],
                    st.upper(),
                    f.get('semester', '') or '—'
                ), tags=(st,))
            self.fees_tree.tag_configure('paid',    foreground=SUCCESS)
            self.fees_tree.tag_configure('pending', foreground=WARNING)
            self.fees_tree.tag_configure('overdue', foreground=DANGER)
            self.fees_tree.tag_configure('partial', foreground=INFO)

        sv.trace('w', load_fees)
        fee_filter.trace('w', load_fees)
        load_fees()

        # Summary strip
        total_amt  = sum(float(f.get('amount') or 0) for f in all_fees)
        total_paid = sum(float(f.get('paid_amount') or 0) for f in all_fees)
        total_due  = total_amt - total_paid
        sum_box = tk.Frame(self.content, bg=WHITE)
        sum_box.pack(fill='x', pady=(8, 0))
        tk.Frame(sum_box, bg='#C62828', height=4).pack(fill='x')
        tk.Label(sum_box,
                 text=f"   Total Fees: ₹{total_amt:,.2f}   |   Collected: ₹{total_paid:,.2f}   "
                      f"|   Outstanding: ₹{total_due:,.2f}   |   Records: {len(all_fees)}",
                 font=(FONT, 11, 'bold'), bg=WHITE, fg=DARK).pack(anchor='w', pady=8)

    def _add_fee_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Fee Entry")
        win.geometry("460x560")
        win.configure(bg=BG)
        win.grab_set()

        tk.Frame(win, bg='#C62828', height=6).pack(fill='x')
        hdr = tk.Frame(win, bg='#C62828', height=55); hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="💰  Add Fee Entry", font=(FONT, 13, 'bold'),
                 bg='#C62828', fg=WHITE).pack(expand=True)
        tk.Frame(win, bg=GOLD, height=2).pack(fill='x')

        body = tk.Frame(win, bg=BG); body.pack(fill='x', padx=30)
        fields = {}

        def _field(label, key, default=''):
            tk.Label(body, text=label, bg=BG, fg=DARK,
                     font=(FONT, 10, 'bold')).pack(anchor='w', pady=(10, 2))
            var = tk.StringVar(value=default)
            frm = tk.Frame(body, bg=WHITE, relief='solid', bd=1)
            tk.Entry(frm, textvariable=var, font=(FONT, 11),
                     bg=WHITE, fg=DARK, insertbackground=BROWN,
                     relief='flat', bd=5).pack(fill='x')
            frm.pack(fill='x')
            fields[key] = var

        # Student dropdown
        tk.Label(body, text="Student *", bg=BG, fg=DARK,
                 font=(FONT, 10, 'bold')).pack(anchor='w', pady=(10, 2))
        try:    students = self.db.get_all_students()
        except: students = []
        stu_opts = [f"{s['student_id']} — {s['full_name']}" for s in students]
        stu_var  = tk.StringVar()
        stu_cb   = ttk.Combobox(body, textvariable=stu_var, values=stu_opts,
                                 font=(FONT, 10), state='readonly')
        stu_cb.pack(fill='x')

        _field("Fee Type *  (e.g. Tuition, Exam, Library)", 'fee_type')
        _field("Total Amount (₹) *",    'amount')
        _field("Paid Amount (₹)",        'paid_amount', '0')
        _field("Due Date  (YYYY-MM-DD)", 'due_date')
        _field("Semester",               'semester')
        _field("Academic Year",          'academic_year', '2024-25')
        _field("Receipt No",             'receipt_no')

        tk.Label(body, text="Status", bg=BG, fg=DARK,
                 font=(FONT, 10, 'bold')).pack(anchor='w', pady=(10, 2))
        status_var = tk.StringVar(value='pending')
        status_cb  = ttk.Combobox(body, textvariable=status_var,
                                   values=['pending', 'paid', 'partial', 'overdue'],
                                   font=(FONT, 10), state='readonly')
        status_cb.pack(fill='x')

        def save():
            stu_sel = stu_var.get()
            if not stu_sel:
                messagebox.showerror("Error", "Select a student!", parent=win); return
            sid = stu_sel.split(' — ')[0].strip()
            ft  = fields['fee_type'].get().strip()
            if not ft:
                messagebox.showerror("Error", "Fee type is required!", parent=win); return
            try:
                amt  = float(fields['amount'].get() or 0)
                paid = float(fields['paid_amount'].get() or 0)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number!", parent=win); return
            due_str   = fields['due_date'].get().strip() or None
            paid_date = None
            if status_var.get() == 'paid' and paid >= amt:
                paid_date = str(date.today())
            try:
                self.db.add_fee(
                    student_id=sid, fee_type=ft, amount=amt, due_date=due_str,
                    semester=fields['semester'].get(), academic_year=fields['academic_year'].get(),
                    receipt_no=fields['receipt_no'].get(), remarks='',
                    paid_amount=paid, paid_date=paid_date, status=status_var.get()
                )
                self.db.log_activity("ADD_FEE", self.admin['username'],
                                     f"Added {ft} ₹{amt} for {sid}")
                messagebox.showinfo("✅ Added", "Fee entry added successfully!", parent=win)
                win.destroy()
                self.show_manage_fees()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        tk.Button(win, text="💾  Save Fee Entry", command=save,
                  bg='#C62828', fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2').pack(fill='x', padx=30, pady=15, ipady=10)

    def _mark_fee_paid(self):
        sel = self.fees_tree.selection() if hasattr(self, 'fees_tree') else []
        if not sel:
            messagebox.showwarning("Select", "Please select a fee record first."); return

        fee_id = int(sel[0])
        # Find fee in cache
        fee = next((f for f in getattr(self, '_all_fees_cache', []) if f['id'] == fee_id), None)
        if not fee:
            messagebox.showerror("Error", "Fee record not found."); return

        amt = float(fee.get('amount') or 0)
        try:
            self.db.update_fee_payment(
                fee_id, paid_amount=amt,
                paid_date=str(date.today()),
                status='paid',
                receipt_no=fee.get('receipt_no', '')
            )
            self.db.log_activity("FEE_PAID", self.admin['username'],
                                 f"Marked fee #{fee_id} as paid for {fee.get('student_id')}")
            messagebox.showinfo("✅ Updated", "Fee marked as PAID successfully!")
            self.show_manage_fees()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ════════════════════════════════════════════════════
    #  ACTIVITY LOG
    # ════════════════════════════════════════════════════
    def show_activity_log(self):
        self.page_title.config(text="📋  Activity Log")
        self.clear_content()
        try: logs = self.db.get_activity_log(200)
        except Exception: logs = []
        cols = ('Action','Performed By','Details','Timestamp')
        tree = self._make_treeview(self.content, cols, [150, 130, 380, 200])
        for log in logs:
            tree.insert('', 'end', values=(
                log['action'], log['performed_by'],
                log['details'], str(log['timestamp'])))

    # ════════════════════════════════════════════════════
    #  SETTINGS
    # ════════════════════════════════════════════════════
    def show_settings(self):
        self.page_title.config(text="⚙️  Settings")
        self.clear_content()
        from settings_module import SettingsPage
        SettingsPage(self.content, self.db, self.admin)

    # ════════════════════════════════════════════════════
    #  LOGOUT
    # ════════════════════════════════════════════════════
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.log_activity("LOGOUT", self.admin['username'], "Logged out")
            self.root.destroy()
            import tkinter as tk
            from login import LoginWindow
            r = tk.Tk()
            LoginWindow(r)
            r.mainloop()