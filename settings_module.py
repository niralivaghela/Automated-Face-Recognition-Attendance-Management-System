"""
Settings Module - Password, Admin Management, System Settings
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

COLORS = {
    'bg_dark': '#f5f5f0', 'bg_card': '#ffffff', 'bg_sidebar': '#8B4513',
    'accent': '#654321', 'text_light': '#333333', 'text_muted': '#666666',
    'success': '#2ecc71', 'warning': '#f39c12', 'danger': '#e74c3c', 'info': '#5DADE2',
}


class SettingsPage:
    def __init__(self, parent, db: DatabaseManager, admin_info):
        self.parent = parent
        self.db = db
        self.admin = admin_info
        self.build_ui()

    def build_ui(self):
        nb = ttk.Notebook(self.parent)
        nb.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure('TNotebook', background=COLORS['bg_dark'])
        style.configure('TNotebook.Tab', background=COLORS['bg_sidebar'], foreground='white',
                        padding=[15, 8], font=('Segoe UI', 10))
        style.map('TNotebook.Tab', background=[('selected', COLORS['accent'])])

        # Tab 0: My Profile  ← NEW
        tab0 = tk.Frame(nb, bg=COLORS['bg_dark'])
        nb.add(tab0, text="👤  My Profile")
        self._build_my_profile(tab0)

        # Tab 1: Change Password
        tab1 = tk.Frame(nb, bg=COLORS['bg_dark'])
        nb.add(tab1, text="🔑  Change Password")
        self._build_change_password(tab1)

        # Tab 2: Admin Management
        tab2 = tk.Frame(nb, bg=COLORS['bg_dark'])
        nb.add(tab2, text="👮  Admin Management")
        self._build_admin_management(tab2)

        # Tab 3: DB Config
        tab3 = tk.Frame(nb, bg=COLORS['bg_dark'])
        nb.add(tab3, text="🗄️  Database Config")
        self._build_db_config(tab3)

        # Tab 4: About
        tab4 = tk.Frame(nb, bg=COLORS['bg_dark'])
        nb.add(tab4, text="ℹ️  About")
        self._build_about(tab4)

    # ── Shared helpers ────────────────────────────────────────

    def _labeled_entry(self, parent, label, show=None, prefill=''):
        tk.Label(parent, text=label, bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(10, 3))
        var = tk.StringVar(value=prefill)
        kw = {'show': show} if show else {}
        tk.Entry(parent, textvariable=var, font=('Segoe UI', 12),
                 bg=COLORS['bg_card'], fg=COLORS['text_light'],
                 insertbackground=COLORS['text_light'],
                 relief='flat', **kw).pack(fill='x', ipady=8)
        return var

    # ══════════════════════════════════════════════════════════
    #  TAB 0 — MY PROFILE  (Update phone, email, name)
    # ══════════════════════════════════════════════════════════
    def _build_my_profile(self, parent):
        card = tk.Frame(parent, bg=COLORS['bg_dark'])
        card.pack(pady=20, padx=80, fill='x')

        # Header
        tk.Label(card, text="👤  My Profile",
                 font=('Segoe UI', 15, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack(pady=(0, 5))

        tk.Label(card,
                 text=f"Logged in as:  {self.admin.get('username', '')}",
                 font=('Segoe UI', 10),
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(pady=(0, 15))

        # ── Info banner ──────────────────────────────────────
        info = tk.Frame(card, bg='#E3F2FD', relief='flat')
        info.pack(fill='x', pady=(0, 15))
        tk.Label(info,
                 text="📱  Fill in your Phone Number to enable Phone OTP login",
                 bg='#E3F2FD', fg=COLORS['info'],
                 font=('Segoe UI', 10, 'bold')).pack(padx=15, pady=10)

        # ── Current values from DB ───────────────────────────
        try:
            current = self.db.get_admin_by_username(self.admin.get('username', ''))
        except Exception:
            current = self.admin

        current_phone = (current or {}).get('phone', '') or ''
        current_email = (current or {}).get('email', '') or ''
        current_name  = (current or {}).get('full_name', '') or ''

        # ── Fields ──────────────────────────────────────────
        self.prof_name  = self._labeled_entry(card, "Full Name", prefill=current_name)
        self.prof_email = self._labeled_entry(card, "Email Address", prefill=current_email)

        # Phone field with special blue highlight
        tk.Label(card, text="📱  Phone Number  (for OTP login)",
                 bg=COLORS['bg_dark'], fg=COLORS['info'],
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(12, 3))

        phone_frame = tk.Frame(card, bg=COLORS['info'], relief='flat', bd=2)
        phone_frame.pack(fill='x')
        self.prof_phone = tk.StringVar(value=current_phone)
        tk.Entry(phone_frame, textvariable=self.prof_phone,
                 font=('Segoe UI', 13, 'bold'),
                 bg=COLORS['bg_card'], fg=COLORS['info'],
                 insertbackground=COLORS['info'],
                 relief='flat').pack(fill='x', ipady=10, padx=2, pady=2)

        # Status label showing current saved phone
        self.phone_status_lbl = tk.Label(
            card,
            text=f"Current saved phone: {current_phone if current_phone else '(none — OTP login disabled)'}",
            bg=COLORS['bg_dark'],
            fg=COLORS['success'] if current_phone else COLORS['danger'],
            font=('Segoe UI', 9)
        )
        self.phone_status_lbl.pack(anchor='w', pady=(4, 0))

        # ── Save button ──────────────────────────────────────
        tk.Button(card, text="💾  Save Profile",
                  command=self._save_profile,
                  bg=COLORS['info'], fg='white',
                  font=('Segoe UI', 12, 'bold'),
                  relief='flat', pady=10, cursor='hand2').pack(fill='x', pady=20)

    def _save_profile(self):
        name  = self.prof_name.get().strip()
        email = self.prof_email.get().strip()
        phone = self.prof_phone.get().strip()

        # Validation
        if not name:
            messagebox.showerror("Error", "Full Name cannot be empty!"); return
        if email and '@' not in email:
            messagebox.showerror("Error", "Please enter a valid email address!"); return

        # Clean phone number — remove spaces, dashes, +91 prefix
        phone_clean = phone.replace(' ', '').replace('-', '').replace('+', '')
        if phone_clean.startswith('91') and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]

        if phone_clean and not phone_clean.isdigit():
            messagebox.showerror("Error", "Phone number should contain digits only!\nExample: 9876543210"); return
        if phone_clean and len(phone_clean) < 10:
            messagebox.showerror("Error", "Phone number must be at least 10 digits!"); return

        try:
            self.db.update_admin_profile(
                username  = self.admin['username'],
                full_name = name,
                email     = email,
                phone     = phone_clean or None
            )
            self.db.log_activity("UPDATE_PROFILE", self.admin['username'],
                                  f"Profile updated. Phone: {phone_clean or 'removed'}")

            # Update status label live
            self.phone_status_lbl.config(
                text=f"Current saved phone: {phone_clean if phone_clean else '(none — OTP login disabled)'}",
                fg=COLORS['success'] if phone_clean else COLORS['danger']
            )

            if phone_clean:
                messagebox.showinfo(
                    "✅ Profile Saved!",
                    f"Profile updated successfully!\n\n"
                    f"📱 Phone saved: {phone_clean}\n\n"
                    f"You can now login using Phone OTP with this number."
                )
            else:
                messagebox.showinfo("✅ Profile Saved", "Profile updated!\n(No phone number — OTP login disabled)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile:\n{e}")

    # ══════════════════════════════════════════════════════════
    #  TAB 1 — CHANGE PASSWORD
    # ══════════════════════════════════════════════════════════
    def _build_change_password(self, parent):
        card = tk.Frame(parent, bg=COLORS['bg_dark'])
        card.pack(pady=30, padx=80, fill='x')

        tk.Label(card, text="Change Your Password", font=('Segoe UI', 15, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack(pady=(0, 15))

        old_var  = self._labeled_entry(card, "Current Password", '●')
        new_var  = self._labeled_entry(card, "New Password", '●')
        conf_var = self._labeled_entry(card, "Confirm New Password", '●')

        def change():
            old  = old_var.get()
            new  = new_var.get()
            conf = conf_var.get()
            if not self.db.verify_admin(self.admin['username'], old):
                messagebox.showerror("Error", "Current password is incorrect!"); return
            if len(new) < 6:
                messagebox.showerror("Error", "New password must be at least 6 characters!"); return
            if new != conf:
                messagebox.showerror("Error", "Passwords do not match!"); return
            self.db.change_password(self.admin['username'], new)
            self.db.log_activity("CHANGE_PASSWORD", self.admin['username'], "Password changed")
            messagebox.showinfo("✅ Success", "Password changed successfully!")
            old_var.set(''); new_var.set(''); conf_var.set('')

        tk.Button(card, text="🔒  Change Password", command=change,
                  bg=COLORS['accent'], fg='white', font=('Segoe UI', 12, 'bold'),
                  relief='flat', pady=10, cursor='hand2').pack(fill='x', pady=20)

    # ══════════════════════════════════════════════════════════
    #  TAB 2 — ADMIN MANAGEMENT
    # ══════════════════════════════════════════════════════════
    def _build_admin_management(self, parent):
        form = tk.Frame(parent, bg=COLORS['bg_dark'])
        form.pack(fill='x', padx=30, pady=15)

        tk.Label(form, text="Add New Admin", font=('Segoe UI', 13, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack(anchor='w', pady=(0, 10))

        row1 = tk.Frame(form, bg=COLORS['bg_dark'])
        row1.pack(fill='x')
        for lbl in ['Username', 'Password', 'Full Name', 'Email', 'Phone']:
            col = tk.Frame(row1, bg=COLORS['bg_dark'])
            col.pack(side='left', expand=True, fill='x', padx=5)
            tk.Label(col, text=lbl, bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
                     font=('Segoe UI', 9)).pack(anchor='w')

        vars_ = {}
        row2 = tk.Frame(form, bg=COLORS['bg_dark'])
        row2.pack(fill='x')
        for k, show in [('username', None), ('password', '●'), ('full_name', None),
                        ('email', None), ('phone', None)]:
            col = tk.Frame(row2, bg=COLORS['bg_dark'])
            col.pack(side='left', expand=True, fill='x', padx=5, pady=3)
            var = tk.StringVar()
            kw  = {'show': show} if show else {}
            tk.Entry(col, textvariable=var, font=('Segoe UI', 10),
                     bg=COLORS['bg_card'], fg=COLORS['text_light'],
                     insertbackground=COLORS['text_light'],
                     relief='flat', **kw).pack(fill='x', ipady=6)
            vars_[k] = var

        def add_admin():
            if not vars_['username'].get() or not vars_['password'].get():
                messagebox.showerror("Error", "Username and Password are required!"); return
            try:
                self.db.add_admin(
                    vars_['username'].get(), vars_['password'].get(),
                    vars_['full_name'].get(), vars_['email'].get(),
                    vars_['phone'].get()
                )
                messagebox.showinfo("Success", "Admin added successfully!")
                for v in vars_.values(): v.set('')
                refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(form, text="➕  Add Admin", command=add_admin,
                  bg=COLORS['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=12, pady=6, cursor='hand2').pack(anchor='w', pady=8)

        tk.Frame(parent, bg=COLORS['accent'], height=2).pack(fill='x', padx=30, pady=5)

        tk.Label(parent, text="Current Admins", font=('Segoe UI', 12, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack(anchor='w', padx=30, pady=5)

        frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        frame.pack(fill='both', expand=True, padx=30)

        cols = ('ID', 'Username', 'Full Name', 'Email', 'Phone', 'Created At')
        style = ttk.Style()
        style.configure("Adm.Treeview", background=COLORS['bg_card'],
                        foreground=COLORS['text_light'], rowheight=26,
                        fieldbackground=COLORS['bg_card'], font=('Segoe UI', 10))
        style.configure("Adm.Treeview.Heading", background=COLORS['bg_sidebar'],
                        foreground=COLORS['text_light'], font=('Segoe UI', 10, 'bold'))
        tree = ttk.Treeview(frame, columns=cols, show='headings', style="Adm.Treeview", height=6)
        for col, w in zip(cols, [40, 110, 150, 180, 120, 140]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')
        tree.pack(fill='both', expand=True)

        def refresh_list():
            tree.delete(*tree.get_children())
            for a in self.db.get_all_admins():
                phone_val = a.get('phone', '') or '—'
                tree.insert('', 'end', values=(
                    a['id'], a['username'], a['full_name'],
                    a['email'], phone_val, str(a['created_at'])[:10]
                ))
        refresh_list()

    # ══════════════════════════════════════════════════════════
    #  TAB 3 — DATABASE CONFIG
    # ══════════════════════════════════════════════════════════
    def _build_db_config(self, parent):
        import database as db_module
        card = tk.Frame(parent, bg=COLORS['bg_dark'])
        card.pack(pady=30, padx=80, fill='x')

        tk.Label(card, text="MySQL Database Configuration", font=('Segoe UI', 14, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack(pady=(0, 20))

        cfg   = db_module.DB_CONFIG
        vars_ = {}
        for k, lbl in [('host', 'Host'), ('user', 'User'),
                       ('password', 'Password'), ('database', 'Database Name')]:
            tk.Label(card, text=lbl, bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
                     font=('Segoe UI', 10)).pack(anchor='w', pady=(8, 2))
            var  = tk.StringVar(value=cfg.get(k, ''))
            show = '●' if k == 'password' else None
            kw   = {'show': show} if show else {}
            tk.Entry(card, textvariable=var, font=('Segoe UI', 11),
                     bg=COLORS['bg_card'], fg=COLORS['text_light'],
                     insertbackground=COLORS['text_light'],
                     relief='flat', **kw).pack(fill='x', ipady=7)
            vars_[k] = var

        def save_config():
            for k, v in vars_.items():
                db_module.DB_CONFIG[k] = v.get()
            messagebox.showinfo("Saved", "Database config updated!\n(Restart required for full effect)")

        tk.Button(card, text="💾  Save Configuration", command=save_config,
                  bg=COLORS['info'], fg='white', font=('Segoe UI', 12, 'bold'),
                  relief='flat', pady=10, cursor='hand2').pack(fill='x', pady=20)

        tk.Label(card, text="⚠️  Edit database.py file to make config permanent.",
                 bg=COLORS['bg_dark'], fg=COLORS['warning'], font=('Segoe UI', 9)).pack()

    # ══════════════════════════════════════════════════════════
    #  TAB 4 — ABOUT
    # ══════════════════════════════════════════════════════════
    def _build_about(self, parent):
        card = tk.Frame(parent, bg=COLORS['bg_dark'])
        card.pack(expand=True)
        tk.Label(card, text="🎓", font=('Segoe UI Emoji', 50), bg=COLORS['bg_dark']).pack(pady=20)
        tk.Label(card, text="Face Detection Attendance System", font=('Segoe UI', 18, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light']).pack()
        tk.Label(card, text="Version 1.0", font=('Segoe UI', 12),
                 bg=COLORS['bg_dark'], fg=COLORS['accent']).pack(pady=5)
        tk.Label(card, text="Built with Python, OpenCV, Face Recognition, Tkinter, MySQL",
                 font=('Segoe UI', 10), bg=COLORS['bg_dark'], fg=COLORS['text_muted']).pack(pady=5)
        features = [
            "✅ Admin Login with SHA-256 password hashing",
            "✅ Student Registration with face capture",
            "✅ Live face recognition attendance",
            "✅ Automatic CSV export on each attendance",
            "✅ Manual attendance marking",
            "✅ Attendance reports with filters",
            "✅ Export to CSV and Excel",
            "✅ Activity log tracking",
            "✅ Multi-admin support",
            "✅ Phone OTP login support",
        ]
        for f in features:
            tk.Label(card, text=f, font=('Segoe UI', 10), bg=COLORS['bg_dark'],
                     fg=COLORS['text_light']).pack(anchor='w', padx=80)