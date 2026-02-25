"""
Students Module - Register, Edit, Delete with Face Capture
OpenCV Only - No dlib / No cmake required
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import cv2
import os
import numpy as np
from PIL import Image, ImageTk
from database import DatabaseManager
from datetime import datetime
from face_engine import (detect_faces, extract_face_roi,
                          encode_face, capture_face_encoding)

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

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'student_photos')
os.makedirs(PHOTOS_DIR, exist_ok=True)


class StudentsPage:
    def __init__(self, parent, db: DatabaseManager, admin_user):
        self.parent     = parent
        self.db         = db
        self.admin_user = admin_user
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self.parent, bg=WHITE)
        toolbar.pack(fill='x', pady=(0, 10))
        tk.Frame(toolbar, bg=BROWN, height=4).pack(fill='x')

        btn_row = tk.Frame(toolbar, bg=WHITE)
        btn_row.pack(fill='x', padx=10, pady=8)

        buttons = [
            ("➕  Add Student",         self.add_student_dialog, SUCCESS),
            ("✏️  Edit",                self.edit_selected,      INFO),
            ("🗑️  Delete",             self.delete_selected,    DANGER),
            ("🔄  Toggle Active",       self.toggle_status,      WARNING),
            ("📷  Re-capture Face",    self.recapture_face,     BROWN_LT),
        ]
        for label, cmd, color in buttons:
            tk.Button(btn_row, text=label, command=cmd,
                      bg=color, fg=WHITE, font=(FONT, 10, 'bold'),
                      relief='flat', padx=12, pady=7, cursor='hand2',
                      activebackground=BROWN2, activeforeground=WHITE
                      ).pack(side='left', padx=4)

        # Search
        tk.Label(btn_row, text="🔍", bg=WHITE, fg=MUTED,
                 font=(FONT, 12)).pack(side='right', padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *a: self.search_students())
        frm = tk.Frame(btn_row, bg=WHITE, relief='solid', bd=1)
        tk.Entry(frm, textvariable=self.search_var, font=(FONT, 11),
                 bg=WHITE, fg=DARK, insertbackground=BROWN,
                 relief='flat', bd=5, width=20).pack(fill='x')
        frm.pack(side='right', padx=4)

        # Stats row
        try:
            students = self.db.get_all_students()
            total  = len(students)
            active = sum(1 for s in students if s['status'] == 'active')
        except Exception:
            total = active = 0

        stats = tk.Frame(self.parent, bg=CREAM)
        stats.pack(fill='x', pady=(0, 8))
        for label, val, color in [
            ("Total Students", total, INFO),
            ("Active", active, SUCCESS),
            ("Inactive", total - active, DANGER),
        ]:
            c = tk.Frame(stats, bg=WHITE)
            c.pack(side='left', padx=6, pady=6)
            tk.Label(c, text=str(val), font=(FONT, 20, 'bold'),
                     bg=WHITE, fg=color).pack(padx=20, pady=(6, 0))
            tk.Label(c, text=label, font=(FONT, 9),
                     bg=WHITE, fg=MUTED).pack(padx=20, pady=(0, 6))

        # Table
        cols = ('Student ID', 'Full Name', 'Class', 'Section',
                'Email', 'Phone', 'Status', 'Registered')
        frame = tk.Frame(self.parent, bg=BG)
        frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Stu.Treeview", background=WHITE, foreground=DARK,
                        rowheight=30, fieldbackground=WHITE, font=(FONT, 10))
        style.configure("Stu.Treeview.Heading", background=BROWN,
                        foreground=WHITE, font=(FONT, 10, 'bold'))
        style.map("Stu.Treeview", background=[('selected', BROWN_LT)])

        self.tree = ttk.Treeview(frame, columns=cols, show='headings',
                                  style="Stu.Treeview")
        widths = [100, 160, 100, 80, 180, 110, 80, 120]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor='center')

        sy = ttk.Scrollbar(frame, orient='vertical',   command=self.tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side='right', fill='y')
        sx.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', lambda e: self.edit_selected())

    def refresh_table(self, students=None):
        self.tree.delete(*self.tree.get_children())
        rows = students if students is not None else self.db.get_all_students()
        for s in rows:
            tag = 'active' if s['status'] == 'active' else 'inactive'
            self.tree.insert('', 'end', values=(
                s['student_id'], s['full_name'], s['class_name'] or '',
                s['section'] or '', s['email'] or '', s['phone'] or '',
                s['status'].upper(), str(s['registered_at'])[:10]
            ), tags=(tag,))
        self.tree.tag_configure('active',   foreground=SUCCESS)
        self.tree.tag_configure('inactive', foreground=DANGER)

    def search_students(self):
        q = self.search_var.get().lower()
        all_s = self.db.get_all_students()
        filtered = [s for s in all_s if
                    q in s['student_id'].lower() or
                    q in s['full_name'].lower() or
                    q in (s['class_name'] or '').lower()]
        self.refresh_table(filtered)

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a student first.")
            return None
        return str(self.tree.item(sel[0])['values'][0])

    def add_student_dialog(self):
        self._student_form_dialog()

    def edit_selected(self):
        sid = self.get_selected_id()
        if sid:
            student = self.db.get_student_by_id(sid)
            self._student_form_dialog(student)

    def recapture_face(self):
        sid = self.get_selected_id()
        if sid:
            student = self.db.get_student_by_id(sid)
            self._student_form_dialog(student, face_only=True)

    # ════════════════════════════════════════════════════
    #  STUDENT FORM DIALOG
    # ════════════════════════════════════════════════════
    def _student_form_dialog(self, student=None, face_only=False):
        win = tk.Toplevel()
        is_edit = student is not None
        win.title("Edit Student" if is_edit else "Add New Student")
        win.configure(bg=BG)
        win.grab_set()
        win.resizable(False, False)

        # ── Window size based on screen height ───────────
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win_w = 620
        win_h = min(820, sh - 80)     # never taller than screen
        x = (sw // 2) - (win_w // 2)
        y = (sh // 2) - (win_h // 2)
        win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # ── Header (fixed top) ───────────────────────────
        tk.Frame(win, bg=BROWN, height=5).pack(fill='x')
        hdr = tk.Frame(win, bg=BROWN, height=50)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        title = "Edit Student" if is_edit else "➕  Register New Student"
        tk.Label(hdr, text=title, font=(FONT, 13, 'bold'),
                 bg=BROWN, fg=WHITE).pack(expand=True)
        tk.Frame(win, bg=GOLD, height=3).pack(fill='x')

        # ── SCROLLABLE body ──────────────────────────────
        scroll_container = tk.Frame(win, bg=BG)
        scroll_container.pack(fill='both', expand=True)

        canvas = tk.Canvas(scroll_container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        body = tk.Frame(canvas, bg=BG)
        body_window = canvas.create_window((0, 0), window=body, anchor='nw')

        def _on_body_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))

        def _on_canvas_configure(e):
            canvas.itemconfig(body_window, width=e.width)

        body.bind('<Configure>', _on_body_configure)
        canvas.bind('<Configure>', _on_canvas_configure)

        # Mouse wheel scroll
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        canvas.bind_all('<MouseWheel>', _on_mousewheel)

        # Inner padding frame
        inner = tk.Frame(body, bg=BG)
        inner.pack(fill='both', expand=True, padx=25, pady=10)

        entries = {}

        def make_field(parent, label, key, disabled=False):
            row = tk.Frame(parent, bg=BG)
            row.pack(fill='x', pady=4)
            tk.Label(row, text=label, width=13, anchor='w',
                     bg=BG, fg=DARK, font=(FONT, 10, 'bold')).pack(side='left')
            var = tk.StringVar(value=student.get(key, '') if student and student.get(key) else '')
            frm = tk.Frame(row, bg=WHITE, relief='solid', bd=1)
            ent = tk.Entry(frm, textvariable=var, font=(FONT, 11),
                           bg=WHITE, fg=DARK, insertbackground=BROWN,
                           relief='flat', bd=5)
            if disabled:
                ent.config(state='disabled', fg=MUTED)
            ent.pack(fill='x')
            frm.pack(side='left', fill='x', expand=True)
            entries[key] = var
            return var

        if not face_only:
            make_field(inner, "Student ID *", 'student_id', disabled=is_edit)
            make_field(inner, "Full Name *",  'full_name')
            make_field(inner, "Class",        'class_name')
            make_field(inner, "Section",      'section')
            make_field(inner, "Email",        'email')
            make_field(inner, "Phone",        'phone')

        # Face capture section
        tk.Frame(inner, bg=BROWN_LT, height=1).pack(fill='x', pady=10)
        face_hdr = tk.Frame(inner, bg=BG)
        face_hdr.pack(fill='x')
        tk.Label(face_hdr, text="📷  Face Registration (OpenCV)",
                 font=(FONT, 11, 'bold'), bg=BG, fg=BROWN).pack(side='left')
        tk.Label(face_hdr, text="No dlib needed ✅",
                 font=(FONT, 9), bg=BG, fg=SUCCESS).pack(side='right')

        # Camera preview — fixed pixel container
        cam_frame = tk.Frame(inner, bg='#1a1a1a', width=560, height=300)
        cam_frame.pack(pady=8, fill='x')
        cam_frame.pack_propagate(False)
        cam_lbl = tk.Label(cam_frame, bg='#1a1a1a',
                            text="📷  Click 'Open Camera' to start\n\n"
                                 "Make sure your face is well lit\n"
                                 "and look directly at the camera",
                            fg='#888888', font=(FONT, 11), justify='center')
        cam_lbl.pack(expand=True, fill='both')

        face_data    = {'encoding': None, 'photo_path': None}
        cap_holder   = [None]
        run_holder   = [False]
        capture_done = [False]

        def open_camera():
            # ✅ FIX: Show loading state immediately
            cam_lbl.config(text="⏳ Opening camera...", fg='#aaaaaa', image='')
            win.update()

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                cam_lbl.config(
                    text="❌ Cannot open camera!\n\n"
                         "• Check camera is connected\n"
                         "• Close other apps using camera\n"
                         "• Try unplugging and reconnecting",
                    fg=DANGER
                )
                messagebox.showerror("Camera Error",
                    "Cannot open camera!\n\n"
                    "• Make sure camera is connected\n"
                    "• Close apps like Zoom, Teams, Skype\n"
                    "• Try unplugging and reconnecting camera", parent=win)
                return

            # ✅ Set camera resolution for better quality
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            cap_holder[0] = cap
            run_holder[0] = True
            cam_btn.config(state='disabled', text="📷 Camera ON")
            cap_btn.config(state='normal')
            face_status.config(text="🟢 Camera running — position your face in the box", fg=SUCCESS)
            threading.Thread(target=preview_loop, daemon=True).start()

        def preview_loop():
            import time
            while run_holder[0] and cap_holder[0] and cap_holder[0].isOpened():
                ret, frame = cap_holder[0].read()
                if not ret:
                    break
                # Draw face rectangles
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces_detected = detect_faces(gray)
                for (x, y, w, h) in faces_detected:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (46, 125, 50), 2)
                    cv2.putText(frame, "Face Detected!", (x, y - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (46, 125, 50), 2)
                # ✅ FIX: resize to exactly fit 480x300 container maintaining aspect ratio
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img.thumbnail((480, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                if run_holder[0]:
                    win.after(0, lambda p=photo: update_preview(p))
                time.sleep(0.03)   # ✅ FIX: ~30fps cap, prevents thread crash

        def update_preview(photo):
            cam_lbl.config(image=photo, text='')
            cam_lbl.image = photo

        def capture_face():
            if not cap_holder[0]:
                messagebox.showwarning("Camera", "Open camera first.", parent=win)
                return
            face_status.config(text="⏳ Capturing face... hold still for 2 seconds", fg=WARNING)
            cap_btn.config(state='disabled')
            win.update()

            # ✅ FIX: run capture in background so UI doesn't freeze
            def _do_capture():
                enc, sample_frame = capture_face_encoding(cap_holder[0], num_samples=15)

                if enc is None:
                    win.after(0, lambda: (
                        face_status.config(text="❌ No face detected. Try again.", fg=DANGER),
                        cap_btn.config(state='normal')
                    ))
                    return

                face_data['encoding'] = enc

                # Save photo
                sid = entries.get('student_id', tk.StringVar()).get().strip() \
                      if not face_only else (student['student_id'] if student else 'temp')
                fname = f"{sid}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                photo_path = os.path.join(PHOTOS_DIR, fname)
                if sample_frame is not None:
                    cv2.imwrite(photo_path, sample_frame)
                    face_data['photo_path'] = photo_path

                # Stop camera preview
                run_holder[0] = False
                if cap_holder[0]:
                    cap_holder[0].release()
                    cap_holder[0] = None

                capture_done[0] = True

                # Show captured photo in preview
                def _update_ui():
                    face_status.config(text="✅ Face captured successfully!", fg=SUCCESS)
                    cap_btn.config(state='disabled')
                    cam_btn.config(state='normal', text="📷 Open Camera")
                    try:
                        if sample_frame is not None:
                            rgb   = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
                            img   = Image.fromarray(rgb)
                            img.thumbnail((480, 300), Image.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            cam_lbl.config(image=photo, text='')
                            cam_lbl.image = photo
                    except Exception:
                        pass

                win.after(0, _update_ui)

            threading.Thread(target=_do_capture, daemon=True).start()

        btn_row2 = tk.Frame(inner, bg=BG)
        btn_row2.pack(fill='x')
        cam_btn = tk.Button(btn_row2, text="📷 Open Camera", command=open_camera,
                             bg=INFO, fg=WHITE, font=(FONT, 10, 'bold'),
                             relief='flat', padx=12, pady=6, cursor='hand2')
        cam_btn.pack(side='left', padx=(0, 6))
        cap_btn = tk.Button(btn_row2, text="⚡ Capture Face", command=capture_face,
                             bg=BROWN, fg=WHITE, font=(FONT, 10, 'bold'),
                             relief='flat', padx=12, pady=6, cursor='hand2',
                             state='disabled')
        cap_btn.pack(side='left')

        face_status = tk.Label(inner, text="", bg=BG, font=(FONT, 10))
        face_status.pack(anchor='w', pady=3)

        # Pre-fill status if editing and already has face
        if is_edit and student and student.get('face_encoding') is not None:
            face_status.config(text="✅ Face already registered — capture new to update",
                               fg=SUCCESS)

        # ── FIXED FOOTER — Save button always visible ────
        tk.Frame(win, bg=BROWN_LT, height=1).pack(fill='x', side='bottom')
        footer = tk.Frame(win, bg=BG)
        footer.pack(fill='x', side='bottom', padx=25, pady=10)

        # Save button
        def save():
            run_holder[0] = False
            if cap_holder[0]:
                cap_holder[0].release()

            if not face_only:
                sid   = entries.get('student_id', tk.StringVar()).get().strip()
                fname = entries.get('full_name',  tk.StringVar()).get().strip()
                if not sid or not fname:
                    messagebox.showerror("Error", "Student ID and Full Name are required!", parent=win)
                    return

            enc = face_data.get('encoding')

            if not is_edit:
                # New student
                if enc is None:
                    if not messagebox.askyesno("No Face",
                        "No face captured. Save without face recognition?", parent=win):
                        return
                try:
                    self.db.add_student(
                        entries['student_id'].get().strip(),
                        entries['full_name'].get().strip(),
                        entries['class_name'].get().strip(),
                        entries['section'].get().strip(),
                        entries['email'].get().strip(),
                        entries['phone'].get().strip(),
                        enc, face_data.get('photo_path'))
                    self.db.log_activity("ADD_STUDENT", self.admin_user,
                                          f"Added {entries['student_id'].get().strip()}")
                    messagebox.showinfo("✅ Saved", "Student registered successfully!", parent=win)
                    win.destroy()
                    self.refresh_table()
                except Exception as e:
                    if '1062' in str(e):
                        messagebox.showerror("Duplicate", "Student ID already exists!", parent=win)
                    else:
                        messagebox.showerror("Error", str(e), parent=win)
            else:
                # Edit
                if face_only:
                    if enc is None:
                        messagebox.showwarning("No Face", "Please capture face first.", parent=win)
                        return
                    self.db.update_student_face(student['student_id'], enc, face_data.get('photo_path'))
                    messagebox.showinfo("✅ Updated", "Face updated successfully!", parent=win)
                    win.destroy()
                else:
                    self.db.update_student(
                        student['student_id'],
                        entries['full_name'].get().strip(),
                        entries['class_name'].get().strip(),
                        entries['section'].get().strip(),
                        entries['email'].get().strip(),
                        entries['phone'].get().strip())
                    if enc:
                        self.db.update_student_face(student['student_id'], enc, face_data.get('photo_path'))
                    self.db.log_activity("EDIT_STUDENT", self.admin_user,
                                          f"Edited {student['student_id']}")
                    messagebox.showinfo("✅ Updated", "Student updated successfully!", parent=win)
                    win.destroy()
                    self.refresh_table()

        tk.Button(footer, text="💾  Save Student", command=save,
                  bg=BROWN, fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2',
                  activebackground=BROWN2).pack(fill='x', ipady=11)

        def on_close():
            run_holder[0] = False
            if cap_holder[0]:
                cap_holder[0].release()
                cap_holder[0] = None
            canvas.unbind_all('<MouseWheel>')
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def delete_selected(self):
        sid = self.get_selected_id()
        if not sid: return
        if messagebox.askyesno("Confirm Delete",
            f"Delete student {sid} and ALL their attendance records?\nThis cannot be undone."):
            self.db.delete_student(sid)
            self.db.log_activity("DELETE_STUDENT", self.admin_user, f"Deleted {sid}")
            self.refresh_table()

    def toggle_status(self):
        sid = self.get_selected_id()
        if not sid: return
        self.db.toggle_student_status(sid)
        self.refresh_table()