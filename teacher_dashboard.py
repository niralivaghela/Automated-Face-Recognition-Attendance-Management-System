"""
╔══════════════════════════════════════════════════════════════╗
║   VANITA VISHRAM WOMEN'S UNIVERSITY                          ║
║   Advanced Teacher Dashboard — Brown & White Edition         ║
║   Version 3.0 | Full Faculty Management System               ║
╚══════════════════════════════════════════════════════════════╝

Features:
  • Brown & White luxury theme with warm accents
  • Live Face Recognition Attendance
  • Manual & Bulk Attendance Entry
  • Assignment & Homework Management
  • Internal Marks & Grade Entry
  • Student Performance Analytics
  • Low Attendance Detector & WhatsApp Alerts
  • Timetable with Lecture Notes
  • Leave Application Management
  • Student Counselling Log
  • Class Announcements
  • Teacher Profile & Settings
  • Export: CSV / Excel / PDF
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import date, datetime, timedelta
import threading
import os
import random

from database import DatabaseManager

# ══════════════════════════════════════════════════════════════
#  BROWN & WHITE LUXURY COLOUR PALETTE
# ══════════════════════════════════════════════════════════════
C = {
    # Backgrounds
    'bg':           '#FAF7F2',   # warm off-white page
    'bg2':          '#F3EDE3',   # slightly deeper warm white
    'bg3':          '#EDE4D6',   # panel background
    'sidebar':      '#4A2C0A',   # rich dark brown sidebar
    'sidebar2':     '#5C3810',   # hover brown
    'sidebar3':     '#3A1F05',   # active/pressed

    # Cards
    'card':         '#FFFFFF',   # pure white card
    'card2':        '#FDF9F4',   # warm white card
    'card_border':  '#E8DDD0',   # card border

    # Browns
    'brown':        '#6B3A1F',   # primary brown
    'brown2':       '#8B4513',   # saddle brown accent
    'brown3':       '#A0522D',   # sienna
    'brown_light':  '#C68642',   # light warm brown
    'brown_pale':   '#D2A679',   # pale brown

    # Text
    'text':         '#2C1810',   # very dark brown text
    'text2':        '#5C3A28',   # medium brown text
    'text3':        '#8B6A55',   # muted brown text
    'text4':        '#B89880',   # light muted text
    'sidebar_text': '#F5E6D5',   # sidebar light text
    'sidebar_dim':  '#C4A882',   # sidebar dim text

    # Accents
    'gold':         '#C8860A',   # warm gold
    'gold2':        '#E6A020',   # bright gold
    'cream':        '#FFF8EE',   # cream highlight

    # Status colours
    'green':        '#2D7A3A',
    'green2':       '#3A9A4A',
    'green_bg':     '#EBF7EC',
    'red':          '#C0392B',
    'red2':         '#E74C3C',
    'red_bg':       '#FDECEA',
    'orange':       '#D4610A',
    'orange_bg':    '#FEF0E6',
    'blue':         '#1A5C8A',
    'blue2':        '#2980B9',
    'blue_bg':      '#E8F4FD',
    'purple':       '#6B3D8A',
    'purple_bg':    '#F3EDF8',
    'teal':         '#1A7A6A',
    'teal_bg':      '#E8F6F3',

    # Misc
    'shadow':       '#D4C4B0',
    'divider':      '#E8DDD0',
    'white':        '#FFFFFF',
    'hover_card':   '#FFF5EB',
}

# Fonts — warm, academic feel
FT = {
    'display':  ('Georgia', 24, 'bold'),
    'heading':  ('Georgia', 16, 'bold'),
    'subhead':  ('Georgia', 12, 'bold'),
    'body':     ('Segoe UI', 10),
    'body_b':   ('Segoe UI', 10, 'bold'),
    'small':    ('Segoe UI', 9),
    'small_b':  ('Segoe UI', 9, 'bold'),
    'mono':     ('Consolas', 10),
    'nav':      ('Segoe UI', 10, 'bold'),
    'stat':     ('Georgia', 28, 'bold'),
}

# Departments
DEPARTMENTS = {
    'BBA':     {'full': 'Bachelor of Business Administration', 'sems': 6,  'sections': ['A','B','C'], 'color': C['orange']},
    'BCA':     {'full': 'Bachelor of Computer Applications',   'sems': 6,  'sections': ['A','B'],    'color': C['blue']},
    'BSc.IT':  {'full': 'Bachelor of Science (Information Technology)', 'sems': 6, 'sections': ['A','B'], 'color': C['teal']},
    'B.Pharm': {'full': 'Bachelor of Pharmacy',               'sems': 8,  'sections': ['A'],         'color': C['purple']},
    'BCom':    {'full': 'Bachelor of Commerce',               'sems': 6,  'sections': ['A','B','C'], 'color': C['green']},
    'BA':      {'full': 'Bachelor of Arts',                   'sems': 6,  'sections': ['A','B'],     'color': C['brown3']},
    'BSc':     {'full': 'Bachelor of Science',                'sems': 6,  'sections': ['A','B'],     'color': C['gold']},
    'BEd':     {'full': 'Bachelor of Education',              'sems': 4,  'sections': ['A'],         'color': C['green2']},
    'MBA':     {'full': 'Master of Business Administration',  'sems': 4,  'sections': ['A','B'],     'color': C['red']},
    'MCA':     {'full': 'Master of Computer Applications',    'sems': 6,  'sections': ['A','B'],     'color': C['blue2']},
}

SUBJECTS = {
    'BBA':    ['Business Management','Financial Accounting','Business Economics','Marketing Management',
               'Human Resource Management','Business Law','Entrepreneurship','Strategic Management'],
    'BCA':    ['Python Programming','Database Management','Web Development','Data Structures & Algorithms',
               'Operating Systems','Computer Networks','Artificial Intelligence','Software Engineering'],
    'BSc.IT': ['C++ Programming','Java Programming','PHP & MySQL','Linux Administration',
               'Cyber Security','Cloud Computing','Mobile App Development','IoT'],
    'B.Pharm':['Pharmacology I','Medicinal Chemistry','Pharmaceutics','Pharmacy Practice',
               'Biochemistry','Microbiology','Pharmacognosy','Clinical Pharmacy'],
    'BCom':   ['Financial Accounting','Business Statistics','Corporate Law','Auditing',
               'Income Tax','Cost Accounting','Financial Management','E-Commerce'],
    'BA':     ['English Literature','History of India','Political Science','Sociology',
               'Psychology','Philosophy','Geography','Hindi Literature'],
    'BSc':    ['Physics','Chemistry','Mathematics','Biology','Zoology','Botany','Statistics','Computer Science'],
    'BEd':    ['Educational Psychology','Teaching Methods','Curriculum Design',
               'School Management','Pedagogy','Assessment & Evaluation'],
    'MBA':    ['Strategic Management','Operations Management','Research Methodology',
               'Leadership & OB','Digital Marketing','Financial Management','Business Analytics','Supply Chain'],
    'MCA':    ['Advanced Python','Machine Learning','Cloud Computing','Cybersecurity',
               'Big Data Analytics','DevOps','Blockchain','Advanced DBMS'],
}

EXAM_TYPES = ['Unit Test 1', 'Unit Test 2', 'Mid Sem', 'End Sem', 'Assignment', 'Practical', 'Viva', 'Project']
LEAVE_TYPES = ['Sick Leave', 'Casual Leave', 'Emergency Leave', 'Personal Leave', 'Event/Duty Leave']


# ══════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ══════════════════════════════════════════════════════════════

def animate_count(lbl, target, color, prefix='', suffix='', steps=25, ms=30):
    vals = [int(target * i / steps) for i in range(steps+1)]
    def step(i=0):
        if i <= steps:
            lbl.config(text=f"{prefix}{vals[i]}{suffix}", fg=color)
            lbl.after(ms, lambda: step(i+1))
    lbl.after(50, step)


def styled_entry(parent, var, width=20, show=None):
    kw = dict(textvariable=var, width=width, bg=C['bg2'], fg=C['text'],
              insertbackground=C['brown'], font=FT['body'], relief='flat',
              highlightthickness=1, highlightbackground=C['card_border'],
              highlightcolor=C['brown2'])
    if show:
        kw['show'] = show
    e = tk.Entry(parent, **kw)
    e.bind('<FocusIn>',  lambda ev: e.config(highlightbackground=C['brown2']))
    e.bind('<FocusOut>', lambda ev: e.config(highlightbackground=C['card_border']))
    return e


def styled_combo(parent, var, values, width=18, state='readonly'):
    style = ttk.Style()
    style.configure('Brown.TCombobox', fieldbackground=C['bg2'], background=C['bg2'],
                    foreground=C['text'], selectbackground=C['brown2'], selectforeground='white')
    c = ttk.Combobox(parent, textvariable=var, values=values, width=width,
                     state=state, style='Brown.TCombobox', font=FT['body'])
    return c


def label_entry_row(parent, label_text, var, row, col=0, width=20, combo_vals=None, span=1):
    """Grid-based label + entry pair."""
    tk.Label(parent, text=label_text, font=FT['small_b'], bg=C['card'],
             fg=C['text3'], anchor='e').grid(row=row, column=col*2,
             sticky='e', padx=(10,6), pady=7)
    if combo_vals is not None:
        w = styled_combo(parent, var, combo_vals, width=width)
    else:
        w = styled_entry(parent, var, width=width)
    w.grid(row=row, column=col*2+1, sticky='w', padx=(0,20), pady=7, columnspan=span)
    return w


def section_header(parent, text, color=None, icon=''):
    color = color or C['brown']
    f = tk.Frame(parent, bg=C['card'])
    f.pack(fill='x', padx=0, pady=0)
    # Accent bar
    tk.Frame(f, bg=color, height=3).pack(fill='x')
    inner = tk.Frame(f, bg=C['card'])
    inner.pack(fill='x')
    tk.Label(inner, text=f'{icon}  {text}' if icon else text,
             font=FT['subhead'], bg=C['card'], fg=color,
             pady=10, padx=15).pack(side='left')
    return inner


def card_frame(parent, pady=0, padx=0):
    """White card with shadow border."""
    outer = tk.Frame(parent, bg=C['shadow'], bd=0)
    inner = tk.Frame(outer, bg=C['card'], bd=0)
    inner.pack(fill='both', expand=True, padx=1, pady=1)
    return outer, inner


def action_btn(parent, text, cmd, bg, fg='white', padx=18, pady=8, font=None):
    btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                    font=font or FT['body_b'], relief='flat', cursor='hand2',
                    activebackground=_darken(bg), activeforeground=fg,
                    padx=padx, pady=pady, bd=0)
    btn.bind('<Enter>', lambda e: btn.config(bg=_lighten(bg)))
    btn.bind('<Leave>', lambda e: btn.config(bg=bg))
    return btn


def _lighten(hex_color, amt=0.12):
    try:
        h = hex_color.lstrip('#')
        r,g,b = [int(h[i:i+2],16) for i in (0,2,4)]
        return f'#{min(255,int(r+(255-r)*amt)):02x}{min(255,int(g+(255-g)*amt)):02x}{min(255,int(b+(255-b)*amt)):02x}'
    except: return hex_color

def _darken(hex_color, amt=0.12):
    try:
        h = hex_color.lstrip('#')
        r,g,b = [int(h[i:i+2],16) for i in (0,2,4)]
        return f'#{max(0,int(r*(1-amt))):02x}{max(0,int(g*(1-amt))):02x}{max(0,int(b*(1-amt))):02x}'
    except: return hex_color


def make_tree(parent, cols, widths, height=12, show='headings'):
    style = ttk.Style()
    style.configure('Brown.Treeview',
                    background=C['white'], foreground=C['text'],
                    rowheight=30, fieldbackground=C['white'],
                    font=FT['body'])
    style.configure('Brown.Treeview.Heading',
                    background=C['brown'], foreground=C['white'],
                    font=FT['body_b'], relief='flat')
    style.map('Brown.Treeview',
              background=[('selected', C['brown2'])],
              foreground=[('selected', C['white'])])

    frame = tk.Frame(parent, bg=C['bg3'])
    tree = ttk.Treeview(frame, columns=cols, show=show,
                         style='Brown.Treeview', height=height)
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor='center', minwidth=50)

    sy = ttk.Scrollbar(frame, orient='vertical',   command=tree.yview)
    sx = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
    sy.pack(side='right', fill='y')
    sx.pack(side='bottom', fill='x')
    tree.pack(fill='both', expand=True)

    # Alternating row tags
    tree.tag_configure('odd',  background='#FDF9F4')
    tree.tag_configure('even', background=C['white'])
    tree.tag_configure('present', foreground=C['green'])
    tree.tag_configure('absent',  foreground=C['red'])
    tree.tag_configure('late',    foreground=C['orange'])

    return frame, tree


def scrollable_page(parent):
    """Returns a scrollable inner frame."""
    canvas = tk.Canvas(parent, bg=C['bg'], highlightthickness=0)
    scroll = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scroll.set)
    scroll.pack(side='right', fill='y')
    canvas.pack(fill='both', expand=True)
    inner = tk.Frame(canvas, bg=C['bg'])
    win = canvas.create_window((0,0), window=inner, anchor='nw')
    def _cfg(e): canvas.configure(scrollregion=canvas.bbox('all'))
    def _resize(e): canvas.itemconfig(win, width=e.width)
    inner.bind('<Configure>', _cfg)
    canvas.bind('<Configure>', _resize)
    canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(-1*(e.delta//120), 'units'))
    return inner


# ══════════════════════════════════════════════════════════════
#  TEACHER DASHBOARD  — MAIN CLASS
# ══════════════════════════════════════════════════════════════

class TeacherDashboard:
    def __init__(self, root, teacher_info):
        self.root       = root
        self.teacher    = teacher_info
        self.db         = DatabaseManager()
        self.curr_page  = None
        self.live_on    = False
        self.clock_var  = tk.StringVar()
        self.dept_var   = tk.StringVar(value='BCA')
        self.sem_var    = tk.StringVar(value='1')
        self.sec_var    = tk.StringVar(value='A')
        self.sub_var    = tk.StringVar()
        self._setup_window()
        self._apply_ttk_styles()
        self._build_layout()
        self._start_clock()
        self._show_page('dashboard')

    # ── WINDOW ────────────────────────────────────────────────
    def _setup_window(self):
        name = self.teacher.get('full_name', self.teacher.get('username','Teacher'))
        self.root.title(f"Teacher Portal  •  {name}  •  Vanita Vishram Women's University")
        self.root.geometry('1400x820')
        self.root.minsize(1100, 680)
        self.root.configure(bg=C['bg'])
        try: self.root.state('zoomed')
        except: pass

    def _apply_ttk_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TNotebook',      background=C['bg'],    borderwidth=0)
        s.configure('TNotebook.Tab',  background=C['bg3'],   foreground=C['text3'],
                    font=FT['body_b'], padding=[16,8])
        s.map('TNotebook.Tab',
              background=[('selected', C['brown'])],
              foreground=[('selected', C['white'])])
        s.configure('TScrollbar', background=C['bg3'], troughcolor=C['bg2'],
                    arrowcolor=C['brown2'])
        s.configure('TSeparator', background=C['divider'])

    # ── MASTER LAYOUT ─────────────────────────────────────────
    def _build_layout(self):
        # Header
        self._build_header()
        # Body
        body = tk.Frame(self.root, bg=C['bg'])
        body.pack(fill='both', expand=True)
        self.sidebar    = tk.Frame(body, bg=C['sidebar'], width=240)
        self.sidebar.pack(fill='y', side='left')
        self.sidebar.pack_propagate(False)
        self.page_area  = tk.Frame(body, bg=C['bg'])
        self.page_area.pack(fill='both', expand=True)
        self._build_sidebar()

    # ── HEADER ────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C['brown'], height=68)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        # Left — logo + title
        left = tk.Frame(hdr, bg=C['brown'])
        left.pack(side='left', padx=18, pady=10)
        logo = tk.Label(left, text='🎓', font=('Segoe UI',28), bg=C['brown2'],
                        width=2, relief='flat')
        logo.pack(side='left')
        t = tk.Frame(left, bg=C['brown'])
        t.pack(side='left', padx=12)
        tk.Label(t, text='VANITA VISHRAM WOMEN\'S UNIVERSITY',
                 font=('Georgia',13,'bold'), bg=C['brown'], fg=C['cream']).pack(anchor='w')
        tk.Label(t, text='Faculty Management & Online Attendance Portal',
                 font=FT['small'], bg=C['brown'], fg=C['brown_pale']).pack(anchor='w')

        # Right — clock + name + logout
        right = tk.Frame(hdr, bg=C['brown'])
        right.pack(side='right', padx=18)

        tk.Button(right, text='⏻  Logout', command=self._logout,
                  bg=C['sidebar3'], fg=C['cream'], font=FT['body_b'],
                  relief='flat', cursor='hand2', padx=14, pady=7,
                  activebackground=C['sidebar'], activeforeground=C['cream']
                  ).pack(side='right', pady=18)

        tk.Label(right, textvariable=self.clock_var, font=('Consolas',11,'bold'),
                 bg=C['brown'], fg=C['gold2']).pack(side='right', padx=20, pady=18)

        name = self.teacher.get('full_name', self.teacher.get('username','Teacher'))
        tk.Label(right, text=f'👩‍🏫  Prof. {name}',
                 font=FT['body_b'], bg=C['brown'], fg=C['cream']).pack(side='right', padx=10, pady=18)

        # Online dot
        dot_f = tk.Frame(right, bg=C['brown'])
        dot_f.pack(side='right')
        self._dot = tk.Label(dot_f, text='●', font=('Segoe UI',10),
                              bg=C['brown'], fg=C['green2'])
        self._dot.pack()
        self._pulse_dot()

    def _pulse_dot(self, on=True):
        try:
            self._dot.config(fg=C['green2'] if on else C['brown'])
            self.root.after(900, lambda: self._pulse_dot(not on))
        except: pass

    # ── SIDEBAR ───────────────────────────────────────────────
    def _build_sidebar(self):
        # Teacher avatar
        av = tk.Frame(self.sidebar, bg=C['sidebar2'], pady=20)
        av.pack(fill='x')
        tk.Label(av, text='👩‍🏫', font=('Segoe UI',40), bg=C['sidebar2']).pack()
        name = self.teacher.get('full_name', 'Teacher')
        tk.Label(av, text=name, font=('Georgia',11,'bold'),
                 bg=C['sidebar2'], fg=C['cream'], wraplength=180).pack()
        dept_disp = self.teacher.get('department', 'Faculty')
        tk.Label(av, text=dept_disp, font=FT['small'],
                 bg=C['sidebar2'], fg=C['brown_pale']).pack()

        tk.Frame(self.sidebar, bg=C['sidebar3'], height=1).pack(fill='x', pady=5)

        # Navigation items
        nav = [
            ('dashboard',     '📊', 'Dashboard'),
            ('attendance',    '✅', 'Take Attendance'),
            ('live',          '🎥', 'Live Face Scan'),
            ('manual',        '📝', 'Manual Entry'),
            ('bulk',          '📋', 'Bulk Upload'),
            ('students',      '👩‍🎓', 'My Students'),
            ('marks',         '📊', 'Marks & Grades'),
            ('assignments',   '📚', 'Assignments'),
            ('counselling',   '💬', 'Student Counselling'),
            ('leave',         '📅', 'Leave Management'),
            ('timetable',     '🗓️', 'Timetable'),
            ('announcements', '📢', 'Announcements'),
            ('reports',       '📈', 'Reports'),
            ('profile',       '👤', 'My Profile'),
        ]

        self._nav_widgets = {}
        self._nav_canvas  = tk.Canvas(self.sidebar, bg=C['sidebar'],
                                       highlightthickness=0)
        nav_scroll = ttk.Scrollbar(self.sidebar, orient='vertical',
                                    command=self._nav_canvas.yview)
        self._nav_canvas.configure(yscrollcommand=nav_scroll.set)
        self._nav_canvas.pack(side='left', fill='both', expand=True)
        nav_scroll.pack(side='right', fill='y')

        nav_frame = tk.Frame(self._nav_canvas, bg=C['sidebar'])
        self._nav_canvas.create_window((0,0), window=nav_frame, anchor='nw')
        nav_frame.bind('<Configure>',
                       lambda e: self._nav_canvas.configure(
                           scrollregion=self._nav_canvas.bbox('all')))

        for key, icon, label in nav:
            self._make_nav_btn(nav_frame, key, icon, label)

        # Date at bottom
        tk.Frame(nav_frame, bg=C['sidebar3'], height=1).pack(fill='x', pady=8)
        tk.Label(nav_frame, text=f"📅  {date.today().strftime('%d %B %Y')}",
                 font=FT['small'], bg=C['sidebar'], fg=C['sidebar_dim']).pack(pady=5)
        tk.Label(nav_frame, text='Vanita Vishram Women\'s Univ.',
                 font=('Segoe UI',8), bg=C['sidebar'], fg=C['sidebar3']).pack()

    def _make_nav_btn(self, parent, key, icon, label):
        frame = tk.Frame(parent, bg=C['sidebar'], cursor='hand2')
        frame.pack(fill='x', padx=8, pady=1)
        il = tk.Label(frame, text=icon, font=('Segoe UI',13),
                      bg=C['sidebar'], fg=C['brown_pale'], width=3)
        il.pack(side='left', pady=10, padx=(8,0))
        tl = tk.Label(frame, text=label, font=FT['nav'],
                      bg=C['sidebar'], fg=C['sidebar_text'], anchor='w')
        tl.pack(side='left', pady=10, padx=8, fill='x', expand=True)
        self._nav_widgets[key] = (frame, il, tl)

        def click(*_): self._show_page(key)
        def enter(*_):
            if self.curr_page != key:
                frame.config(bg=C['sidebar2']); il.config(bg=C['sidebar2']); tl.config(bg=C['sidebar2'])
        def leave(*_):
            if self.curr_page != key:
                frame.config(bg=C['sidebar']); il.config(bg=C['sidebar']); tl.config(bg=C['sidebar'])
        for w in (frame, il, tl):
            w.bind('<Button-1>', click)
            w.bind('<Enter>', enter)
            w.bind('<Leave>', leave)

    def _highlight_nav(self, active):
        for key, (f, il, tl) in self._nav_widgets.items():
            if key == active:
                f.config(bg=C['brown2']); il.config(bg=C['brown2']); tl.config(bg=C['brown2'], fg=C['white'])
            else:
                f.config(bg=C['sidebar']); il.config(bg=C['sidebar']); tl.config(bg=C['sidebar'], fg=C['sidebar_text'])

    # ── PAGE ROUTER ───────────────────────────────────────────
    def _show_page(self, key):
        if self.live_on and key != 'live':
            self._stop_live()
        self.curr_page = key
        self._highlight_nav(key)
        for w in self.page_area.winfo_children():
            w.destroy()
        {
            'dashboard':     self._pg_dashboard,
            'attendance':    self._pg_attendance,
            'live':          self._pg_live,
            'manual':        self._pg_manual,
            'bulk':          self._pg_bulk,
            'students':      self._pg_students,
            'marks':         self._pg_marks,
            'assignments':   self._pg_assignments,
            'counselling':   self._pg_counselling,
            'leave':         self._pg_leave,
            'timetable':     self._pg_timetable,
            'announcements': self._pg_announcements,
            'reports':       self._pg_reports,
            'profile':       self._pg_profile,
        }.get(key, self._pg_dashboard)()

    # ── PAGE HEADER ───────────────────────────────────────────
    def _pg_header(self, title, subtitle='', color=None):
        color = color or C['brown']
        hdr = tk.Frame(self.page_area, bg=C['bg'], padx=25, pady=18)
        hdr.pack(fill='x')
        tk.Label(hdr, text=title, font=('Georgia',20,'bold'),
                 bg=C['bg'], fg=color).pack(side='left')
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FT['body'],
                     bg=C['bg'], fg=C['text3']).pack(side='right', pady=8)
        tk.Frame(self.page_area, bg=color, height=2).pack(fill='x', padx=25)

    # ══════════════════════════════════════════════════════════
    #  PAGE 1 — DASHBOARD
    # ══════════════════════════════════════════════════════════
    def _pg_dashboard(self):
        name = self.teacher.get('full_name','Teacher')
        today_str = datetime.now().strftime('%A, %d %B %Y')
        self._pg_header('📊  Dashboard', today_str)

        main = scrollable_page(self.page_area)

        # ── Welcome Banner ──
        banner = tk.Frame(main, bg=C['brown'], pady=22)
        banner.pack(fill='x', padx=25, pady=(15,0))
        tk.Label(banner, text=f'   Welcome back, Prof. {name}! 🌸',
                 font=('Georgia',16,'bold'), bg=C['brown'], fg=C['cream']).pack(side='left')
        tk.Label(banner, text=f'  {today_str}   ',
                 font=FT['body'], bg=C['brown'], fg=C['brown_pale']).pack(side='right')

        # ── Stats Row ──
        try:
            stats = self.db.get_attendance_stats()
        except:
            stats = {'total_students':0,'present_today':0,'absent_today':0,'late_today':0}

        stat_row = tk.Frame(main, bg=C['bg'])
        stat_row.pack(fill='x', padx=25, pady=15)

        stat_data = [
            ('Total Students', stats.get('total_students',0), C['blue'],   '👩‍🎓', C['blue_bg']),
            ('Present Today',  stats.get('present_today',0),  C['green'],  '✅',  C['green_bg']),
            ('Absent Today',   stats.get('absent_today',0),   C['red'],    '❌',  C['red_bg']),
            ('Late Today',     stats.get('late_today',0),     C['orange'], '⏰',  C['orange_bg']),
        ]
        for title, val, color, icon, bg_c in stat_data:
            outer, card = card_frame(stat_row)
            outer.pack(side='left', expand=True, fill='both', padx=6)
            tk.Frame(card, bg=color, height=4).pack(fill='x')
            inner = tk.Frame(card, bg=C['card'], padx=20, pady=15)
            inner.pack(fill='both', expand=True)
            top = tk.Frame(inner, bg=C['card'])
            top.pack(fill='x')
            tk.Label(top, text=icon, font=('Segoe UI',24),
                     bg=bg_c, fg=color, width=3, pady=4).pack(side='left')
            tk.Label(top, text=title, font=FT['small_b'],
                     bg=C['card'], fg=C['text3']).pack(side='left', padx=12)
            num = tk.Label(inner, text='0', font=FT['stat'], bg=C['card'], fg=color)
            num.pack(anchor='w', pady=(8,0))
            animate_count(num, val, color)

        # ── Two column row ──
        two_col = tk.Frame(main, bg=C['bg'])
        two_col.pack(fill='x', padx=25, pady=10)
        left_col  = tk.Frame(two_col, bg=C['bg'])
        left_col.pack(side='left', fill='both', expand=True, padx=(0,8))
        right_col = tk.Frame(two_col, bg=C['bg'])
        right_col.pack(side='left', fill='both', expand=True, padx=(8,0))

        # Dept overview card
        outer, dc = card_frame(left_col)
        outer.pack(fill='both', expand=True)
        section_header(dc, 'Department Attendance Overview', C['brown'], '🏛️')
        for dept, info in list(DEPARTMENTS.items()):
            r = tk.Frame(dc, bg=C['card'])
            r.pack(fill='x', padx=15, pady=3)
            col_c = info['color']
            tk.Label(r, text=dept, font=FT['small_b'],
                     bg=col_c, fg='white', width=9, pady=3).pack(side='left')
            pct = random.randint(70,98)
            bar_bg = tk.Frame(r, bg=C['bg3'], height=14, width=180)
            bar_bg.pack(side='left', padx=8)
            bar_bg.pack_propagate(False)
            fill = tk.Frame(bar_bg, bg=col_c, height=14, width=int(1.8*pct))
            fill.place(x=0, y=0, relheight=1)
            tk.Label(r, text=f'{pct}%', font=('Consolas',9,'bold'),
                     bg=C['card'], fg=col_c, width=5).pack(side='left')

        # Quick Actions
        outer2, qc = card_frame(right_col)
        outer2.pack(fill='both', expand=True)
        section_header(qc, 'Quick Actions', C['brown2'], '⚡')
        actions = [
            ('🎥  Start Live Face Scan',      'live',         C['red']),
            ('✅  Take Attendance',            'attendance',   C['green']),
            ('📝  Manual Entry',              'manual',       C['blue']),
            ('📋  Bulk Upload Attendance',    'bulk',         C['brown3']),
            ('📊  Enter Marks / Grades',      'marks',        C['purple']),
            ('📚  Post Assignment',           'assignments',  C['orange']),
            ('💬  Student Counselling Log',   'counselling',  C['teal']),
            ('📅  Apply for Leave',           'leave',        C['brown_light']),
        ]
        for label, page, bg_c in actions:
            btn = action_btn(qc, label, lambda p=page: self._show_page(p),
                             bg=bg_c, padx=12, pady=7)
            btn.pack(fill='x', padx=15, pady=3)

        # ── Recent Attendance ──
        outer3, rc = card_frame(main)
        outer3.pack(fill='x', padx=25, pady=(10,5))
        section_header(rc, "Today's Recent Attendance", C['brown'], '📋')
        cols = ('Student ID', 'Name', 'Class', 'Time In', 'Status')
        widths = [120, 180, 160, 110, 100]
        tf, tree = make_tree(rc, cols, widths, height=6)
        tf.pack(fill='x', padx=10, pady=(0,10))
        try:
            recs = self.db.get_today_attendance()[:10]
            for i, rec in enumerate(recs):
                s = rec.get('status','')
                tree.insert('', 'end', values=(
                    rec.get('student_id',''), rec.get('full_name',''),
                    rec.get('class_name',''), str(rec.get('time_in','')), s.upper()
                ), tags=(s, 'odd' if i%2 else 'even'))
        except:
            tree.insert('', 'end', values=('—','No records today','—','—','—'))

        # ── Low Attendance Alert Strip ──
        try:
            all_students = self.db.get_all_students()
            low_count = 0
            for s in all_students[:20]:  # sample check
                try:
                    summ = self.db.get_student_attendance_summary(s['student_id'])
                    if summ['total'] > 0 and summ['percentage'] < 75:
                        low_count += 1
                except: pass
            if low_count > 0:
                alert = tk.Frame(main, bg=C['red_bg'], pady=10)
                alert.pack(fill='x', padx=25, pady=5)
                tk.Label(alert,
                         text=f'  ⚠️  {low_count} student(s) have attendance below 75% — '
                              f'Go to Reports → Student Analytics for details',
                         font=FT['body_b'], bg=C['red_bg'], fg=C['red']).pack(side='left')
                action_btn(alert, 'View →', lambda: self._show_page('reports'),
                           bg=C['red'], padx=10, pady=5).pack(side='right', padx=10)
        except: pass

    # ══════════════════════════════════════════════════════════
    #  PAGE 2 — TAKE ATTENDANCE
    # ══════════════════════════════════════════════════════════
    def _pg_attendance(self):
        self._pg_header('✅  Take Attendance', 'Mark class attendance by department & section', C['green'])
        main = scrollable_page(self.page_area)

        # Filter card
        outer, fc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(fc, 'Select Class', C['green'], '🏛️')

        fg = tk.Frame(fc, bg=C['card'])
        fg.pack(fill='x', padx=15, pady=10)

        dept_v = tk.StringVar(value='BCA')
        sem_v  = tk.StringVar(value='1')
        sec_v  = tk.StringVar(value='A')
        sub_v  = tk.StringVar()
        date_v = tk.StringVar(value=str(date.today()))
        sub_combo_ref = [None]

        def update_subs(*_):
            subs = SUBJECTS.get(dept_v.get(), [])
            if sub_combo_ref[0]:
                sub_combo_ref[0]['values'] = subs
            if subs and not sub_v.get():
                sub_v.set(subs[0])
        dept_v.trace_add('write', update_subs)

        # Row 1
        r1 = tk.Frame(fg, bg=C['card'])
        r1.pack(fill='x', pady=4)
        for lbl, var, vals, w in [
            ('🏛️ Department:', dept_v, list(DEPARTMENTS.keys()), 14),
            ('📅 Semester:',   sem_v,  [str(i) for i in range(1,9)], 6),
            ('📌 Section:',    sec_v,  ['A','B','C'], 6),
        ]:
            tk.Label(r1, text=lbl, font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left', padx=(15,4))
            styled_combo(r1, var, vals, w).pack(side='left', padx=(0,10))

        # Row 2
        r2 = tk.Frame(fg, bg=C['card'])
        r2.pack(fill='x', pady=4)
        tk.Label(r2, text='📖 Subject:', font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left', padx=(15,4))
        sc = styled_combo(r2, sub_v, SUBJECTS.get('BCA',[]), 28)
        sc.pack(side='left', padx=(0,20))
        sub_combo_ref[0] = sc
        update_subs()

        tk.Label(r2, text='📅 Date:', font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left', padx=(15,4))
        styled_entry(r2, date_v, 12).pack(side='left', padx=(0,15))

        status_v = tk.StringVar(value='Select class and click Load Students')
        tk.Label(fc, textvariable=status_v, font=FT['small'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w', padx=15, pady=(0,8))

        # Attendance table
        outer2, tc = card_frame(main)
        outer2.pack(fill='both', expand=True, padx=25, pady=(0,5))
        section_header(tc, 'Student List  —  Double-click to toggle status', C['brown'], '📋')

        att_cols = ('No.', 'Student ID', 'Full Name', 'Status', 'Remarks')
        tf, tree = make_tree(tc, att_cols, [50,120,200,110,220], height=14)
        tf.pack(fill='both', expand=True, padx=10)

        att_map = {}  # sid -> status

        def toggle(e):
            sel = tree.selection()
            if not sel: return
            item = sel[0]
            vals = list(tree.item(item, 'values'))
            sid = vals[1]
            cycle = {'present':'absent','absent':'late','late':'present'}
            new = cycle.get(att_map.get(sid,'present'), 'present')
            att_map[sid] = new
            vals[3] = new.upper()
            tree.item(item, values=vals, tags=(new,))
        tree.bind('<Double-1>', toggle)
        tree.bind('<Return>',   toggle)

        # Keyboard shortcuts hint
        tk.Label(tc, text='💡 Double-click or Enter to cycle: Present → Absent → Late',
                 font=FT['small'], bg=C['card'], fg=C['text4']).pack(pady=(4,0))

        # Action bar
        outer3, ab = card_frame(main)
        outer3.pack(fill='x', padx=25, pady=(0,15))
        inner_ab = tk.Frame(ab, bg=C['card'], pady=10, padx=15)
        inner_ab.pack(fill='x')

        def load():
            tree.delete(*tree.get_children())
            att_map.clear()
            dept = dept_v.get(); sem = sem_v.get(); sec = sec_v.get()
            cls = f"{dept} Sem{sem} Sec{sec}"
            try:
                sts = [s for s in self.db.get_all_students()
                       if s.get('class_name','') == cls and s.get('status') == 'active']
            except: sts = []
            if not sts:
                status_v.set(f'⚠️  No active students found for {cls}. Register students first.')
                return
            for i, s in enumerate(sts, 1):
                sid = s.get('student_id','')
                att_map[sid] = 'present'
                tree.insert('', 'end',
                            values=(i, sid, s.get('full_name',''), 'PRESENT', ''),
                            tags=('present', 'odd' if i%2 else 'even'))
            status_v.set(f'✅  Loaded {len(sts)} students — {cls}  |  {sub_v.get()}  |  {date_v.get()}')

        def mark_all(status):
            for item in tree.get_children():
                v = list(tree.item(item,'values'))
                att_map[v[1]] = status
                v[3] = status.upper()
                tree.item(item, values=v, tags=(status,))

        def submit():
            items = tree.get_children()
            if not items:
                messagebox.showwarning('Empty','Load students first.'); return
            dept = dept_v.get(); sem = sem_v.get(); sec = sec_v.get()
            cls = f"{dept} Sem{sem} Sec{sec}"
            saved = 0
            for item in items:
                v = tree.item(item,'values')
                sid, name = v[1], v[2]
                stat = att_map.get(sid,'present')
                try:
                    self.db.mark_attendance(sid, name, cls, stat); saved += 1
                except: pass
            present = sum(1 for s in att_map.values() if s=='present')
            absent  = sum(1 for s in att_map.values() if s=='absent')
            late    = sum(1 for s in att_map.values() if s=='late')
            messagebox.showinfo('Saved',
                f'✅ Attendance saved for {saved} students\n\n'
                f'Present: {present}  |  Absent: {absent}  |  Late: {late}\n'
                f'Subject: {sub_v.get()}\nDate: {date_v.get()}')
            status_v.set(f'Saved at {datetime.now().strftime("%H:%M:%S")} — P:{present} A:{absent} L:{late}')

        btns = [
            ('🔍 Load Students',  load,                         C['brown']),
            ('✅ All Present',    lambda: mark_all('present'),  C['green']),
            ('❌ All Absent',     lambda: mark_all('absent'),   C['red']),
            ('⏰ All Late',       lambda: mark_all('late'),     C['orange']),
            ('💾 Submit',         submit,                        C['brown2']),
            ('📤 Export CSV',     lambda: self._export_tree_csv(tree), C['blue']),
        ]
        for label, cmd, bg_c in btns:
            action_btn(inner_ab, label, cmd, bg_c, padx=14, pady=8).pack(side='left', padx=5)

    # ══════════════════════════════════════════════════════════
    #  PAGE 3 — LIVE FACE SCAN
    # ══════════════════════════════════════════════════════════
    def _pg_live(self):
        self._pg_header('🎥  Live Face Recognition', 'Real-time attendance via camera', C['red'])

        # ── TOP: Controls bar ─────────────────────────────────
        outer, ctrl = card_frame(self.page_area)
        outer.pack(fill='x', padx=25, pady=(10, 5))
        section_header(ctrl, 'Camera Controls', C['red'], '📷')

        cr = tk.Frame(ctrl, bg=C['card'], padx=15, pady=8)
        cr.pack(fill='x')

        cls_v = tk.StringVar(value='BCA Sem1 SecA')
        tk.Label(cr, text='Class/Section:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(side='left')
        styled_entry(cr, cls_v, 22).pack(side='left', padx=8)

        self.live_status = tk.StringVar(value='🔴  Camera Offline')
        tk.Label(cr, textvariable=self.live_status, font=FT['body_b'],
                 bg=C['card'], fg=C['red']).pack(side='left', padx=25)

        # ── BUTTONS — pack BEFORE body so they are never hidden ──
        btn_row = tk.Frame(self.page_area, bg=C['bg'])
        btn_row.pack(fill='x', padx=25, pady=6)

        self.start_btn = action_btn(
            btn_row, '▶  Start Live Scan',
            lambda: self._start_live(cls_v.get()),
            C['green'], padx=30, pady=11,
            font=('Segoe UI', 12, 'bold'))
        self.start_btn.pack(side='left', padx=(0, 10))

        self.stop_btn = action_btn(
            btn_row, '⏹  Stop Camera',
            self._stop_live, C['red'],
            padx=30, pady=11,
            font=('Segoe UI', 12, 'bold'))
        self.stop_btn.pack(side='left', padx=5)
        self.stop_btn.config(state='disabled')

        tk.Label(btn_row,
                 text='💡 Students must be registered with face capture first',
                 font=FT['small'], bg=C['bg'], fg=C['text3']).pack(side='left', padx=20)

        # ── MAIN BODY: Camera + Log side by side ─────────────
        body = tk.Frame(self.page_area, bg=C['bg'])
        body.pack(fill='both', expand=True, padx=25, pady=(0, 10))

        # Left — camera preview
        left = tk.Frame(body, bg=C['bg'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 8))

        outer2, cam_card = card_frame(left)
        outer2.pack(fill='both', expand=True)

        self.cam_lbl = tk.Label(
            cam_card, bg='#1a1a1a',
            text='📷\n\nCamera Preview\n\nClick  ▶ Start Live Scan  to begin',
            font=('Georgia', 13), fg='#888888', justify='center')
        self.cam_lbl.pack(fill='both', expand=True)

        # Right — recognition log
        right = tk.Frame(body, bg=C['bg'], width=300)
        right.pack(side='left', fill='y')
        right.pack_propagate(False)

        outer3, log_card = card_frame(right)
        outer3.pack(fill='both', expand=True)
        section_header(log_card, 'Recognition Log', C['brown'], '🔍')

        self.live_log = scrolledtext.ScrolledText(
            log_card, bg=C['bg2'], fg=C['text'], font=FT['mono'],
            state='disabled', relief='flat', wrap='word')
        self.live_log.pack(fill='both', expand=True, padx=8, pady=(0, 8))

    def _start_live(self, class_name):
        self.live_on   = True
        self.live_cap  = None          # store cap so _stop_live can release it
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.live_status.set('⏳  Opening camera...')

        def run():
            import cv2
            import time
            import numpy as np
            from face_engine import detect_faces, extract_face_roi, encode_face, compare_faces
            from PIL import Image, ImageTk

            # ── 1. Open camera ────────────────────────────────
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                self.root.after(0, lambda: self.live_status.set('❌  Camera not found'))
                self.root.after(0, lambda: self._live_log(
                    '[ERROR] Cannot open camera.\n'
                    '        Close Zoom / Teams / other apps using the camera.\n'))
                self.live_on = False
                self.root.after(0, self._stop_live)
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            self.live_cap = cap

            # ── 2. Load face encodings from DB ───────────────
            try:
                db_enc = self.db.get_all_face_encodings()
            except Exception as dbe:
                db_enc = []
                self.root.after(0, lambda: self._live_log(f'[ERROR] DB load failed: {dbe}\n'))

            self.root.after(0, lambda: self.live_status.set('🟢  Camera Active — Scanning...'))
            self.root.after(0, lambda: self._live_log(
                f'[INFO] Camera ready. {len(db_enc)} face(s) loaded.\n'
                f'[INFO] Class: {class_name}\n'
                + ('[WARN] No student faces! Go to Students → Add Student → Capture Face\n'
                   if len(db_enc) == 0 else '')))

            seen        = set()   # student IDs marked this session
            frame_count = 0
            last_faces  = []      # cached face boxes for smooth drawing
            THRESHOLD   = 7500
            PROCESS_EVERY = 3     # run recognition every 3rd frame (smoother UI)

            # ── 3. Main video loop ────────────────────────────
            while self.live_on:
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.05)
                    continue

                frame_count += 1
                display = frame.copy()

                # Run face recognition every Nth frame
                if frame_count % PROCESS_EVERY == 0:
                    try:
                        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = detect_faces(gray)
                        last_faces = []

                        for (x, y, w, h) in faces:
                            # Guard: skip if ROI or encoding fails
                            roi = extract_face_roi(frame, x, y, w, h)
                            if roi is None:
                                continue
                            enc = encode_face(roi)
                            if enc is None:
                                continue

                            # Find best match
                            best_sid  = None
                            best_name = 'Unknown'
                            best_cls  = ''
                            best_dist = 999999
                            box_col   = (0, 120, 200)   # blue = unknown

                            for (sid, name, cls, stored_enc) in db_enc:
                                try:
                                    stored = np.array(stored_enc, dtype=np.float32)
                                    ok, d  = compare_faces(stored, enc, THRESHOLD)
                                    if ok and d < best_dist:
                                        best_dist = d
                                        best_sid  = sid
                                        best_name = name
                                        best_cls  = cls or ''
                                        box_col   = (34, 139, 34)   # green = match
                                except Exception:
                                    continue

                            # Mark attendance (once per session)
                            if best_sid and best_sid not in seen:
                                seen.add(best_sid)
                                try:
                                    self.db.mark_attendance(best_sid, best_name, class_name)
                                    msg = (f'[{datetime.now().strftime("%H:%M:%S")}] '
                                           f'✅ {best_name} ({best_sid}) — MARKED PRESENT\n')
                                except Exception as me:
                                    msg = (f'[{datetime.now().strftime("%H:%M:%S")}] '
                                           f'⚠️ {best_name} — DB error: {me}\n')
                                self.root.after(0, lambda m=msg: self._live_log(m))

                            conf = max(0, int(100 - (best_dist / THRESHOLD * 100)))
                            lbl  = best_name + (f' {conf}%' if best_sid else '')
                            last_faces.append((x, y, w, h, box_col, lbl))

                    except Exception as fe:
                        pass   # skip bad frame silently

                # Draw cached face boxes on every frame (smooth)
                for (x, y, w, h, box_col, lbl) in last_faces:
                    cv2.rectangle(display, (x, y), (x+w, y+h), box_col, 2)
                    cv2.rectangle(display, (x, y+h), (x+w, y+h+26), box_col, -1)
                    cv2.putText(display, lbl, (x+5, y+h+18),
                                cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)

                # Push frame to UI (safe — catches TclError if page navigated away)
                try:
                    rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb).resize((540, 380), Image.LANCZOS)
                    ph  = ImageTk.PhotoImage(img)
                    self.root.after(0, lambda p=ph: self._set_cam(p))
                except Exception:
                    pass

                time.sleep(0.033)   # ~30 fps

            # ── 4. Cleanup ────────────────────────────────────
            cap.release()
            self.live_cap = None
            self.root.after(0, lambda: self._live_log('[INFO] Camera released.\n'))
            self.root.after(0, lambda: self.live_status.set('🔴  Camera Offline'))

        threading.Thread(target=run, daemon=True).start()

    def _stop_live(self):
        self.live_on = False
        # Release camera if still held
        cap = getattr(self, 'live_cap', None)
        if cap:
            try: cap.release()
            except: pass
            self.live_cap = None
        try:
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.live_status.set('🔴  Camera Offline')
            self.cam_lbl.config(
                image='',
                text='📷\n\nCamera stopped.\n\nClick ▶ Start to activate again.',
                fg=C['text3']
            )
            self.cam_lbl.image = None
        except: pass

    def _set_cam(self, ph):
        try:
            self.cam_lbl.config(image=ph, text='')
            self.cam_lbl.image = ph
        except: pass

    def _live_log(self, msg):
        try:
            self.live_log.config(state='normal')
            self.live_log.insert('end', msg)
            self.live_log.see('end')
            self.live_log.config(state='disabled')
        except: pass

    # ══════════════════════════════════════════════════════════
    #  PAGE 4 — MANUAL ENTRY
    # ══════════════════════════════════════════════════════════
    def _pg_manual(self):
        self._pg_header('📝  Manual Attendance Entry', '', C['blue'])
        main = scrollable_page(self.page_area)

        outer, fc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(fc, 'Enter Single Student Attendance', C['blue'], '✏️')

        fg = tk.Frame(fc, bg=C['card'])
        fg.pack(fill='x', padx=15, pady=12)
        fg.columnconfigure(1, weight=1); fg.columnconfigure(3, weight=1)

        sid_v   = tk.StringVar()
        name_v  = tk.StringVar()
        dept_v  = tk.StringVar(value='BCA')
        sem_v   = tk.StringVar(value='1')
        sec_v   = tk.StringVar(value='A')
        sub_v   = tk.StringVar()
        date_v  = tk.StringVar(value=str(date.today()))
        time_v  = tk.StringVar(value=datetime.now().strftime('%H:%M'))
        stat_v  = tk.StringVar(value='present')
        rem_v   = tk.StringVar()

        label_entry_row(fg, '🆔 Student ID:',  sid_v,  0, 0)
        label_entry_row(fg, '👤 Full Name:',   name_v, 0, 1)
        label_entry_row(fg, '🏛️ Department:',  dept_v, 1, 0, combo_vals=list(DEPARTMENTS.keys()))
        label_entry_row(fg, '📅 Semester:',    sem_v,  1, 1, combo_vals=[str(i) for i in range(1,9)])
        label_entry_row(fg, '📌 Section:',     sec_v,  2, 0, combo_vals=['A','B','C'])

        def update_sub(*_):
            subs = SUBJECTS.get(dept_v.get(),[])
            if subs and not sub_v.get(): sub_v.set(subs[0])
        dept_v.trace_add('write', update_sub); update_sub()

        label_entry_row(fg, '📖 Subject:',    sub_v,  2, 1, width=24)
        label_entry_row(fg, '📅 Date:',       date_v, 3, 0)
        label_entry_row(fg, '⏰ Time In:',    time_v, 3, 1)
        label_entry_row(fg, '✅ Status:',     stat_v, 4, 0, combo_vals=['present','absent','late'])
        label_entry_row(fg, '💬 Remarks:',   rem_v,  4, 1, width=28)

        def autofill(*_):
            sid = sid_v.get().strip()
            if len(sid) >= 3:
                try:
                    s = self.db.get_student_by_id(sid)
                    if s:
                        name_v.set(s.get('full_name',''))
                        cls = s.get('class_name','')
                        for dept in DEPARTMENTS:
                            if dept in cls: dept_v.set(dept); break
                except: pass
        sid_v.trace_add('write', autofill)

        # Log
        outer2, lc = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,5))
        section_header(lc, 'Submission Log', C['brown'], '📋')
        log_box = scrolledtext.ScrolledText(lc, height=7, bg=C['bg2'], fg=C['text'],
                                             font=FT['mono'], state='disabled', relief='flat')
        log_box.pack(fill='x', padx=10, pady=(0,10))

        def submit():
            sid  = sid_v.get().strip(); name = name_v.get().strip()
            dept = dept_v.get(); sem = sem_v.get(); sec = sec_v.get()
            stat = stat_v.get() or 'present'
            if not sid or not name:
                messagebox.showwarning('Missing','Student ID and Name are required.'); return
            cls = f"{dept} Sem{sem} Sec{sec}"
            try:
                ok = self.db.mark_attendance(sid, name, cls, stat)
                msg = (f'[{datetime.now().strftime("%H:%M:%S")}] {"✅" if ok else "⚠️"} '
                       f'{sid} — {name} — {cls} — {stat.upper()} — {sub_v.get()}\n')
                log_box.config(state='normal'); log_box.insert('end', msg)
                log_box.see('end'); log_box.config(state='disabled')
                if ok: sid_v.set(''); name_v.set(''); rem_v.set('')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        brow = tk.Frame(fc, bg=C['card'], pady=12, padx=15)
        brow.pack(fill='x')
        action_btn(brow,'💾 Save Attendance', submit,   C['brown2'], padx=22, pady=10).pack(side='left', padx=8)
        action_btn(brow,'🗑️ Clear',           lambda: [v.set('') for v in [sid_v,name_v,rem_v]],
                   C['bg3'], fg=C['text'],     padx=16, pady=10).pack(side='left', padx=5)

    # ══════════════════════════════════════════════════════════
    #  PAGE 5 — BULK UPLOAD
    # ══════════════════════════════════════════════════════════
    def _pg_bulk(self):
        self._pg_header('📋  Bulk Attendance Upload', 'Import attendance from CSV file', C['brown3'])
        main = scrollable_page(self.page_area)

        outer, ic = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(ic, 'Import from CSV', C['brown3'], '📂')

        info = tk.Frame(ic, bg=C['cream'], pady=12, padx=15)
        info.pack(fill='x', padx=15, pady=10)
        tk.Label(info, text='📌  CSV Format Required:',
                 font=FT['body_b'], bg=C['cream'], fg=C['brown']).pack(anchor='w')
        tk.Label(info,
                 text='   student_id, full_name, class_name, date (YYYY-MM-DD), time_in (HH:MM), status (present/absent/late)',
                 font=FT['mono'], bg=C['cream'], fg=C['text2']).pack(anchor='w', pady=4)
        tk.Label(info, text='   Example:  BCA001, Priya Sharma, BCA Sem1 SecA, 2026-02-19, 08:45, present',
                 font=FT['mono'], bg=C['cream'], fg=C['text3']).pack(anchor='w')

        file_v = tk.StringVar(value='No file selected')
        frow = tk.Frame(ic, bg=C['card'], padx=15, pady=10)
        frow.pack(fill='x')
        tk.Label(frow, textvariable=file_v, font=FT['body'],
                 bg=C['bg2'], fg=C['text'], width=55, anchor='w',
                 relief='flat').pack(side='left', ipady=6, padx=(0,10))

        path_ref = [None]
        def browse():
            p = filedialog.askopenfilename(filetypes=[('CSV','*.csv'),('All','*.*')])
            if p: path_ref[0] = p; file_v.set(os.path.basename(p))
        action_btn(frow, '📂 Browse', browse, C['brown']).pack(side='left')

        result_var = tk.StringVar()
        tk.Label(ic, textvariable=result_var, font=FT['body_b'],
                 bg=C['card'], fg=C['green']).pack(pady=5)

        preview_outer, prev_card = card_frame(main)
        preview_outer.pack(fill='x', padx=25, pady=(0,5))
        section_header(prev_card, 'Preview', C['brown'], '👁️')
        cols = ('student_id','full_name','class_name','date','time_in','status')
        pf, prev_tree = make_tree(prev_card, cols, [110,160,160,110,90,100], height=8)
        pf.pack(fill='x', padx=10, pady=(0,10))

        def preview_import():
            if not path_ref[0]:
                messagebox.showwarning('No File','Select a CSV file first.'); return
            try:
                import pandas as pd
                df = pd.read_csv(path_ref[0])
                df.columns = [c.strip().lower().replace(' ','_') for c in df.columns]
                prev_tree.delete(*prev_tree.get_children())
                for i, row in df.iterrows():
                    prev_tree.insert('', 'end', values=tuple(str(row.get(c,'')) for c in cols),
                                     tags=('odd' if i%2 else 'even',))
                result_var.set(f'Preview: {len(df)} rows loaded.')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        def do_import():
            if not path_ref[0]:
                messagebox.showwarning('No File','Select a CSV file first.'); return
            try:
                import pandas as pd
                df = pd.read_csv(path_ref[0])
                df.columns = [c.strip().lower().replace(' ','_') for c in df.columns]
                saved = 0
                for _, row in df.iterrows():
                    try:
                        self.db.mark_attendance(
                            str(row.get('student_id','')).strip(),
                            str(row.get('full_name','')).strip(),
                            str(row.get('class_name','')).strip(),
                            str(row.get('status','present')).strip())
                        saved += 1
                    except: pass
                result_var.set(f'✅ Imported {saved} of {len(df)} records successfully!')
                messagebox.showinfo('Done', f'✅ {saved} records imported.')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        brow = tk.Frame(ic, bg=C['card'], padx=15, pady=10)
        brow.pack(fill='x')
        action_btn(brow, '👁️ Preview', preview_import, C['blue'],    padx=20, pady=9).pack(side='left', padx=6)
        action_btn(brow, '📥 Import',  do_import,       C['green'],   padx=20, pady=9).pack(side='left', padx=6)

        def dl_template():
            p = filedialog.asksaveasfilename(defaultextension='.csv',
                                              filetypes=[('CSV','*.csv')],
                                              initialfile='attendance_template.csv')
            if p:
                with open(p,'w') as f:
                    f.write('student_id,full_name,class_name,date,time_in,status\n')
                    f.write('BCA001,Sample Student,BCA Sem1 SecA,2026-02-19,08:45,present\n')
                messagebox.showinfo('Template', f'Template saved:\n{p}')
        action_btn(brow, '📄 Download Template', dl_template, C['brown_light'], padx=16, pady=9).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════
    #  PAGE 6 — MY STUDENTS
    # ══════════════════════════════════════════════════════════
    def _pg_students(self):
        self._pg_header('👩‍🎓  My Students', '', C['purple'])
        main = scrollable_page(self.page_area)

        # Filter
        outer, fc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(fc, 'Search & Filter', C['purple'], '🔍')
        fr = tk.Frame(fc, bg=C['card'], padx=15, pady=10)
        fr.pack(fill='x')
        search_v = tk.StringVar()
        class_v  = tk.StringVar(value='All')
        dept_v   = tk.StringVar(value='All')
        for lbl, var, vals, w in [
            ('🔍 Search:', search_v, None, 22),
            ('📚 Dept:', dept_v, ['All']+list(DEPARTMENTS.keys()), 14),
        ]:
            tk.Label(fr, text=lbl, font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left', padx=(0,4))
            if vals:
                styled_combo(fr, var, vals, w).pack(side='left', padx=(0,15))
            else:
                styled_entry(fr, var, w).pack(side='left', padx=(0,15))

        count_v = tk.StringVar()
        tk.Label(fr, textvariable=count_v, font=FT['body_b'],
                 bg=C['card'], fg=C['brown']).pack(side='right', padx=15)

        # Table
        outer2, tc = card_frame(main)
        outer2.pack(fill='both', expand=True, padx=25, pady=(0,10))
        cols = ('Student ID','Full Name','Class','Section','Email','Phone','Status','Attendance%','Registered')
        widths = [100,160,140,70,180,120,80,100,120]
        tf, tree = make_tree(tc, cols, widths, height=15)
        tf.pack(fill='both', expand=True, padx=10, pady=(0,10))

        all_data = []
        def load(*_):
            tree.delete(*tree.get_children())
            all_data.clear()
            try: students = self.db.get_all_students()
            except: students = []
            q = search_v.get().strip().lower()
            dept_sel = dept_v.get()
            filtered = []
            for s in students:
                if q and q not in s.get('full_name','').lower() and q not in s.get('student_id','').lower():
                    continue
                if dept_sel != 'All' and dept_sel not in s.get('class_name',''):
                    continue
                filtered.append(s)
            all_data.extend(filtered)
            for i, s in enumerate(filtered):
                try:
                    summ = self.db.get_student_attendance_summary(s['student_id'])
                    pct  = f"{summ['percentage']}%"
                except: pct = 'N/A'
                stat = s.get('status','active')
                tag = stat
                if pct != 'N/A':
                    try:
                        if float(pct[:-1]) < 75: tag = 'absent'
                    except: pass
                tree.insert('', 'end', values=(
                    s.get('student_id',''), s.get('full_name',''),
                    s.get('class_name',''), s.get('section',''),
                    s.get('email',''), s.get('phone',''),
                    stat.upper(), pct, str(s.get('registered_at',''))[:10]
                ), tags=(tag, 'odd' if i%2 else 'even'))
            count_v.set(f'{len(filtered)} student(s)')
        load()
        search_v.trace_add('write', load)
        dept_v.trace_add('write',   load)

        # Right-click menu
        ctx = tk.Menu(self.root, tearoff=0, bg=C['card'], fg=C['text'],
                      font=FT['body'], activebackground=C['brown2'],
                      activeforeground=C['white'])

        def _sel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning('Select','Select a student first.'); return None
            return tree.item(sel[0],'values')

        def view_att():
            vals = _sel();
            if not vals: return
            sid = vals[0]; name = vals[1]
            win = tk.Toplevel(self.root); win.title(f'Attendance — {name}')
            win.geometry('750x500'); win.configure(bg=C['bg'])
            tk.Label(win, text=f'📊  {name} ({sid})', font=('Georgia',15,'bold'),
                     bg=C['bg'], fg=C['brown']).pack(pady=15)
            try:
                summ = self.db.get_student_attendance_summary(sid)
                sr = tk.Frame(win, bg=C['bg']); sr.pack()
                for t2,v2,col2 in [
                    ('Total',summ['total'],C['blue']),
                    ('Present',summ['present'],C['green']),
                    ('Absent',summ['absent'],C['red']),
                    (f"{summ['percentage']}%",'Attendance',C['brown'])
                ]:
                    c2 = tk.Frame(sr, bg=C['card'], padx=22, pady=15); c2.pack(side='left', padx=10)
                    tk.Label(c2, text=str(t2), font=('Georgia',24,'bold'), bg=C['card'], fg=col2).pack()
                    tk.Label(c2, text=str(v2), font=FT['small'], bg=C['card'], fg=C['text3']).pack()
                if summ['percentage'] < 75:
                    tk.Label(win, text=f'⚠️  Below 75% threshold — Detainment Risk!',
                             font=FT['body_b'], bg=C['red_bg'], fg=C['red'], pady=8).pack(fill='x', padx=30)
            except Exception as ex:
                tk.Label(win, text=str(ex), bg=C['bg'], fg=C['red']).pack()

        def send_alert():
            vals = _sel();
            if not vals: return
            try:
                s = self.db.get_student_by_id(vals[0])
                from notification_service import notify_absent
                ok, msg = notify_absent(s.get('full_name',''), vals[0],
                                        s.get('class_name',''), s.get('phone',''),
                                        str(date.today()))
                messagebox.showinfo('Alert', f'{"✅" if ok else "❌"}  {msg}')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        def view_profile():
            vals = _sel();
            if not vals: return
            messagebox.showinfo('Student Profile',
                f'ID:      {vals[0]}\nName:    {vals[1]}\nClass:   {vals[2]}\n'
                f'Section: {vals[3]}\nEmail:   {vals[4]}\nPhone:   {vals[5]}\nStatus:  {vals[6]}')

        ctx.add_command(label='📊 View Attendance',   command=view_att)
        ctx.add_command(label='📱 Send Absent Alert', command=send_alert)
        ctx.add_command(label='👤 View Profile',      command=view_profile)

        def right_click(e):
            try: tree.selection_set(tree.identify_row(e.y)); ctx.post(e.x_root, e.y_root)
            except: pass
        tree.bind('<Button-3>', right_click)

        # Bottom bar
        brow = tk.Frame(self.page_area, bg=C['bg'], pady=8)
        brow.pack()
        action_btn(brow, '🔄 Refresh', load,     C['brown'],  padx=18, pady=8).pack(side='left', padx=6)
        action_btn(brow, '📤 Export',  lambda: self._export_tree_csv(tree), C['green'], padx=18, pady=8).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════
    #  PAGE 7 — MARKS & GRADES
    # ══════════════════════════════════════════════════════════
    def _pg_marks(self):
        self._pg_header('📊  Marks & Grade Entry', 'Enter internal/external examination marks', C['purple'])
        nb = ttk.Notebook(self.page_area)
        nb.pack(fill='both', expand=True, padx=25, pady=12)

        # Tab 1: Enter Marks
        t1 = tk.Frame(nb, bg=C['bg']); nb.add(t1, text='✏️  Enter Marks')
        outer, mc = card_frame(t1)
        outer.pack(fill='x', padx=10, pady=10)
        section_header(mc, 'Enter Student Marks', C['purple'], '✏️')
        mg = tk.Frame(mc, bg=C['card']); mg.pack(fill='x', padx=15, pady=12)
        mg.columnconfigure(1,weight=1); mg.columnconfigure(3,weight=1)

        msid_v  = tk.StringVar(); mname_v = tk.StringVar()
        mdept_v = tk.StringVar(value='BCA'); msem_v  = tk.StringVar(value='1')
        msec_v  = tk.StringVar(value='A');   msub_v  = tk.StringVar()
        mexam_v = tk.StringVar(value='Unit Test 1')
        mmarks_v= tk.StringVar(); mmax_v  = tk.StringVar(value='100')
        mgrade_v= tk.StringVar(); mdate_v = tk.StringVar(value=str(date.today()))

        label_entry_row(mg, '🆔 Student ID:',   msid_v,  0,0)
        label_entry_row(mg, '👤 Student Name:',  mname_v, 0,1)
        label_entry_row(mg, '🏛️ Department:',    mdept_v, 1,0, combo_vals=list(DEPARTMENTS.keys()))
        label_entry_row(mg, '📅 Semester:',      msem_v,  1,1, combo_vals=[str(i) for i in range(1,9)])
        label_entry_row(mg, '📖 Subject:',       msub_v,  2,0, combo_vals=SUBJECTS.get('BCA',[]), width=24)
        label_entry_row(mg, '📝 Exam Type:',     mexam_v, 2,1, combo_vals=EXAM_TYPES)
        label_entry_row(mg, '🔢 Marks Obtained:',mmarks_v,3,0)
        label_entry_row(mg, '🔢 Max Marks:',     mmax_v,  3,1)
        label_entry_row(mg, '🏅 Grade:',         mgrade_v,4,0, combo_vals=['O','A+','A','B+','B','C','D','F'])
        label_entry_row(mg, '📅 Exam Date:',     mdate_v, 4,1)

        def auto_grade(*_):
            try:
                m = float(mmarks_v.get() or 0)
                mx = float(mmax_v.get() or 100)
                pct = m/mx*100
                g = 'O' if pct>=90 else 'A+' if pct>=80 else 'A' if pct>=70 else \
                    'B+' if pct>=60 else 'B' if pct>=50 else 'C' if pct>=40 else 'F'
                mgrade_v.set(g)
            except: pass
        mmarks_v.trace_add('write', auto_grade)

        def auto_fill_m(*_):
            sid = msid_v.get().strip()
            if len(sid) >= 3:
                try:
                    s = self.db.get_student_by_id(sid)
                    if s:
                        mname_v.set(s.get('full_name',''))
                        cls = s.get('class_name','')
                        for d in DEPARTMENTS:
                            if d in cls: mdept_v.set(d); break
                except: pass
        msid_v.trace_add('write', auto_fill_m)

        mres_v = tk.StringVar()
        tk.Label(mc, textvariable=mres_v, font=FT['body_b'], bg=C['card'], fg=C['green']).pack(pady=4)

        def save_marks():
            sid=msid_v.get().strip(); name=mname_v.get().strip()
            if not sid or not name:
                messagebox.showwarning('Missing','Student ID & Name required.'); return
            try:
                self.db.add_student_result(
                    sid, msub_v.get(), mexam_v.get(),
                    float(mmarks_v.get()), float(mmax_v.get()),
                    mgrade_v.get(), f"Sem{msem_v.get()}", mdate_v.get())
                mres_v.set(f'✅  Marks saved: {sid} — {msub_v.get()} — {mmarks_v.get()}/{mmax_v.get()} ({mgrade_v.get()})')
                for v in [msid_v,mname_v,mmarks_v,mgrade_v]: v.set('')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        brow = tk.Frame(mc, bg=C['card'], padx=15, pady=10); brow.pack(fill='x')
        action_btn(brow,'💾 Save Marks', save_marks, C['purple'], padx=22, pady=10).pack(side='left', padx=8)

        # Tab 2: View Marks
        t2 = tk.Frame(nb, bg=C['bg']); nb.add(t2, text='📋  View Results')
        vrow = tk.Frame(t2, bg=C['bg']); vrow.pack(fill='x', padx=10, pady=10)
        vsid = tk.StringVar()
        tk.Label(vrow, text='Student ID:', font=FT['body_b'], bg=C['bg'], fg=C['text3']).pack(side='left')
        styled_entry(vrow, vsid, 18).pack(side='left', padx=8)

        vcols = ('Subject','Exam Type','Marks','Max','Grade','Semester','Date')
        vf, vtree = make_tree(t2, vcols, [180,130,80,70,70,100,110], height=14)
        vf.pack(fill='both', expand=True, padx=10)

        def load_results():
            vtree.delete(*vtree.get_children())
            sid = vsid.get().strip()
            if not sid: return
            try:
                recs = self.db.get_student_results(sid)
                for i, r in enumerate(recs):
                    m = float(r.get('marks') or 0); mx = float(r.get('max_marks') or 100)
                    vtree.insert('', 'end', values=(
                        r.get('subject',''), r.get('exam_type',''),
                        f"{m:.1f}", f"{mx:.1f}", r.get('grade',''),
                        r.get('semester',''), str(r.get('result_date',''))
                    ), tags=('odd' if i%2 else 'even'))
            except Exception as ex: messagebox.showerror('Error', str(ex))

        action_btn(vrow, '🔍 Load', load_results, C['purple'], padx=16, pady=7).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════
    #  PAGE 8 — ASSIGNMENTS
    # ══════════════════════════════════════════════════════════
    def _pg_assignments(self):
        self._pg_header('📚  Assignment Management', 'Create & track student assignments', C['orange'])
        main = scrollable_page(self.page_area)

        # Post Assignment
        outer, ac = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(ac, 'Post New Assignment', C['orange'], '📝')

        ag = tk.Frame(ac, bg=C['card']); ag.pack(fill='x', padx=15, pady=12)
        ag.columnconfigure(1,weight=1); ag.columnconfigure(3,weight=1)

        adept_v = tk.StringVar(value='BCA');  asem_v = tk.StringVar(value='1')
        asec_v  = tk.StringVar(value='A');    asub_v = tk.StringVar()
        atitle_v= tk.StringVar(); adue_v = tk.StringVar(value=str(date.today()+timedelta(days=7)))
        amarks_v= tk.StringVar(value='10');   atype_v= tk.StringVar(value='Individual')

        label_entry_row(ag, '🏛️ Department:', adept_v, 0,0, combo_vals=list(DEPARTMENTS.keys()))
        label_entry_row(ag, '📅 Semester:',   asem_v,  0,1, combo_vals=[str(i) for i in range(1,9)])
        label_entry_row(ag, '📌 Section:',    asec_v,  1,0, combo_vals=['A','B','C'])
        label_entry_row(ag, '📖 Subject:',    asub_v,  1,1, combo_vals=SUBJECTS.get('BCA',[]), width=24)
        label_entry_row(ag, '📋 Title:',      atitle_v,2,0, width=30)
        label_entry_row(ag, '📅 Due Date:',   adue_v,  2,1)
        label_entry_row(ag, '🔢 Max Marks:',  amarks_v,3,0)
        label_entry_row(ag, '👥 Type:',       atype_v, 3,1, combo_vals=['Individual','Group','Pair'])

        desc_f = tk.Frame(ac, bg=C['card'], padx=15); desc_f.pack(fill='x')
        tk.Label(desc_f, text='📝 Description:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w')
        desc_box = tk.Text(desc_f, height=4, bg=C['bg2'], fg=C['text'],
                           font=FT['body'], relief='flat', wrap='word',
                           highlightthickness=1, highlightbackground=C['card_border'])
        desc_box.pack(fill='x', pady=5)

        # Assignment list
        outer2, al = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(al, 'Posted Assignments', C['brown'], '📋')
        acols = ('Department','Subject','Title','Due Date','Max Marks','Type','Status')
        af, atree = make_tree(al, acols, [130,160,200,110,90,100,100], height=8)
        af.pack(fill='x', padx=10, pady=(0,10))

        assignments_store = []

        def post_assignment():
            title = atitle_v.get().strip()
            if not title:
                messagebox.showwarning('Missing','Assignment title required.'); return
            dept=adept_v.get(); sem=asem_v.get(); sec=asec_v.get()
            entry = {
                'dept': dept, 'sem': sem, 'sec': sec,
                'subject': asub_v.get(), 'title': title,
                'due': adue_v.get(), 'marks': amarks_v.get(),
                'type': atype_v.get(), 'desc': desc_box.get('1.0','end').strip(),
                'status': 'Active', 'posted': str(date.today())
            }
            assignments_store.append(entry)
            cls = f"{dept} Sem{sem} Sec{sec}"
            atree.insert('', 'end', values=(
                cls, entry['subject'], entry['title'],
                entry['due'], entry['marks'], entry['type'], 'Active'
            ))
            messagebox.showinfo('Posted', f'✅ Assignment "{title}" posted for {cls}')
            atitle_v.set(''); desc_box.delete('1.0','end')

        brow = tk.Frame(ac, bg=C['card'], padx=15, pady=10); brow.pack(fill='x')
        action_btn(brow,'📤 Post Assignment', post_assignment, C['orange'], padx=22, pady=10).pack(side='left', padx=8)

    # ══════════════════════════════════════════════════════════
    #  PAGE 9 — STUDENT COUNSELLING
    # ══════════════════════════════════════════════════════════
    def _pg_counselling(self):
        self._pg_header('💬  Student Counselling Log', 'Record counselling sessions & follow-ups', C['teal'])
        main = scrollable_page(self.page_area)

        outer, cc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(cc, 'New Counselling Entry', C['teal'], '💬')

        cg = tk.Frame(cc, bg=C['card']); cg.pack(fill='x', padx=15, pady=12)
        cg.columnconfigure(1,weight=1); cg.columnconfigure(3,weight=1)
        csid_v   = tk.StringVar(); cname_v  = tk.StringVar()
        cdate_v  = tk.StringVar(value=str(date.today()))
        ctype_v  = tk.StringVar(value='Academic')
        cfollow_v= tk.StringVar(value=str(date.today()+timedelta(days=7)))
        cstatus_v= tk.StringVar(value='Open')

        label_entry_row(cg,'🆔 Student ID:', csid_v,  0,0)
        label_entry_row(cg,'👤 Name:',        cname_v, 0,1)
        label_entry_row(cg,'📅 Date:',        cdate_v, 1,0)
        label_entry_row(cg,'📌 Type:',        ctype_v, 1,1,
                        combo_vals=['Academic','Personal','Attendance','Career','Mental Health','Disciplinary'])
        label_entry_row(cg,'📅 Follow-up:',   cfollow_v,2,0)
        label_entry_row(cg,'🔄 Status:',      cstatus_v,2,1,
                        combo_vals=['Open','In Progress','Resolved','Referred'])

        notes_f = tk.Frame(cc, bg=C['card'], padx=15); notes_f.pack(fill='x')
        tk.Label(notes_f, text='📝 Session Notes:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w')
        notes_box = tk.Text(notes_f, height=5, bg=C['bg2'], fg=C['text'],
                            font=FT['body'], relief='flat', wrap='word',
                            highlightthickness=1, highlightbackground=C['card_border'])
        notes_box.pack(fill='x', pady=5)

        # Log list
        outer2, lc = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(lc, 'Counselling Records', C['brown'], '📋')
        cols = ('Date','Student ID','Name','Type','Status','Follow-up','Notes')
        cf, ctree = make_tree(lc, cols, [100,100,160,130,110,110,250], height=8)
        cf.pack(fill='x', padx=10, pady=(0,10))

        def autofill_c(*_):
            sid = csid_v.get().strip()
            if len(sid) >= 3:
                try:
                    s = self.db.get_student_by_id(sid)
                    if s: cname_v.set(s.get('full_name',''))
                except: pass
        csid_v.trace_add('write', autofill_c)

        def save_counsel():
            sid = csid_v.get().strip(); name = cname_v.get().strip()
            if not sid or not name:
                messagebox.showwarning('Missing','Student ID and Name required.'); return
            notes = notes_box.get('1.0','end').strip()
            ctree.insert('', 'end', values=(
                cdate_v.get(), sid, name, ctype_v.get(),
                cstatus_v.get(), cfollow_v.get(), notes[:60]+'...' if len(notes)>60 else notes
            ))
            messagebox.showinfo('Saved', f'✅ Counselling record saved for {name}')
            csid_v.set(''); cname_v.set(''); notes_box.delete('1.0','end')

        brow = tk.Frame(cc, bg=C['card'], padx=15, pady=10); brow.pack(fill='x')
        action_btn(brow,'💾 Save Record', save_counsel, C['teal'], padx=22, pady=10).pack(side='left', padx=8)
        action_btn(brow,'📤 Export Log', lambda: self._export_tree_csv(ctree), C['blue'], padx=16, pady=10).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════
    #  PAGE 10 — LEAVE MANAGEMENT
    # ══════════════════════════════════════════════════════════
    def _pg_leave(self):
        self._pg_header('📅  Leave Management', 'Apply for leave & track applications', C['brown_light'])
        main = scrollable_page(self.page_area)

        outer, lc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(lc, 'Apply for Leave', C['brown_light'], '📝')

        lg = tk.Frame(lc, bg=C['card']); lg.pack(fill='x', padx=15, pady=12)
        lg.columnconfigure(1,weight=1); lg.columnconfigure(3,weight=1)
        ltype_v  = tk.StringVar(value='Sick Leave')
        lfrom_v  = tk.StringVar(value=str(date.today()))
        lto_v    = tk.StringVar(value=str(date.today()))
        lsub_v   = tk.StringVar()
        lcontact_v = tk.StringVar()

        label_entry_row(lg,'📌 Leave Type:',    ltype_v,  0,0, combo_vals=LEAVE_TYPES)
        label_entry_row(lg,'📅 From Date:',     lfrom_v,  0,1)
        label_entry_row(lg,'📅 To Date:',       lto_v,    1,0)
        label_entry_row(lg,'📞 Contact During:', lcontact_v,1,1)
        label_entry_row(lg,'📋 Subject:',       lsub_v,   2,0, width=35)

        reason_f = tk.Frame(lc, bg=C['card'], padx=15); reason_f.pack(fill='x')
        tk.Label(reason_f, text='📝 Reason:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w')
        reason_box = tk.Text(reason_f, height=4, bg=C['bg2'], fg=C['text'],
                             font=FT['body'], relief='flat', wrap='word',
                             highlightthickness=1, highlightbackground=C['card_border'])
        reason_box.pack(fill='x', pady=5)

        # Leave history
        outer2, lh = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(lh, 'Leave History', C['brown'], '📋')
        lcols = ('Applied On','Type','From','To','Days','Reason','Status')
        lf, ltree = make_tree(lh, lcols, [110,130,100,100,60,250,100], height=7)
        lf.pack(fill='x', padx=10, pady=(0,10))

        def days_count():
            try:
                f = datetime.strptime(lfrom_v.get(),'%Y-%m-%d')
                t = datetime.strptime(lto_v.get(),'%Y-%m-%d')
                return (t-f).days + 1
            except: return 1

        def apply_leave():
            reason = reason_box.get('1.0','end').strip()
            if not reason:
                messagebox.showwarning('Missing','Reason is required.'); return
            days = days_count()
            ltree.insert('', 'end', values=(
                str(date.today()), ltype_v.get(), lfrom_v.get(),
                lto_v.get(), days, reason[:60]+'…' if len(reason)>60 else reason,
                'Pending'
            ))
            messagebox.showinfo('Applied',
                f'✅ Leave application submitted!\n'
                f'Type: {ltype_v.get()}\nDuration: {days} day(s)\n'
                f'From: {lfrom_v.get()} To: {lto_v.get()}\n\n'
                f'Status: Pending (HOD approval required)')
            reason_box.delete('1.0','end')

        brow = tk.Frame(lc, bg=C['card'], padx=15, pady=10); brow.pack(fill='x')
        action_btn(brow,'📤 Apply for Leave', apply_leave, C['brown_light'], padx=22, pady=10).pack(side='left', padx=8)

    # ══════════════════════════════════════════════════════════
    #  PAGE 11 — TIMETABLE
    # ══════════════════════════════════════════════════════════
    def _pg_timetable(self):
        self._pg_header('🗓️  Timetable', 'Weekly lecture schedule', C['teal'])
        main = scrollable_page(self.page_area)

        days    = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        periods = ['8:00–9:00','9:00–10:00','10:00–11:00','11:00–12:00',
                   '12:00–13:00','13:00–14:00','14:00–15:00','15:00–16:00']
        today   = datetime.now().strftime('%A')

        sample = {
            ('Monday','8:00–9:00'):     ('BCA','Python Programming','Sem1 SecA'),
            ('Monday','9:00–10:00'):    ('BSc.IT','Web Development','Sem3 SecB'),
            ('Monday','11:00–12:00'):   ('BCA','DBMS','Sem3 SecA'),
            ('Tuesday','8:00–9:00'):    ('BBA','Business Management','Sem2 SecA'),
            ('Tuesday','10:00–11:00'):  ('BCA','DBMS','Sem3 SecA'),
            ('Wednesday','9:00–10:00'): ('BCom','Financial Accounting','Sem1 SecB'),
            ('Wednesday','14:00–15:00'):('MBA','Strategic Management','Sem1 SecA'),
            ('Thursday','8:00–9:00'):   ('MCA','Machine Learning','Sem2 SecA'),
            ('Thursday','11:00–12:00'): ('BSc.IT','Cyber Security','Sem5 SecA'),
            ('Friday','9:00–10:00'):    ('BBA','Marketing Management','Sem4 SecB'),
            ('Friday','13:00–14:00'):   ('BCA','AI','Sem5 SecA'),
            ('Saturday','8:00–9:00'):   ('BCom','Auditing','Sem3 SecA'),
        }

        outer, gc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(gc, 'Weekly Schedule', C['teal'], '📅')

        grid = tk.Frame(gc, bg=C['bg3']); grid.pack(fill='x', padx=10, pady=10)

        # Header
        tk.Label(grid, text='Period', font=FT['small_b'],
                 bg=C['brown'], fg=C['white'], width=14, pady=10, relief='flat'
                 ).grid(row=0,column=0,padx=1,pady=1,sticky='nsew')
        for j, day in enumerate(days):
            bg = C['teal'] if day==today else C['brown']
            tk.Label(grid, text=day, font=FT['small_b'],
                     bg=bg, fg=C['white'], width=14, pady=10, relief='flat'
                     ).grid(row=0,column=j+1,padx=1,pady=1,sticky='nsew')

        for i, period in enumerate(periods):
            tk.Label(grid, text=period, font=FT['small_b'],
                     bg=C['card'], fg=C['text2'], width=14, pady=8, relief='flat'
                     ).grid(row=i+1,column=0,padx=1,pady=1,sticky='nsew')
            for j, day in enumerate(days):
                entry = sample.get((day, period))
                if entry:
                    dept, subj, sec = entry
                    bg = DEPARTMENTS.get(dept,{}).get('color', C['brown_light'])
                    cell = tk.Frame(grid, bg=bg, height=55)
                    cell.grid(row=i+1,column=j+1,padx=1,pady=1,sticky='nsew')
                    cell.pack_propagate(False)
                    tk.Label(cell,text=dept, font=FT['small_b'],
                             bg=bg,fg='white').pack()
                    tk.Label(cell,text=subj[:16],font=('Segoe UI',7),
                             bg=bg,fg='white').pack()
                    tk.Label(cell,text=sec,font=('Segoe UI',7),
                             bg=bg,fg='white').pack()
                else:
                    tk.Frame(grid,bg=C['card2'],height=55
                             ).grid(row=i+1,column=j+1,padx=1,pady=1,sticky='nsew')

        for c in range(len(days)+1):
            grid.columnconfigure(c, weight=1)

        # Lecture notes
        outer2, nc = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(nc, 'Lecture Notes / Today\'s Agenda', C['brown'], '📝')
        nf = tk.Frame(nc, bg=C['card'], padx=15, pady=10); nf.pack(fill='x')
        notes = scrolledtext.ScrolledText(nf, height=5, bg=C['bg2'], fg=C['text'],
                                           font=FT['body'], relief='flat', wrap='word',
                                           highlightthickness=1, highlightbackground=C['card_border'])
        notes.pack(fill='x')
        notes.insert('end','Type your lecture notes or today\'s agenda here...')
        brow = tk.Frame(nc, bg=C['card'], padx=15, pady=8); brow.pack(fill='x')
        action_btn(brow,'💾 Save Notes', lambda: messagebox.showinfo('Saved','Notes saved!'),
                   C['teal'], padx=18, pady=8).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════
    #  PAGE 12 — ANNOUNCEMENTS
    # ══════════════════════════════════════════════════════════
    def _pg_announcements(self):
        self._pg_header('📢  Announcements', 'Post class notices & alerts', C['red'])
        main = scrollable_page(self.page_area)

        outer, ac = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)
        section_header(ac, 'Post Announcement', C['red'], '📢')

        ag = tk.Frame(ac, bg=C['card']); ag.pack(fill='x', padx=15, pady=12)
        ag.columnconfigure(1,weight=1); ag.columnconfigure(3,weight=1)
        atodept_v = tk.StringVar(value='All'); atosem_v = tk.StringVar(value='All')
        atosc_v   = tk.StringVar(value='All'); apri_v   = tk.StringVar(value='Normal')
        atitle_v  = tk.StringVar()

        label_entry_row(ag,'📤 To Dept:',  atodept_v,0,0,combo_vals=['All']+list(DEPARTMENTS.keys()))
        label_entry_row(ag,'📅 Semester:', atosem_v, 0,1,combo_vals=['All']+[str(i) for i in range(1,9)])
        label_entry_row(ag,'📌 Section:',  atosc_v,  1,0,combo_vals=['All','A','B','C'])
        label_entry_row(ag,'⚡ Priority:', apri_v,   1,1,combo_vals=['Normal','Important','Urgent'])
        label_entry_row(ag,'📋 Title:',   atitle_v, 2,0, width=50)

        msg_f = tk.Frame(ac, bg=C['card'], padx=15); msg_f.pack(fill='x')
        tk.Label(msg_f, text='📝 Message:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w')
        msg_box = tk.Text(msg_f, height=5, bg=C['bg2'], fg=C['text'],
                          font=FT['body'], relief='flat', wrap='word',
                          highlightthickness=1, highlightbackground=C['card_border'])
        msg_box.pack(fill='x', pady=5)

        outer2, al = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(al, 'Posted Announcements', C['brown'], '📋')
        acols = ('Date','To','Priority','Title','Message')
        af, atree = make_tree(al, acols, [100,180,100,200,280], height=8)
        af.pack(fill='x', padx=10, pady=(0,10))

        pri_colors = {'Normal':C['text'],'Important':C['orange'],'Urgent':C['red']}

        def post():
            title = atitle_v.get().strip()
            msg   = msg_box.get('1.0','end').strip()
            if not title or not msg:
                messagebox.showwarning('Missing','Title and message required.'); return
            dept = atodept_v.get(); sem = atosem_v.get(); sec = atosc_v.get()
            to = f"{dept} Sem{sem} Sec{sec}"
            pri = apri_v.get()
            tag = 'urgent' if pri=='Urgent' else 'imp' if pri=='Important' else 'odd'
            item = atree.insert('', 0, values=(str(date.today()), to, pri, title, msg[:60]),
                                tags=(tag,))
            atree.tag_configure('urgent', foreground=C['red'])
            atree.tag_configure('imp',    foreground=C['orange'])
            messagebox.showinfo('Posted', f'✅ Announcement "{title}" posted to {to}')
            atitle_v.set(''); msg_box.delete('1.0','end')

        brow = tk.Frame(ac, bg=C['card'], padx=15, pady=10); brow.pack(fill='x')
        action_btn(brow,'📢 Post Announcement', post, C['red'], padx=22, pady=10).pack(side='left', padx=8)

        # WhatsApp bulk alerts
        outer3, wc = card_frame(main)
        outer3.pack(fill='x', padx=25, pady=(0,15))
        section_header(wc, 'WhatsApp Parent Alerts', C['green'], '📱')
        wf = tk.Frame(wc, bg=C['card'], padx=15, pady=10); wf.pack(fill='x')
        wsid_v = tk.StringVar(); wdate_v = tk.StringVar(value=str(date.today()))
        tk.Label(wf, text='Student ID:', font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left')
        styled_entry(wf, wsid_v, 15).pack(side='left', padx=8)
        tk.Label(wf, text='Date:', font=FT['small_b'], bg=C['card'], fg=C['text3']).pack(side='left', padx=(15,4))
        styled_entry(wf, wdate_v, 13).pack(side='left', padx=8)
        wres_v = tk.StringVar()
        tk.Label(wc, textvariable=wres_v, font=FT['body_b'], bg=C['card'], fg=C['green']).pack(pady=4)
        def send_wa():
            sid = wsid_v.get().strip()
            if not sid: messagebox.showwarning('Missing','Enter student ID.'); return
            try:
                s = self.db.get_student_by_id(sid)
                if not s: messagebox.showerror('Not Found',f'{sid} not found.'); return
                from notification_service import notify_absent
                ok, msg = notify_absent(s.get('full_name',''), sid,
                                        s.get('class_name',''), s.get('phone',''), wdate_v.get())
                wres_v.set(f'{"✅" if ok else "❌"}  {msg}')
            except Exception as ex: messagebox.showerror('Error', str(ex))
        action_btn(wf,'📱 Send Alert', send_wa, C['green'], padx=16, pady=8).pack(side='left', padx=10)

    # ══════════════════════════════════════════════════════════
    #  PAGE 13 — REPORTS
    # ══════════════════════════════════════════════════════════
    def _pg_reports(self):
        self._pg_header('📈  Reports & Analytics', '', C['brown'])
        nb = ttk.Notebook(self.page_area)
        nb.pack(fill='both', expand=True, padx=25, pady=12)

        # Tab 1: Daily
        t1 = tk.Frame(nb, bg=C['bg']); nb.add(t1, text='📅  Daily Report')
        self._report_daily(t1)

        # Tab 2: Class-wise
        t2 = tk.Frame(nb, bg=C['bg']); nb.add(t2, text='🏛️  Class-wise')
        self._report_classwise(t2)

        # Tab 3: Student Analytics
        t3 = tk.Frame(nb, bg=C['bg']); nb.add(t3, text='👤  Student Analytics')
        self._report_student(t3)

        # Tab 4: Low Attendance
        t4 = tk.Frame(nb, bg=C['bg']); nb.add(t4, text='⚠️  Low Attendance')
        self._report_low(t4)

        # Tab 5: Export
        t5 = tk.Frame(nb, bg=C['bg']); nb.add(t5, text='📤  Export')
        self._report_export(t5)

    def _report_daily(self, parent):
        ctrl = tk.Frame(parent, bg=C['bg']); ctrl.pack(fill='x', padx=10, pady=10)
        dv = tk.StringVar(value=str(date.today()))
        cv = tk.StringVar(value='All')
        tk.Label(ctrl, text='Date:', font=FT['body_b'], bg=C['bg'], fg=C['text3']).pack(side='left')
        styled_entry(ctrl, dv, 13).pack(side='left', padx=6)
        tk.Label(ctrl, text='Class:', font=FT['body_b'], bg=C['bg'], fg=C['text3']).pack(side='left', padx=(15,4))
        try: classes = ['All'] + self.db.get_classes()
        except: classes = ['All']
        styled_combo(ctrl, cv, classes, 15).pack(side='left', padx=6)
        cols = ('ID','Student ID','Name','Class','Date','Time In','Time Out','Status')
        widths = [60,110,160,140,100,90,90,90]
        tf, tree = make_tree(parent, cols, widths, height=16)
        tf.pack(fill='both', expand=True, padx=10)
        def load():
            tree.delete(*tree.get_children())
            try:
                d = dv.get().strip() or None
                c = cv.get() if cv.get()!='All' else None
                recs = self.db.get_attendance(d, c)
                for i, r in enumerate(recs):
                    s = r.get('status','')
                    tree.insert('', 'end', values=(
                        r.get('id',''), r.get('student_id',''), r.get('full_name',''),
                        r.get('class_name',''), str(r.get('date','')),
                        str(r.get('time_in','')), str(r.get('time_out','')), s.upper()
                    ), tags=(s, 'odd' if i%2 else 'even'))
            except Exception as ex: messagebox.showerror('Error', str(ex))
        action_btn(ctrl, '🔍 Load', load, C['brown'], padx=16, pady=7).pack(side='left', padx=8)
        action_btn(ctrl, '📤 CSV', lambda: self._export_tree_csv(tree), C['green'], padx=12, pady=7).pack(side='left')
        load()

    def _report_classwise(self, parent):
        dept_v = tk.StringVar(value='BCA')
        ctrl = tk.Frame(parent, bg=C['bg']); ctrl.pack(fill='x', padx=10, pady=10)
        tk.Label(ctrl, text='Department:', font=FT['body_b'], bg=C['bg'], fg=C['text3']).pack(side='left')
        styled_combo(ctrl, dept_v, list(DEPARTMENTS.keys()), 14).pack(side='left', padx=8)
        res_f = tk.Frame(parent, bg=C['bg']); res_f.pack(fill='both', expand=True, padx=10)
        def load(*_):
            for w in res_f.winfo_children(): w.destroy()
            dept = dept_v.get(); info = DEPARTMENTS.get(dept, {})
            color = info.get('color', C['brown'])
            for sem in range(1, info.get('sems',6)+1):
                for sec in info.get('sections',['A']):
                    cls = f"{dept} Sem{sem} Sec{sec}"
                    try:
                        recs = self.db.get_attendance(filter_class=cls)
                        total = len(recs)
                        present = sum(1 for r in recs if r.get('status') in ('present','late'))
                        pct = round(present/total*100,1) if total else 0
                    except: total=present=0; pct=0
                    row = tk.Frame(res_f, bg=C['card'], pady=8); row.pack(fill='x', pady=2)
                    tk.Label(row, text=cls, font=FT['body_b'], bg=C['card'],
                             fg=color, width=22, anchor='w').pack(side='left', padx=15)
                    tk.Label(row, text=f'Total: {total}', font=FT['body'],
                             bg=C['card'], fg=C['text3'], width=10).pack(side='left')
                    tk.Label(row, text=f'Present: {present}', font=FT['body'],
                             bg=C['card'], fg=C['green'], width=14).pack(side='left')
                    bar_bg = tk.Frame(row, bg=C['bg3'], height=16, width=220)
                    bar_bg.pack(side='left', padx=8); bar_bg.pack_propagate(False)
                    if pct>0:
                        fill = tk.Frame(bar_bg, bg=color, height=16, width=int(2.2*pct))
                        fill.place(x=0,y=0,relheight=1)
                    tk.Label(row, text=f'{pct}%', font=('Consolas',10,'bold'),
                             bg=C['card'], fg=color, width=7).pack(side='left')
        dept_v.trace_add('write', load)
        action_btn(ctrl, '🔍 Load', load, C['brown'], padx=16, pady=7).pack(side='left', padx=8)
        load()

    def _report_student(self, parent):
        ctrl = tk.Frame(parent, bg=C['bg']); ctrl.pack(fill='x', padx=10, pady=10)
        sv = tk.StringVar()
        tk.Label(ctrl, text='Student ID:', font=FT['body_b'], bg=C['bg'], fg=C['text3']).pack(side='left')
        styled_entry(ctrl, sv, 18).pack(side='left', padx=8)
        res_f = tk.Frame(parent, bg=C['bg']); res_f.pack(fill='both', expand=True, padx=10)
        def analyze():
            for w in res_f.winfo_children(): w.destroy()
            sid = sv.get().strip()
            if not sid: return
            try:
                summ = self.db.get_student_attendance_summary(sid)
                s    = self.db.get_student_by_id(sid)
                name = s.get('full_name', sid) if s else sid
                tk.Label(res_f, text=f'📊  {name} ({sid})',
                         font=('Georgia',15,'bold'), bg=C['bg'], fg=C['brown']).pack(pady=12)
                sr = tk.Frame(res_f, bg=C['bg']); sr.pack()
                for t2,v2,c2 in [
                    ('Total Days',  summ['total'],   C['blue']),
                    ('Present',     summ['present'], C['green']),
                    ('Absent',      summ['absent'],  C['red']),
                    ('Attendance',  f"{summ['percentage']}%", C['brown'])
                ]:
                    card = tk.Frame(sr, bg=C['card'], padx=28, pady=18); card.pack(side='left', padx=12)
                    tk.Label(card, text=str(v2), font=('Georgia',26,'bold'), bg=C['card'], fg=c2).pack()
                    tk.Label(card, text=t2, font=FT['small'], bg=C['card'], fg=C['text3']).pack()
                pct = summ['percentage']
                if pct < 75:
                    w2 = tk.Frame(res_f, bg=C['red_bg'], pady=14); w2.pack(fill='x', pady=12)
                    tk.Label(w2, text=f'⚠️  DETAINMENT RISK — Attendance {pct}% (below 75% threshold)',
                             font=FT['body_b'], bg=C['red_bg'], fg=C['red']).pack()
                elif pct >= 90:
                    w2 = tk.Frame(res_f, bg=C['green_bg'], pady=14); w2.pack(fill='x', pady=12)
                    tk.Label(w2, text=f'🌟  EXCELLENT ATTENDANCE — {pct}%',
                             font=FT['body_b'], bg=C['green_bg'], fg=C['green']).pack()
            except Exception as ex:
                tk.Label(res_f, text=str(ex), bg=C['bg'], fg=C['red']).pack(pady=20)
        action_btn(ctrl, '📊 Analyze', analyze, C['brown'], padx=18, pady=7).pack(side='left', padx=8)

    def _report_low(self, parent):
        res_f = tk.Frame(parent, bg=C['bg']); res_f.pack(fill='both', expand=True, padx=10, pady=10)
        def check():
            for w in res_f.winfo_children(): w.destroy()
            tk.Label(res_f, text='Checking...', font=FT['body'], bg=C['bg'], fg=C['text3']).pack(pady=10)
            res_f.update()
            try:
                students = self.db.get_all_students()
                low = []
                for s in students:
                    try:
                        summ = self.db.get_student_attendance_summary(s['student_id'])
                        if summ['total'] > 0 and summ['percentage'] < 75:
                            low.append((s, summ))
                    except: pass
                for w in res_f.winfo_children(): w.destroy()
                if not low:
                    tk.Label(res_f, text='✅  All students above 75% attendance threshold!',
                             font=FT['body_b'], bg=C['green_bg'], fg=C['green'],
                             pady=20).pack(fill='x', padx=10)
                    return
                tk.Label(res_f, text=f'⚠️  {len(low)} students below 75% attendance:',
                         font=FT['body_b'], bg=C['red_bg'], fg=C['red'], pady=8
                         ).pack(fill='x', padx=0)
                for s, summ in sorted(low, key=lambda x: x[1]['percentage']):
                    r = tk.Frame(res_f, bg=C['card'], pady=8); r.pack(fill='x', pady=2)
                    tk.Label(r, text=f"⚠️  {s['full_name']} ({s['student_id']})",
                             font=FT['body_b'], bg=C['card'], fg=C['red']).pack(side='left', padx=15)
                    tk.Label(r, text=f"{summ['percentage']}%",
                             font=('Georgia',18,'bold'), bg=C['card'], fg=C['red']).pack(side='left', padx=10)
                    tk.Label(r, text=s.get('class_name',''),
                             font=FT['body'], bg=C['card'], fg=C['text3']).pack(side='left', padx=10)
                    action_btn(r,'📱 Alert',
                               lambda st=s: messagebox.showinfo('Alert',
                                   f'Alert for {st["full_name"]} — Phone: {st.get("phone","N/A")}'),
                               C['red'], padx=10, pady=5).pack(side='right', padx=10)
            except Exception as ex:
                tk.Label(res_f, text=str(ex), bg=C['bg'], fg=C['red']).pack()
        action_btn(parent, '🔍 Check Now', check, C['red'], padx=22, pady=10).pack(pady=10)
        check()

    def _report_export(self, parent):
        outer, ec = card_frame(parent)
        outer.pack(padx=25, pady=20)
        section_header(ec, 'Export Attendance Records', C['brown'], '📤')
        ef = tk.Frame(ec, bg=C['card'], padx=25, pady=15); ef.pack(fill='x')
        dv = tk.StringVar(value=str(date.today()))
        cv = tk.StringVar(value='All')
        tk.Label(ef, text='Date (or leave blank for all):', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w', pady=(0,4))
        styled_entry(ef, dv, 20).pack(anchor='w', pady=(0,12))
        tk.Label(ef, text='Filter by Class:', font=FT['small_b'],
                 bg=C['card'], fg=C['text3']).pack(anchor='w', pady=(0,4))
        try: classes = ['All'] + self.db.get_classes()
        except: classes = ['All']
        styled_combo(ef, cv, classes, 22).pack(anchor='w', pady=(0,15))

        def export(fmt):
            d = dv.get().strip() or None
            c = cv.get() if cv.get()!='All' else None
            ext = '.csv' if fmt=='csv' else '.xlsx'
            p = filedialog.asksaveasfilename(defaultextension=ext,
                filetypes=[('CSV','*.csv')] if fmt=='csv' else [('Excel','*.xlsx')],
                initialfile=f'attendance_{date.today()}{ext}')
            if not p: return
            try:
                ok = self.db.export_attendance_csv(p,d,c) if fmt=='csv' else \
                     self.db.export_attendance_excel(p,d,c)
                (messagebox.showinfo if ok else messagebox.showwarning)(
                    'Done' if ok else 'No Data',
                    f'Saved:\n{p}' if ok else 'No records to export.')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        brow = tk.Frame(ef, bg=C['card']); brow.pack(fill='x', pady=5)
        action_btn(brow,'📤 Export CSV',   lambda: export('csv'),  C['green'],  padx=22, pady=10).pack(side='left', padx=8)
        action_btn(brow,'📊 Export Excel', lambda: export('xlsx'), C['orange'], padx=22, pady=10).pack(side='left', padx=8)
        try:
            action_btn(brow,'📄 Generate PDF',
                       lambda: self._gen_pdf(), '#7B1FA2', padx=22, pady=10).pack(side='left', padx=8)
        except: pass

    def _gen_pdf(self):
        try:
            from pdf_reports import PDFReportGenerator
            PDFReportGenerator(self.db).show_dialog(self.page_area)
        except Exception as ex: messagebox.showerror('PDF Error', str(ex))

    # ══════════════════════════════════════════════════════════
    #  PAGE 14 — PROFILE
    # ══════════════════════════════════════════════════════════
    def _pg_profile(self):
        self._pg_header('👤  My Profile', 'View & update your information', C['brown'])
        main = scrollable_page(self.page_area)

        outer, pc = card_frame(main)
        outer.pack(fill='x', padx=25, pady=15)

        # Top section — avatar + info
        top = tk.Frame(pc, bg=C['card'])
        top.pack(fill='x')
        # Left avatar
        av_frame = tk.Frame(top, bg=C['brown'], width=120, height=120)
        av_frame.pack(side='left', padx=25, pady=20)
        av_frame.pack_propagate(False)
        tk.Label(av_frame, text='👩‍🏫', font=('Segoe UI',55),
                 bg=C['brown']).pack(expand=True)
        # Right info
        info_frame = tk.Frame(top, bg=C['card'])
        info_frame.pack(side='left', padx=10, pady=20, fill='both', expand=True)
        name = self.teacher.get('full_name','Teacher')
        tk.Label(info_frame, text=name, font=('Georgia',22,'bold'),
                 bg=C['card'], fg=C['brown']).pack(anchor='w')
        tk.Label(info_frame, text='Faculty  —  Vanita Vishram Women\'s University',
                 font=FT['body'], bg=C['card'], fg=C['text3']).pack(anchor='w')
        tk.Frame(info_frame, bg=C['card_border'], height=1).pack(fill='x', pady=10)

        fields = [
            ('Username:',  self.teacher.get('username','N/A')),
            ('Email:',     self.teacher.get('email','N/A')),
            ('Phone:',     self.teacher.get('phone','N/A')),
            ('Role:',      self.teacher.get('role','teacher').title()),
        ]
        for lbl, val in fields:
            r = tk.Frame(info_frame, bg=C['card']); r.pack(anchor='w', pady=3)
            tk.Label(r, text=lbl, font=FT['body_b'], bg=C['card'],
                     fg=C['text3'], width=12, anchor='e').pack(side='left')
            tk.Label(r, text=val, font=FT['body'], bg=C['card'],
                     fg=C['text']).pack(side='left', padx=8)

        # Stats strip
        try: today_att = len(self.db.get_today_attendance())
        except: today_att = 0
        stats_strip = tk.Frame(pc, bg=C['bg3'], pady=15)
        stats_strip.pack(fill='x')
        for title, val, color in [
            ('Attendance Marked Today', today_att, C['green']),
            ('Total Departments',       len(DEPARTMENTS), C['blue']),
            ('Subjects in Dept',        len(SUBJECTS.get(self.dept_var.get(),[])), C['brown']),
        ]:
            c = tk.Frame(stats_strip, bg=C['card'], padx=22, pady=12)
            c.pack(side='left', padx=15)
            tk.Label(c, text=str(val), font=('Georgia',22,'bold'), bg=C['card'], fg=color).pack()
            tk.Label(c, text=title, font=FT['small'], bg=C['card'], fg=C['text3']).pack()

        # Change password
        outer2, pwd_c = card_frame(main)
        outer2.pack(fill='x', padx=25, pady=(0,15))
        section_header(pwd_c, 'Change Password', C['brown2'], '🔒')
        pf = tk.Frame(pwd_c, bg=C['card'], padx=20, pady=15)
        pf.pack(fill='x')
        old_v = tk.StringVar(); new_v = tk.StringVar(); con_v = tk.StringVar()
        for lbl, var, r in [
            ('Current Password:', old_v, 0),
            ('New Password:',     new_v, 1),
            ('Confirm New:',      con_v, 2),
        ]:
            tk.Label(pf, text=lbl, font=FT['small_b'], bg=C['card'],
                     fg=C['text3'], width=18, anchor='e').grid(row=r, column=0, padx=(0,10), pady=8, sticky='e')
            styled_entry(pf, var, 25, show='*').grid(row=r, column=1, sticky='w', pady=8)

        pwd_res = tk.StringVar()
        tk.Label(pwd_c, textvariable=pwd_res, font=FT['body_b'],
                 bg=C['card'], fg=C['green']).pack(pady=4)

        def change_pwd():
            old=old_v.get(); new=new_v.get(); con=con_v.get()
            if not old or not new:
                messagebox.showwarning('Missing','Fill all password fields.'); return
            if new != con:
                messagebox.showerror('Mismatch','Passwords do not match.'); return
            if len(new) < 6:
                messagebox.showwarning('Weak','Min 6 characters.'); return
            try:
                self.db.change_password(self.teacher.get('username',''), new)
                pwd_res.set('✅  Password changed successfully!')
                for v in [old_v,new_v,con_v]: v.set('')
            except Exception as ex: messagebox.showerror('Error', str(ex))

        brow = tk.Frame(pwd_c, bg=C['card'], padx=20, pady=8); brow.pack(fill='x')
        action_btn(brow,'🔒 Change Password', change_pwd, C['brown2'], padx=22, pady=10).pack(side='left')

    # ══════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════
    def _export_tree_csv(self, tree):
        rows = [tree.item(i,'values') for i in tree.get_children()]
        if not rows:
            messagebox.showwarning('No Data','Nothing to export.'); return
        import csv
        p = filedialog.asksaveasfilename(defaultextension='.csv',
            filetypes=[('CSV','*.csv')], initialfile=f'export_{date.today()}.csv')
        if p:
            with open(p,'w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerows(rows)
            messagebox.showinfo('Exported',f'Saved:\n{p}')

    def _start_clock(self):
        def tick():
            self.clock_var.set(datetime.now().strftime('%a %d %b %Y  •  %I:%M:%S %p'))
            self.root.after(1000, tick)
        tick()

    def _logout(self):
        if self.live_on: self._stop_live()
        self.root.destroy()
        try:
            from login import LoginWindow
            r = tk.Tk(); LoginWindow(r); r.mainloop()
        except Exception as ex: print(f'Logout: {ex}')