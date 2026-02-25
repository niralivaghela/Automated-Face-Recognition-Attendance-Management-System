"""
Login Window - Vanita Vishram Women's University
White & Brown Theme with College Logo
"""
import tkinter as tk
from tkinter import messagebox
import random, string, os, webbrowser
from PIL import Image, ImageTk
from database import DatabaseManager

# ── College Brand Palette (White & Brown) ─────────────────
BG       = '#FDFAF6'       # warm white background
BROWN    = '#6B2D0E'       # deep brown (primary)
BROWN2   = '#8B3A10'       # medium brown
BROWN_LT = '#C4783A'       # light brown / caramel
CREAM    = '#FFF3E0'       # cream card
GOLD     = '#D4A017'       # gold accent
WHITE    = '#FFFFFF'
DARK     = '#2C1A0E'       # very dark brown text
MUTED    = '#9E7B5A'       # muted brown text
SUCCESS  = '#2E7D32'
INFO     = '#1565C0'
WARNING  = '#E65100'
DANGER   = '#C62828'

FONT     = 'Segoe UI'

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'college_logo.png')

def _gen_otp(): return ''.join(random.choices(string.digits, k=6))
def _gen_token(): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def open_dashboard(root, user_info, role='admin'):
    """Open the correct dashboard based on role."""
    root.destroy()
    import tkinter as tk

    if role == 'student':
        from student_dashboard import StudentDashboard
        r = tk.Tk()
        StudentDashboard(r, user_info)
        r.mainloop()
    elif role == 'teacher':
        from teacher_dashboard import TeacherDashboard
        r = tk.Tk()
        TeacherDashboard(r, user_info)
        r.mainloop()
    else:
        from dashboard import Dashboard
        r = tk.Tk()
        Dashboard(r, user_info)
        r.mainloop()


# ══════════════════════════════════════════════════════════
class LoginWindow:
    """
    Login Window with 3 role tabs:
      🔴 Admin   — full system access
      🟡 Teacher — take attendance + reports
      🟢 Student — view own attendance + weekly summary
    """
    def __init__(self, root):
        self.root = root
        self.db   = DatabaseManager()
        self.otp  = None
        self._otp_admin = None
        self._role = 'admin'   # current tab role
        self.setup_window()
        self.build_ui()

    def setup_window(self):
        self.root.title("Vanita Vishram Women's University - Attendance System")
        self.root.geometry("520x720")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 260
        y = (self.root.winfo_screenheight() // 2) - 360
        self.root.geometry(f"520x720+{x}+{y}")

    def build_ui(self):
        # ── Top header ────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BROWN, height=170)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        try:
            img = Image.open(LOGO_PATH).resize((75, 75), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(img)
            tk.Label(hdr, image=self._logo, bg=BROWN).pack(pady=(14, 3))
        except Exception:
            tk.Label(hdr, text="🎓", font=(FONT+' Emoji', 36), bg=BROWN, fg=GOLD).pack(pady=(14, 3))

        tk.Label(hdr, text="Vanita Vishram Women's University",
                 font=(FONT, 13, 'bold'), bg=BROWN, fg=WHITE).pack()
        tk.Label(hdr, text="Face Detection Attendance System",
                 font=(FONT, 9), bg=BROWN, fg=GOLD).pack(pady=(2, 0))

        tk.Frame(self.root, bg=GOLD, height=3).pack(fill='x')

        # ── Role Tab bar ──────────────────────────────────
        tab_bar = tk.Frame(self.root, bg='#4a1e08', height=50)
        tab_bar.pack(fill='x')
        tab_bar.pack_propagate(False)

        self._role_btns = {}
        role_tabs = [
            ("🔴  Admin",    'admin',   '#C62828'),
            ("🟡  Teacher",  'teacher', '#E65100'),
            ("🟢  Student",  'student', '#2E7D32'),
        ]
        for label, role, color in role_tabs:
            btn = tk.Button(tab_bar, text=label,
                            command=lambda r=role, c=color: self._switch_role(r, c),
                            bg='#4a1e08', fg='#ccaa88',
                            font=(FONT, 10),
                            relief='flat', cursor='hand2')
            btn.pack(side='left', expand=True, fill='both')
            self._role_btns[role] = (btn, color)

        # ── Body ──────────────────────────────────────────
        self.body = tk.Frame(self.root, bg=CREAM)
        self.body.pack(fill='both', expand=True)

        self._role_frames = {}
        self._build_admin_frame()
        self._build_teacher_frame()
        self._build_student_frame()

        # ── Footer ────────────────────────────────────────
        foot = tk.Frame(self.root, bg=BROWN, height=42)
        foot.pack(fill='x', side='bottom')
        foot.pack_propagate(False)
        tk.Button(foot, text="Forgot Password?",
                  command=self.open_forgot,
                  bg=BROWN, fg=WHITE, font=(FONT, 10),
                  relief='flat', cursor='hand2').pack(side='right', padx=20, pady=8)

        # Default tab
        self._switch_role('admin', '#C62828')

    def _switch_role(self, role, color):
        self._role = role
        for r, (btn, c) in self._role_btns.items():
            if r == role:
                btn.config(bg=c, fg=WHITE, font=(FONT, 10, 'bold'))
            else:
                btn.config(bg='#4a1e08', fg='#ccaa88', font=(FONT, 10))

        for r, frame in self._role_frames.items():
            if r == role:
                frame.pack(fill='both', expand=True)
            else:
                frame.pack_forget()

    # ──────────────────────────────────────────────────────
    #  Shared helpers
    # ──────────────────────────────────────────────────────
    def _lbl(self, p, t):
        return tk.Label(p, text=t, bg=CREAM, fg=DARK, font=(FONT, 10, 'bold'))

    def _entry(self, p, var, show=None):
        kw = {'show': show} if show else {}
        f  = tk.Frame(p, bg=WHITE, relief='solid', bd=1)
        e  = tk.Entry(f, textvariable=var, font=(FONT, 12),
                      bg=WHITE, fg=DARK, insertbackground=BROWN,
                      relief='flat', bd=8, **kw)
        e.pack(fill='x')
        return f, e

    def _action_btn(self, p, text, cmd, color=None):
        c = color or BROWN
        return tk.Button(p, text=text, command=cmd,
                         bg=c, fg=WHITE, font=(FONT, 11, 'bold'),
                         relief='flat', cursor='hand2',
                         padx=10, activebackground=BROWN2,
                         activeforeground=WHITE)

    # ══════════════════════════════════════════════════════
    #  🔴 ADMIN FRAME
    # ══════════════════════════════════════════════════════
    def _build_admin_frame(self):
        frame = tk.Frame(self.body, bg=CREAM)
        self._role_frames['admin'] = frame

        # Role badge
        badge = tk.Frame(frame, bg='#C62828', height=28)
        badge.pack(fill='x')
        tk.Label(badge, text="🔴  Admin Portal — Full System Access",
                 font=(FONT, 9, 'bold'), bg='#C62828', fg=WHITE).pack(pady=5)

        tk.Label(frame, text="Welcome Back 👋",
                 font=(FONT, 14, 'bold'), bg=CREAM, fg=BROWN).pack(pady=(14, 2))
        tk.Label(frame, text="Sign in with your admin credentials",
                 font=(FONT, 9), bg=CREAM, fg=MUTED).pack()

        body = tk.Frame(frame, bg=CREAM)
        body.pack(fill='x', padx=35, pady=8)

        self._lbl(body, "Username or Email").pack(anchor='w', pady=(10, 3))
        self.un_var = tk.StringVar()
        frm, self._un_ent = self._entry(body, self.un_var)
        frm.pack(fill='x')

        self._lbl(body, "Password").pack(anchor='w', pady=(10, 3))
        self.pw_var = tk.StringVar()
        frm2, self.pw_ent = self._entry(body, self.pw_var, show='●')
        frm2.pack(fill='x')

        sp_row = tk.Frame(body, bg=CREAM)
        sp_row.pack(fill='x', pady=4)
        self._sp = tk.BooleanVar()
        tk.Checkbutton(sp_row, text="Show password", variable=self._sp,
                       command=lambda: self.pw_ent.config(show='' if self._sp.get() else '●'),
                       bg=CREAM, fg=MUTED, selectcolor=WHITE,
                       activebackground=CREAM, font=(FONT, 9)).pack(side='left')

        self._action_btn(body, "LOGIN AS ADMIN  →", self.login_admin, '#C62828').pack(
            fill='x', pady=12, ipady=10)

        tk.Label(body, text="Default: admin / admin123",
                 bg=CREAM, fg=MUTED, font=(FONT, 8)).pack()

        # Register + Google
        row = tk.Frame(frame, bg=CREAM)
        row.pack(fill='x', padx=35, pady=4)
        tk.Button(row, text="➕ Register Admin",
                  command=self.open_register,
                  bg=CREAM, fg=BROWN, font=(FONT, 9, 'bold'),
                  relief='solid', bd=1, cursor='hand2').pack(side='left', expand=True, fill='x', padx=(0, 4), ipady=6)
        tk.Button(row, text="🔵 Google Sign-In",
                  command=self.google_login,
                  bg=WHITE, fg='#444', font=(FONT, 9, 'bold'),
                  relief='solid', bd=1, cursor='hand2').pack(side='left', expand=True, fill='x', padx=(4, 0), ipady=6)

        self.root.bind('<Return>', lambda e: self.login_admin() if self._role == 'admin' else None)

    # ══════════════════════════════════════════════════════
    #  🟡 TEACHER FRAME
    # ══════════════════════════════════════════════════════
    def _build_teacher_frame(self):
        frame = tk.Frame(self.body, bg=CREAM)
        self._role_frames['teacher'] = frame

        badge = tk.Frame(frame, bg='#E65100', height=28)
        badge.pack(fill='x')
        tk.Label(badge, text="🟡  Teacher Portal — Take Attendance & View Reports",
                 font=(FONT, 9, 'bold'), bg='#E65100', fg=WHITE).pack(pady=5)

        tk.Label(frame, text="Teacher Login 👩‍🏫",
                 font=(FONT, 14, 'bold'), bg=CREAM, fg=BROWN).pack(pady=(14, 2))
        tk.Label(frame, text="Use your teacher credentials to sign in",
                 font=(FONT, 9), bg=CREAM, fg=MUTED).pack()

        body = tk.Frame(frame, bg=CREAM)
        body.pack(fill='x', padx=35, pady=10)

        self._lbl(body, "Teacher Username or Email").pack(anchor='w', pady=(10, 3))
        self.t_un_var = tk.StringVar()
        frm, _ = self._entry(body, self.t_un_var)
        frm.pack(fill='x')

        self._lbl(body, "Password").pack(anchor='w', pady=(10, 3))
        self.t_pw_var = tk.StringVar()
        frm2, t_pw_ent = self._entry(body, self.t_pw_var, show='●')
        frm2.pack(fill='x')

        sp_row = tk.Frame(body, bg=CREAM)
        sp_row.pack(fill='x', pady=4)
        t_sp = tk.BooleanVar()
        tk.Checkbutton(sp_row, text="Show password", variable=t_sp,
                       command=lambda: t_pw_ent.config(show='' if t_sp.get() else '●'),
                       bg=CREAM, fg=MUTED, selectcolor=WHITE,
                       activebackground=CREAM, font=(FONT, 9)).pack(side='left')

        self._action_btn(body, "LOGIN AS TEACHER  →", self.login_teacher, '#E65100').pack(
            fill='x', pady=12, ipady=10)

        # Info box
        info = tk.Frame(body, bg='#FFF8E1', relief='solid', bd=1)
        info.pack(fill='x', pady=6)
        tk.Label(info,
                 text="ℹ️  Teacher accounts are created by Admin.\n"
                      "Contact your administrator for credentials.",
                 bg='#FFF8E1', fg='#795548', font=(FONT, 9),
                 justify='left').pack(padx=10, pady=8, anchor='w')

        # ── What teachers can do ──────────────────────────
        tk.Label(frame, text="Teacher Access Includes:",
                 font=(FONT, 9, 'bold'), bg=CREAM, fg=BROWN).pack(pady=(4, 2))
        perms = tk.Frame(frame, bg=CREAM)
        perms.pack(fill='x', padx=40)
        for item in ["📸 Take Face Recognition Attendance",
                     "👥 View Student List",
                     "📊 View & Export Reports",
                     "📄 Generate PDF Reports"]:
            tk.Label(perms, text=f"  ✓  {item}",
                     bg=CREAM, fg=SUCCESS, font=(FONT, 9)).pack(anchor='w')

    # ══════════════════════════════════════════════════════
    #  🟢 STUDENT FRAME
    # ══════════════════════════════════════════════════════
    def _build_student_frame(self):
        frame = tk.Frame(self.body, bg=CREAM)
        self._role_frames['student'] = frame

        badge = tk.Frame(frame, bg='#2E7D32', height=28)
        badge.pack(fill='x')
        tk.Label(badge, text="🟢  Student Portal — View Your Attendance",
                 font=(FONT, 9, 'bold'), bg='#2E7D32', fg=WHITE).pack(pady=5)

        tk.Label(frame, text="Student Login 👩‍🎓",
                 font=(FONT, 14, 'bold'), bg=CREAM, fg=BROWN).pack(pady=(14, 2))
        tk.Label(frame, text="Enter your Student ID and phone number",
                 font=(FONT, 9), bg=CREAM, fg=MUTED).pack()

        body = tk.Frame(frame, bg=CREAM)
        body.pack(fill='x', padx=35, pady=10)

        self._lbl(body, "Student ID  (e.g. STU001)").pack(anchor='w', pady=(10, 3))
        self.s_id_var = tk.StringVar()
        frm, _ = self._entry(body, self.s_id_var)
        frm.pack(fill='x')

        self._lbl(body, "Password  (your registered phone number)").pack(anchor='w', pady=(10, 3))
        self.s_pw_var = tk.StringVar()
        frm2, s_pw_ent = self._entry(body, self.s_pw_var, show='●')
        frm2.pack(fill='x')

        sp_row = tk.Frame(body, bg=CREAM)
        sp_row.pack(fill='x', pady=4)
        s_sp = tk.BooleanVar()
        tk.Checkbutton(sp_row, text="Show password", variable=s_sp,
                       command=lambda: s_pw_ent.config(show='' if s_sp.get() else '●'),
                       bg=CREAM, fg=MUTED, selectcolor=WHITE,
                       activebackground=CREAM, font=(FONT, 9)).pack(side='left')

        self._action_btn(body, "VIEW MY ATTENDANCE  →", self.login_student, '#2E7D32').pack(
            fill='x', pady=12, ipady=10)

        # Info box
        info = tk.Frame(body, bg='#E8F5E9', relief='solid', bd=1)
        info.pack(fill='x', pady=6)
        tk.Label(info,
                 text="🔑  Your password is your registered phone number.\n"
                      "Contact Admin if you don't have access.",
                 bg='#E8F5E9', fg='#388E3C', font=(FONT, 9),
                 justify='left').pack(padx=10, pady=8, anchor='w')

        # ── What students can see ─────────────────────────
        tk.Label(frame, text="Student Access Includes:",
                 font=(FONT, 9, 'bold'), bg=CREAM, fg=BROWN).pack(pady=(4, 2))
        perms = tk.Frame(frame, bg=CREAM)
        perms.pack(fill='x', padx=40)
        for item in ["📅 Your attendance dashboard",
                     "📆 This week's attendance",
                     "📊 Monthly attendance %",
                     "📥 Download your report"]:
            tk.Label(perms, text=f"  ✓  {item}",
                     bg=CREAM, fg=SUCCESS, font=(FONT, 9)).pack(anchor='w')

    # ══════════════════════════════════════════════════════
    #  LOGIN HANDLERS
    # ══════════════════════════════════════════════════════
    def login_admin(self):
        un = self.un_var.get().strip()
        pw = self.pw_var.get().strip()
        if not un or not pw:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return
        try:
            # Try username + role=admin first, then email
            admin = self.db.verify_admin(un, pw)
            if not admin:
                admin = self.db.verify_admin_by_email(un, pw)
            # Accept admin role or any existing user without role set
            if admin and admin.get('role', 'admin') not in ('admin', None, ''):
                messagebox.showerror("Access Denied",
                    f"This account has role '{admin['role']}'.\n"
                    "Please use the correct login tab.")
                return
        except Exception as e:
            messagebox.showerror("DB Error", str(e)); return
        if admin:
            self.db.log_activity("LOGIN", admin['username'], "Admin login")
            open_dashboard(self.root, admin, role='admin')
        else:
            messagebox.showerror("Login Failed", "❌ Invalid username/email or password!")
            self.pw_var.set('')

    def login_teacher(self):
        un = self.t_un_var.get().strip()
        pw = self.t_pw_var.get().strip()
        if not un or not pw:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return
        try:
            teacher = self.db.verify_user_by_role(un, pw, 'teacher')
        except Exception as e:
            messagebox.showerror("DB Error", str(e)); return
        if teacher:
            self.db.log_activity("LOGIN", teacher['username'], "Teacher login")
            open_dashboard(self.root, teacher, role='teacher')
        else:
            messagebox.showerror("Login Failed",
                "❌ Invalid teacher credentials!\n\n"
                "Teacher accounts are created by Admin.\n"
                "Contact your administrator.")
            self.t_pw_var.set('')

    def login_student(self):
        sid = self.s_id_var.get().strip()
        pw  = self.s_pw_var.get().strip()
        if not sid or not pw:
            messagebox.showwarning("Input Error", "Please enter Student ID and phone number.")
            return
        try:
            student = self.db.verify_student_login(sid, pw)
        except Exception as e:
            messagebox.showerror("DB Error", str(e)); return
        if student:
            self.db.log_activity("LOGIN", student['student_id'], "Student login")
            open_dashboard(self.root, student, role='student')
        else:
            messagebox.showerror("Login Failed",
                "❌ Invalid Student ID or phone number!\n\n"
                "Your password is your registered phone number.\n"
                "Contact Admin if you need help.")
            self.s_pw_var.set('')

    def google_login(self):
        GoogleLoginWindow(self.root, self.db, lambda a: open_dashboard(self.root, a, role='admin'))

    def open_forgot(self):   ForgotPasswordWindow(self.root, self.db)
    def open_register(self): RegisterWindow(self.root, self.db)



# ══════════════════════════════════════════════════════════
#  GOOGLE LOGIN
# ══════════════════════════════════════════════════════════
class GoogleLoginWindow:
    def __init__(self, parent, db, on_success):
        self.db = db; self.on_success = on_success
        self.win = tk.Toplevel(parent)
        self.win.title("Google Sign-In")
        self.win.geometry("400x480")
        self.win.configure(bg=WHITE)
        self.win.resizable(False, False)
        self.win.grab_set()
        x = parent.winfo_x() + parent.winfo_width()//2 - 200
        y = parent.winfo_y() + parent.winfo_height()//2 - 240
        self.win.geometry(f"400x480+{x}+{y}")
        self._build()

    def _build(self):
        tk.Frame(self.win, bg='#4285F4', height=8).pack(fill='x')
        tk.Label(self.win, text="G", font=('Arial', 52, 'bold'),
                 bg=WHITE, fg='#4285F4').pack(pady=(20, 0))
        tk.Label(self.win, text="Sign in with Google",
                 font=(FONT, 15, 'bold'), bg=WHITE, fg='#202124').pack()
        tk.Label(self.win, text="Vanita Vishram Women's University",
                 font=(FONT, 9), bg=WHITE, fg='#5f6368').pack(pady=(2, 15))
        tk.Frame(self.win, bg='#dadce0', height=1).pack(fill='x', padx=30)

        body = tk.Frame(self.win, bg=WHITE)
        body.pack(fill='x', padx=30, pady=15)
        tk.Label(body, text="Admin Email", bg=WHITE, fg='#5f6368',
                 font=(FONT, 10)).pack(anchor='w', pady=(5, 4))
        self.g_email = tk.StringVar()
        em = tk.Entry(body, textvariable=self.g_email, font=(FONT, 12),
                      relief='solid', bd=1, fg='#202124')
        em.pack(fill='x', ipady=9)
        em.focus()
        tk.Label(body, text="ℹ️  Enter the email linked to your admin account.",
                 bg=WHITE, fg='#5f6368', font=(FONT, 9), justify='left').pack(anchor='w', pady=8)

        btn_row = tk.Frame(self.win, bg=WHITE)
        btn_row.pack(fill='x', padx=30, pady=15)
        tk.Button(btn_row, text="Cancel", command=self.win.destroy,
                  bg=WHITE, fg='#4285F4', font=(FONT, 11),
                  relief='flat', cursor='hand2').pack(side='left')
        tk.Button(btn_row, text="Next  →", command=self._auth,
                  bg='#4285F4', fg=WHITE, font=(FONT, 11, 'bold'),
                  relief='flat', cursor='hand2', padx=20, pady=8).pack(side='right')

        tk.Frame(self.win, bg='#dadce0', height=1).pack(fill='x', padx=30)
        tk.Button(self.win, text="🌐 Open Google Login in Browser",
                  command=lambda: webbrowser.open("https://accounts.google.com/signin"),
                  bg=WHITE, fg='#4285F4', font=(FONT, 9),
                  relief='flat', cursor='hand2').pack(pady=10)

    def _auth(self):
        email = self.g_email.get().strip()
        if not email or '@' not in email:
            messagebox.showerror("Invalid", "Enter a valid email.", parent=self.win); return
        try:
            admin = self.db.get_admin_by_email(email)
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self.win); return
        if not admin:
            messagebox.showerror(
                "Not Found",
                f"No account found for:\n{email}\n\n"
                "Please register first using the '➕ Register New Admin' button.",
                parent=self.win
            ); return
        self.db.log_activity("LOGIN", admin['username'], "Google login")
        messagebox.showinfo("✅ Welcome!", f"Logged in as {admin['full_name'] or admin['username']}", parent=self.win)
        self.win.destroy()
        self.on_success(admin)


# ══════════════════════════════════════════════════════════
#  REGISTER WINDOW  ✅ FIXED - Now saves phone & all fields
# ══════════════════════════════════════════════════════════
class RegisterWindow:
    def __init__(self, parent, db):
        self.db = db
        self.win = tk.Toplevel(parent)
        self.win.title("Register New Admin Account")
        self.win.geometry("460x650")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.grab_set()
        x = parent.winfo_x() + parent.winfo_width()//2 - 230
        y = parent.winfo_y() + parent.winfo_height()//2 - 325
        self.win.geometry(f"460x650+{x}+{y}")
        self._build()

    def _field(self, p, label, show=None):
        tk.Label(p, text=label, bg=BG, fg=DARK,
                 font=(FONT, 10, 'bold')).pack(anchor='w', pady=(10, 3))
        var = tk.StringVar()
        kw  = {'show': show} if show else {}
        frm = tk.Frame(p, bg=WHITE, relief='solid', bd=1)
        e   = tk.Entry(frm, textvariable=var, font=(FONT, 11),
                       bg=WHITE, fg=DARK, insertbackground=BROWN,
                       relief='flat', bd=6, **kw)
        e.pack(fill='x')
        frm.pack(fill='x')
        return var, e

    def _build(self):
        tk.Frame(self.win, bg=BROWN, height=6).pack(fill='x')

        hdr = tk.Frame(self.win, bg=BROWN, height=60)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text="➕  Create Admin Account",
                 font=(FONT, 13, 'bold'), bg=BROWN, fg=WHITE).pack(expand=True)

        tk.Frame(self.win, bg=GOLD, height=3).pack(fill='x')

        body = tk.Frame(self.win, bg=BG)
        body.pack(fill='x', padx=35)

        self.v_name,  _       = self._field(body, "Full Name  *")
        self.v_user,  _       = self._field(body, "Username  *  (min 3 chars)")
        self.v_email, _       = self._field(body, "Email Address  *")
        self.v_phone, _       = self._field(body, "📱 Phone Number  (required for OTP login)")
        self.v_pw,   _pw      = self._field(body, "Password  *  (min 6 chars)", show='●')
        self.v_conf, _cf      = self._field(body, "Confirm Password  *", show='●')
        self._pw_entries      = [_pw, _cf]

        self._show = tk.BooleanVar()
        tk.Checkbutton(body, text="Show passwords", variable=self._show,
                       command=self._toggle,
                       bg=BG, fg=MUTED, selectcolor=WHITE,
                       activebackground=BG, font=(FONT, 9)).pack(anchor='w', pady=5)

        # ✅ Info label about phone OTP
        tk.Label(body,
                 text="💡 Add your phone number to enable 📱 Phone OTP login",
                 bg=BG, fg=INFO, font=(FONT, 8), wraplength=380, justify='left').pack(anchor='w', pady=(0, 8))

        tk.Button(self.win, text="✅  Create Account",
                  command=self._register,
                  bg=BROWN, fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2',
                  activebackground=BROWN2).pack(fill='x', padx=35, pady=15, ipady=11)

    def _toggle(self):
        s = '' if self._show.get() else '●'
        for e in self._pw_entries: e.config(show=s)

    def _register(self):
        name  = self.v_name.get().strip()
        user  = self.v_user.get().strip()
        email = self.v_email.get().strip()
        phone = self.v_phone.get().strip()
        pw    = self.v_pw.get()
        conf  = self.v_conf.get()

        # ✅ Validation
        if not name or not user or not email or not pw:
            messagebox.showerror("Error", "Full Name, Username, Email & Password are required!", parent=self.win); return
        if len(user) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters.", parent=self.win); return
        if '@' not in email:
            messagebox.showerror("Error", "Please enter a valid email address.", parent=self.win); return
        if len(pw) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.", parent=self.win); return
        if pw != conf:
            messagebox.showerror("Error", "Passwords do not match!", parent=self.win); return

        # ✅ Phone number cleaning
        phone_clean = phone.replace(' ', '').replace('-', '')
        if phone_clean.startswith('+91'):
            phone_clean = phone_clean[3:]
        if phone_clean.startswith('91') and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]

        try:
            # ✅ FIX: Use register_admin which properly saves ALL fields including phone
            success, msg = self.db.register_admin(user, pw, name, email, phone_clean)
            if success:
                phone_msg = f"\nPhone: {phone_clean}" if phone_clean else "\n⚠️  No phone added (OTP login unavailable)"
                messagebox.showinfo(
                    "✅ Registered!",
                    f"Account created successfully!\n\n"
                    f"Username: {user}\n"
                    f"Email: {email}"
                    f"{phone_msg}\n\n"
                    f"You can now login with your username or email.",
                    parent=self.win
                )
                self.win.destroy()
            else:
                messagebox.showerror("Registration Failed", msg, parent=self.win)
        except Exception as e:
            if '1062' in str(e) or 'Duplicate' in str(e):
                messagebox.showerror("Already Exists", "Username or email already registered!", parent=self.win)
            else:
                messagebox.showerror("Error", str(e), parent=self.win)


# ══════════════════════════════════════════════════════════
#  FORGOT PASSWORD — 3 STEPS
# ══════════════════════════════════════════════════════════
class ForgotPasswordWindow:
    def __init__(self, parent, db):
        self.db=db; self.token=None; self.email=None
        self.win=tk.Toplevel(parent)
        self.win.title("Reset Password")
        self.win.geometry("420x440")
        self.win.configure(bg=BG)
        self.win.resizable(False,False)
        self.win.grab_set()
        x=parent.winfo_x()+parent.winfo_width()//2-210
        y=parent.winfo_y()+parent.winfo_height()//2-220
        self.win.geometry(f"420x440+{x}+{y}")
        self._step1()

    def _clear(self):
        for w in self.win.winfo_children(): w.destroy()

    def _progress(self, step):
        tk.Frame(self.win, bg=BROWN, height=4).pack(fill='x')
        bar=tk.Frame(self.win,bg=BG); bar.pack(fill='x',padx=40,pady=8)
        for i,lbl in enumerate(["① Email","② Token","③ New Password"]):
            active=(i+1==step); done=(i+1<step)
            col=SUCCESS if done else (BROWN if active else MUTED)
            tk.Label(bar,text=lbl,bg=BG,fg=col,
                     font=(FONT,10,'bold' if active else 'normal')).pack(side='left',expand=True)

    def _entry_field(self, p, label, show=None):
        tk.Label(p,text=label,bg=BG,fg=DARK,font=(FONT,10,'bold')).pack(anchor='w',pady=(12,3))
        var=tk.StringVar()
        kw={'show':show} if show else {}
        frm=tk.Frame(p,bg=WHITE,relief='solid',bd=1)
        tk.Entry(frm,textvariable=var,font=(FONT,12),bg=WHITE,fg=DARK,
                 insertbackground=BROWN,relief='flat',bd=6,**kw).pack(fill='x')
        frm.pack(fill='x')
        return var

    def _step1(self):
        self._clear()
        tk.Label(self.win,text="🔓  Forgot Password",font=(FONT,15,'bold'),bg=BG,fg=BROWN).pack(pady=(20,2))
        self._progress(1)
        body=tk.Frame(self.win,bg=BG); body.pack(fill='x',padx=40)
        self.em_var=self._entry_field(body,"Registered Email Address")
        tk.Label(body,text="A reset token will be generated and shown.",
                 bg=BG,fg=MUTED,font=(FONT,9)).pack(anchor='w',pady=6)
        tk.Button(body,text="📧  Generate Reset Token",command=self._send_token,
                  bg=BROWN,fg=WHITE,font=(FONT,12,'bold'),relief='flat',cursor='hand2',
                  activebackground=BROWN2).pack(fill='x',pady=15,ipady=10)

    def _send_token(self):
        email=self.em_var.get().strip()
        if not email or '@' not in email:
            messagebox.showerror("Invalid","Enter valid email.",parent=self.win); return
        try:
            admin=self.db.get_admin_by_email(email)
        except Exception as e:
            messagebox.showerror("DB Error",str(e),parent=self.win); return
        if not admin:
            messagebox.showerror("Not Found","No account with that email.",parent=self.win); return
        try: token=self.db.save_reset_token(email)
        except Exception: token=_gen_token()
        self.email=email; self.token=token
        print(f"\n[🔑 TOKEN for {email}]: {token}\n")
        messagebox.showinfo("Token Generated",f"Token generated!\n\n[Demo] Token:\n\n    {token}\n\nValid 15 minutes.",parent=self.win)
        self._step2()

    def _step2(self):
        self._clear()
        tk.Label(self.win,text="🔑  Verify Token",font=(FONT,15,'bold'),bg=BG,fg=BROWN).pack(pady=(20,2))
        self._progress(2)
        body=tk.Frame(self.win,bg=BG); body.pack(fill='x',padx=40)
        tk.Label(body,text="Paste Reset Token",bg=BG,fg=DARK,font=(FONT,10,'bold')).pack(anchor='w',pady=(12,3))
        self.tok_var=tk.StringVar(value=self.token or '')
        frm=tk.Frame(body,bg=WHITE,relief='solid',bd=1)
        tk.Entry(frm,textvariable=self.tok_var,font=(FONT,13,'bold'),bg=WHITE,fg=BROWN,
                 insertbackground=BROWN,relief='flat',bd=6,justify='center').pack(fill='x')
        frm.pack(fill='x')
        tk.Button(body,text="✅  Verify Token",command=self._verify_token,
                  bg=INFO,fg=WHITE,font=(FONT,12,'bold'),relief='flat',cursor='hand2').pack(fill='x',pady=20,ipady=10)
        tk.Button(body,text="← Back / Resend",command=self._step1,
                  bg=BG,fg=MUTED,font=(FONT,10),relief='flat',cursor='hand2').pack()

    def _verify_token(self):
        token=self.tok_var.get().strip()
        if not token: messagebox.showerror("Error","Enter token.",parent=self.win); return
        try: valid=self.db.verify_reset_token(token)
        except Exception: valid=(token==self.token)
        if valid: self.token=token; self._step3()
        else: messagebox.showerror("Invalid","Token invalid or expired.",parent=self.win)

    def _step3(self):
        self._clear()
        tk.Label(self.win,text="🔒  Set New Password",font=(FONT,15,'bold'),bg=BG,fg=BROWN).pack(pady=(20,2))
        self._progress(3)
        body=tk.Frame(self.win,bg=BG); body.pack(fill='x',padx=40)
        self.np_var=self._entry_field(body,"New Password  (min 6 chars)",show='●')
        self.cp_var=self._entry_field(body,"Confirm New Password",show='●')
        tk.Button(body,text="💾  Reset Password",command=self._do_reset,
                  bg=SUCCESS,fg=WHITE,font=(FONT,12,'bold'),relief='flat',cursor='hand2').pack(fill='x',pady=20,ipady=10)

    def _do_reset(self):
        pw=self.np_var.get(); conf=self.cp_var.get()
        if len(pw)<6: messagebox.showerror("Error","Min 6 chars.",parent=self.win); return
        if pw!=conf: messagebox.showerror("Error","Passwords don't match.",parent=self.win); return
        ok=False
        try: ok=self.db.reset_password_with_token(self.token,pw)
        except Exception: pass
        if not ok and self.email:
            try: self.db.change_password_by_email(self.email,pw); ok=True
            except Exception: pass
        if ok:
            messagebox.showinfo("✅ Success","Password reset!\nLogin with new password.",parent=self.win)
            self.win.destroy()
        else:
            messagebox.showerror("Error","Reset failed. Try again.",parent=self.win)