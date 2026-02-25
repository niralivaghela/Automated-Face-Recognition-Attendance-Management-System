"""
Attendance Module - OpenCV Face Recognition
NO dlib / NO cmake / NO face_recognition library needed
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import numpy as np
from datetime import datetime, date
from database import DatabaseManager

try:
    from notification_service import notify_absent
    NOTIFY_AVAILABLE = True
except ImportError:
    NOTIFY_AVAILABLE = False

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


class AttendancePage:
    def __init__(self, parent, db: DatabaseManager, admin_user):
        self.parent       = parent
        self.db           = db
        self.admin_user   = admin_user
        self.cap          = None
        self.running      = False
        self.marked_today = set()
        self.frame_count  = 0
        self._photo_ref   = None
        self._last_frame_time = 0   # throttle UI updates
        self.known_faces  = []

        self.build_ui()
        self.load_known_faces()

    # ════════════════════════════════════════════════════
    #  LOAD FACES
    # ════════════════════════════════════════════════════
    def load_known_faces(self):
        """Load all student face encodings from DB."""
        try:
            data = self.db.get_all_face_encodings()
            self.known_faces = [
                (d[0], d[1], d[2], d[3])
                for d in data if d[3] is not None
            ]
            n = len(self.known_faces)
            self._set_status(
                f"✅  {n} face(s) loaded. Ready to start." if n > 0
                else "⚠️  No faces loaded. Add students with face capture first.",
                SUCCESS if n > 0 else WARNING
            )
        except Exception as e:
            self._set_status(f"⚠️  Could not load faces: {e}", WARNING)

    # ════════════════════════════════════════════════════
    #  UI BUILD
    # ════════════════════════════════════════════════════
    def build_ui(self):
        # ── Control bar ──────────────────────────────────
        ctrl = tk.Frame(self.parent, bg=WHITE)
        ctrl.pack(fill='x', pady=(0, 8))
        tk.Frame(ctrl, bg=BROWN, height=4).pack(fill='x')

        btn_row = tk.Frame(ctrl, bg=WHITE)
        btn_row.pack(fill='x', padx=12, pady=10)

        self.start_btn = tk.Button(
            btn_row, text="▶  Start Camera",
            command=self.start_camera,
            bg=SUCCESS, fg=WHITE, font=(FONT, 11, 'bold'),
            relief='flat', padx=16, pady=8, cursor='hand2'
        )
        self.start_btn.pack(side='left', padx=(0, 6))

        self.stop_btn = tk.Button(
            btn_row, text="⏹  Stop Camera",
            command=self.stop_camera,
            bg=DANGER, fg=WHITE, font=(FONT, 11, 'bold'),
            relief='flat', padx=16, pady=8, cursor='hand2',
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=6)

        tk.Button(
            btn_row, text="🔄  Reload Faces",
            command=self._reload_faces_safe,
            bg=INFO, fg=WHITE, font=(FONT, 11),
            relief='flat', padx=16, pady=8, cursor='hand2'
        ).pack(side='left', padx=6)

        tk.Button(
            btn_row, text="✏️  Manual Mark",
            command=self.manual_mark,
            bg=BROWN_LT, fg=WHITE, font=(FONT, 11),
            relief='flat', padx=16, pady=8, cursor='hand2'
        ).pack(side='left', padx=6)

        tk.Button(
            btn_row, text="📲  Send Absent Alerts",
            command=self.send_absent_alerts,
            bg='#7B1FA2', fg=WHITE, font=(FONT, 11),
            relief='flat', padx=16, pady=8, cursor='hand2'
        ).pack(side='left', padx=6)

        tk.Label(
            btn_row, text="⚡ OpenCV Mode",
            bg=WHITE, fg=GOLD, font=(FONT, 9, 'bold')
        ).pack(side='left', padx=12)

        self.status_lbl = tk.Label(
            btn_row, text="Loading...",
            bg=WHITE, fg=MUTED, font=(FONT, 10)
        )
        self.status_lbl.pack(side='right', padx=12)

        # ── Main split area ───────────────────────────────
        main = tk.Frame(self.parent, bg=BG)
        main.pack(fill='both', expand=True)

        # Camera panel
        cam_panel = tk.Frame(main, bg=WHITE)
        cam_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))
        tk.Frame(cam_panel, bg=BROWN, height=4).pack(fill='x')
        tk.Label(
            cam_panel, text="📷  Live Camera Feed",
            font=(FONT, 12, 'bold'), bg=WHITE, fg=BROWN
        ).pack(pady=(10, 4))

        self.video_label = tk.Label(
            cam_panel, bg='#1a1a1a',
            text="Camera is OFF\n\nClick  ▶ Start Camera  to begin\n\n"
                 "✅ No cmake or dlib required!\n"
                 "Uses OpenCV built-in face detection",
            fg='#888888', font=(FONT, 12), justify='center'
        )
        self.video_label.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Log panel
        log_panel = tk.Frame(main, bg=WHITE, width=310)
        log_panel.pack(side='right', fill='y')
        log_panel.pack_propagate(False)
        tk.Frame(log_panel, bg=BROWN, height=4).pack(fill='x')
        tk.Label(
            log_panel, text="✅  Recognized Today",
            font=(FONT, 12, 'bold'), bg=WHITE, fg=BROWN
        ).pack(pady=(10, 4))

        count_frame = tk.Frame(log_panel, bg=CREAM)
        count_frame.pack(fill='x', padx=10, pady=5)
        self.count_var = tk.StringVar(value="0")
        tk.Label(
            count_frame, textvariable=self.count_var,
            font=(FONT, 36, 'bold'), bg=CREAM, fg=BROWN
        ).pack()
        tk.Label(
            count_frame, text="Attendance Marked",
            font=(FONT, 9), bg=CREAM, fg=MUTED
        ).pack(pady=(0, 8))

        tk.Frame(log_panel, bg=GOLD, height=2).pack(fill='x', padx=10, pady=5)

        style = ttk.Style()
        style.configure("Log.Treeview", background=WHITE, foreground=DARK,
                        rowheight=26, fieldbackground=WHITE, font=(FONT, 9))
        style.configure("Log.Treeview.Heading", background=BROWN,
                        foreground=WHITE, font=(FONT, 9, 'bold'))
        style.map("Log.Treeview", background=[('selected', BROWN_LT)])

        cols = ('Name', 'Class', 'Time', 'Status')
        self.log_tree = ttk.Treeview(
            log_panel, columns=cols,
            show='headings', style="Log.Treeview", height=22
        )
        for col, w in zip(cols, [120, 75, 68, 68]):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=w, anchor='center')

        sy = ttk.Scrollbar(log_panel, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=sy.set)
        sy.pack(side='right', fill='y', padx=(0, 4))
        self.log_tree.pack(fill='both', expand=True, padx=(4, 0))

    def _set_status(self, text, color=None):
        """Safe status update — works from any thread."""
        self.parent.after(0, lambda: self.status_lbl.config(
            text=text, fg=color or MUTED
        ))

    def _reload_faces_safe(self):
        """Reload faces and clear today's session log."""
        self.load_known_faces()
        self.marked_today.clear()
        self.count_var.set("0")
        self.log_tree.delete(*self.log_tree.get_children())

    # ════════════════════════════════════════════════════
    #  CAMERA START / STOP
    # ════════════════════════════════════════════════════
    def start_camera(self):
        """Open camera in background thread so UI stays responsive."""
        try:
            import cv2
            from PIL import Image, ImageTk
        except ImportError as e:
            messagebox.showerror("Missing Library",
                f"Required library missing:\n{e}\n\n"
                "Run:\n  pip install opencv-python Pillow")
            return

        if self.running:
            return   # already running

        if not self.known_faces:
            messagebox.showwarning("No Faces",
                "No registered student faces found.\n\n"
                "Go to  Students → Add Student  and capture\n"
                "at least one student's face first.\n\n"
                "Then click  🔄 Reload Faces  and try again.")
            return

        # Disable button immediately to prevent double-click
        self.start_btn.config(state='disabled', text="⏳ Opening...")
        self._set_status("⏳  Opening camera...", MUTED)

        # Open camera in background so UI doesn't freeze
        def _open_cam():
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                self.parent.after(0, self._camera_open_failed)
                return

            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            self.cap = cap
            self.running = True
            self.frame_count = 0
            self._last_frame_time = 0

            self.parent.after(0, self._camera_opened_ok)
            self._video_loop()

        threading.Thread(target=_open_cam, daemon=True).start()

    def _camera_opened_ok(self):
        """Called on main thread after camera opens successfully."""
        self.start_btn.config(state='disabled', text="▶  Start Camera")
        self.stop_btn.config(state='normal')
        self._set_status("🟢  Camera running — looking for faces...", SUCCESS)

    def _camera_open_failed(self):
        """Called on main thread if camera failed to open."""
        self.start_btn.config(state='normal', text="▶  Start Camera")
        self._set_status("❌  Camera failed to open.", DANGER)
        messagebox.showerror("Camera Error",
            "Cannot open webcam!\n\n"
            "• Make sure camera is connected\n"
            "• Close apps using camera (Zoom, Teams, etc.)\n"
            "• Try a different USB port\n"
            "• Restart the application")

    def stop_camera(self):
        """Stop camera — safe to call from any thread."""
        self.running = False
        cap = self.cap
        self.cap = None
        if cap:
            try:
                cap.release()
            except Exception:
                pass

        # UI updates must happen on main thread
        def _update_ui():
            try:
                self.video_label.config(
                    image='',
                    text="Camera stopped.\n\nClick  ▶ Start Camera  to begin again.",
                    fg='#888888', font=(FONT, 12)
                )
                self.video_label.image = None
                self.start_btn.config(state='normal', text="▶  Start Camera")
                self.stop_btn.config(state='disabled')
                self._set_status("⏹  Camera stopped.", MUTED)
            except Exception:
                pass

        self.parent.after(0, _update_ui)

    # ════════════════════════════════════════════════════
    #  VIDEO LOOP  (runs in background thread)
    # ════════════════════════════════════════════════════
    def _video_loop(self):
        import cv2
        from PIL import Image, ImageTk
        from face_engine import detect_faces, extract_face_roi, encode_face, compare_faces

        THRESHOLD     = 7500
        PROCESS_EVERY = 3     # run face recognition every 3rd frame
        last_faces    = []    # cache last detected faces for smooth drawing

        while self.running:
            cap = self.cap
            if cap is None or not cap.isOpened():
                break

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            self.frame_count += 1
            display = frame.copy()

            # ── Face detection + recognition every Nth frame ──
            if self.frame_count % PROCESS_EVERY == 0:
                try:
                    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = detect_faces(gray)

                    # detect_faces may return empty tuple — convert safely
                    if len(faces) == 0:
                        last_faces = []
                    else:
                        last_faces = []
                        for (x, y, w, h) in faces:
                            live_enc  = encode_face(extract_face_roi(gray, x, y, w, h))
                            best_sid  = None
                            best_name = "Unknown"
                            best_cls  = ""
                            best_dist = 999999
                            box_color = (198, 40, 40)   # red

                            for sid, name, cls, stored_enc in self.known_faces:
                                try:
                                    stored_arr = np.array(stored_enc, dtype=np.float32)
                                    match, dist = compare_faces(stored_arr, live_enc, THRESHOLD)
                                    if match and dist < best_dist:
                                        best_dist = dist
                                        best_sid  = sid
                                        best_name = name
                                        best_cls  = cls or ''
                                        box_color = (46, 125, 50)   # green
                                except Exception:
                                    continue

                            # Mark attendance
                            if best_sid and best_sid not in self.marked_today:
                                try:
                                    ok = self.db.mark_attendance(best_sid, best_name, best_cls)
                                    if ok:
                                        self.marked_today.add(best_sid)
                                        now = datetime.now().strftime('%H:%M:%S')
                                        self.parent.after(
                                            0,
                                            lambda n=best_name, c=best_cls, t=now:
                                                self._add_log(n, c, t)
                                        )
                                        self.db.log_activity(
                                            "ATTENDANCE", self.admin_user,
                                            f"Face: {best_name} ({best_sid})"
                                        )
                                except Exception:
                                    pass

                            conf_pct = max(0, int(100 - (best_dist / THRESHOLD * 100)))
                            label    = f"{best_name}" + (f"  {conf_pct}%" if best_sid else "")
                            last_faces.append((x, y, w, h, box_color, label))
                except Exception:
                    pass

            # ── Draw cached face boxes on every frame ─────────
            for (x, y, w, h, box_color, label) in last_faces:
                cv2.rectangle(display, (x, y), (x+w, y+h), box_color, 2)
                cv2.rectangle(display, (x, y+h), (x+w, y+h+26), box_color, -1)
                cv2.putText(display, label,
                            (x+5, y+h+18),
                            cv2.FONT_HERSHEY_DUPLEX, 0.55,
                            (255, 255, 255), 1)

            # ── Convert and push frame to Tkinter UI ──────────
            try:
                rgb   = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
                img   = Image.fromarray(rgb)

                w_lbl = self.video_label.winfo_width()
                h_lbl = self.video_label.winfo_height()
                if w_lbl < 10: w_lbl = 640
                if h_lbl < 10: h_lbl = 480

                img.thumbnail((w_lbl, h_lbl), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                if self.running:
                    self.parent.after(0, lambda p=photo: self._update_frame(p))
            except Exception:
                pass

            time.sleep(0.033)   # ~30fps

        # Loop ended
        if self.running:
            self.parent.after(0, self.stop_camera)

    def _update_frame(self, photo):
        """Update video label with new frame — always clears any text."""
        if not self.running:
            return
        try:
            self._photo_ref = photo
            self.video_label.config(
                image=photo,
                text='',          # ← clear "Camera stopped" text
                bg='#1a1a1a'
            )
            self.video_label.image = photo   # prevent garbage collection
        except Exception:
            pass

    def _add_log(self, name, cls, time_str):
        """Add attendance entry to the log panel."""
        try:
            self.log_tree.insert('', 0,
                values=(name, cls, time_str, 'PRESENT'),
                tags=('present',))
            self.log_tree.tag_configure('present', foreground=SUCCESS)
            self.count_var.set(str(len(self.marked_today)))
            self._set_status(f"✅  Marked: {name} at {time_str}", SUCCESS)
        except Exception:
            pass

    # ════════════════════════════════════════════════════
    #  MANUAL MARK
    # ════════════════════════════════════════════════════
    def manual_mark(self):
        win = tk.Toplevel()
        win.title("Manual Attendance")
        win.geometry("400x300")
        win.configure(bg=BG)
        win.grab_set()
        win.resizable(False, False)

        # Center
        win.update_idletasks()
        x = (win.winfo_screenwidth()  // 2) - 200
        y = (win.winfo_screenheight() // 2) - 150
        win.geometry(f"400x300+{x}+{y}")

        tk.Frame(win, bg=BROWN, height=5).pack(fill='x')
        tk.Label(win, text="✏️  Manual Attendance",
                 font=(FONT, 13, 'bold'), bg=BG, fg=BROWN).pack(pady=(15, 5))

        body = tk.Frame(win, bg=BG)
        body.pack(fill='x', padx=35)

        tk.Label(body, text="Student ID:", bg=BG, fg=DARK,
                 font=(FONT, 11, 'bold')).pack(anchor='w', pady=(10, 3))
        sid_var = tk.StringVar()
        frm = tk.Frame(body, bg=WHITE, relief='solid', bd=1)
        sid_ent = tk.Entry(frm, textvariable=sid_var, font=(FONT, 12),
                           bg=WHITE, fg=DARK, insertbackground=BROWN,
                           relief='flat', bd=6)
        sid_ent.pack(fill='x')
        frm.pack(fill='x')
        sid_ent.focus()

        tk.Label(body, text="Status:", bg=BG, fg=DARK,
                 font=(FONT, 11, 'bold')).pack(anchor='w', pady=(10, 3))
        status_var = tk.StringVar(value='present')
        ttk.Combobox(body, textvariable=status_var,
                     values=['present', 'late', 'absent'],
                     state='readonly', font=(FONT, 11)).pack(fill='x')

        def submit():
            sid = sid_var.get().strip()
            if not sid:
                messagebox.showwarning("Input", "Enter Student ID.", parent=win)
                return
            student = self.db.get_student_by_id(sid)
            if not student:
                messagebox.showerror("Not Found", f"ID '{sid}' not found.", parent=win)
                return

            status = status_var.get()
            try:
                self.db.mark_attendance(sid, student['full_name'],
                                        student['class_name'], status)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)
                return

            # Send absent notification
            phone_msg = ""
            if status == 'absent' and NOTIFY_AVAILABLE:
                parent_phone = student.get('phone', '')
                today_str    = date.today().strftime('%d-%m-%Y')
                threading.Thread(
                    target=notify_absent,
                    args=(student['full_name'], sid,
                          student['class_name'] or '',
                          parent_phone, today_str),
                    daemon=True
                ).start()
                phone_msg = (f"\n📲 Alert sent to: {parent_phone}"
                             if parent_phone else "\n⚠️ No phone — alert not sent")

            messagebox.showinfo("✅ Done",
                f"Attendance marked!\n\n"
                f"Name   : {student['full_name']}\n"
                f"Status : {status.upper()}{phone_msg}", parent=win)
            win.destroy()

        tk.Button(win, text="✅  Mark Attendance", command=submit,
                  bg=BROWN, fg=WHITE, font=(FONT, 12, 'bold'),
                  relief='flat', cursor='hand2',
                  activebackground=BROWN2).pack(fill='x', padx=35, pady=18, ipady=10)
        win.bind('<Return>', lambda e: submit())

    # ════════════════════════════════════════════════════
    #  SEND ABSENT ALERTS
    # ════════════════════════════════════════════════════
    def send_absent_alerts(self):
        if not NOTIFY_AVAILABLE:
            messagebox.showerror("Missing File",
                "notification_service.py not found.\n"
                "Make sure it is in the same project folder.")
            return

        today     = date.today()
        today_str = today.strftime('%d-%m-%Y')

        try:
            all_students  = self.db.get_all_students()
            today_records = self.db.get_attendance(filter_date=str(today))
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
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

        if not absent_students:
            messagebox.showinfo("✅ All Present!",
                f"All active students are present today ({today_str})!\n"
                "No absent alerts to send. 🎉")
            return

        no_phone   = [s for s in absent_students if not s.get('phone')]
        with_phone = [s for s in absent_students if s.get('phone')]

        confirm_msg = (
            f"📲 Absent Alert Summary — {today_str}\n\n"
            f"Total absent   : {len(absent_students)}\n"
            f"Will notify    : {len(with_phone)} (have phone)\n"
            f"Will skip      : {len(no_phone)} (no phone)\n"
        )
        if with_phone:
            confirm_msg += "\nWill notify:\n"
            for s in with_phone[:5]:
                confirm_msg += f"  • {s['full_name']} → {s['phone']}\n"
            if len(with_phone) > 5:
                confirm_msg += f"  ... and {len(with_phone)-5} more\n"

        confirm_msg += "\nSend alerts now?"

        if not messagebox.askyesno("Send Absent Alerts", confirm_msg):
            return

        self._set_status("📲 Sending absent alerts...", '#7B1FA2')

        def _send_all():
            sent = failed = skipped = 0
            for s in absent_students:
                # Mark absent in DB
                try:
                    self.db.mark_attendance(
                        s['student_id'], s['full_name'],
                        s.get('class_name', ''), 'absent'
                    )
                except Exception:
                    pass

                phone = s.get('phone', '')
                if not phone:
                    skipped += 1
                    continue

                ok, msg = notify_absent(
                    s['full_name'], s['student_id'],
                    s.get('class_name', ''), phone, today_str
                )
                if ok:
                    sent += 1
                else:
                    failed += 1

                try:
                    self.db.log_activity(
                        "ABSENT_ALERT", self.admin_user,
                        f"{s['full_name']} ({s['student_id']}) → {phone}"
                    )
                except Exception:
                    pass

            result = (
                f"📲 Absent Alerts Done!\n\n"
                f"✅ Sent    : {sent}\n"
                f"❌ Failed  : {failed}\n"
                f"⏭️ Skipped : {skipped} (no phone)\n"
            )
            self.parent.after(0, lambda: (
                self._set_status(f"✅ Alerts sent: {sent}", SUCCESS),
                messagebox.showinfo("Alerts Done", result)
            ))

        threading.Thread(target=_send_all, daemon=True).start()