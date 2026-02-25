"""
Reports Module - Attendance Reports with Filters & Export
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import date, datetime, timedelta
from database import DatabaseManager

COLORS = {
    'bg_dark': '#f5f5f0', 'bg_card': '#ffffff', 'bg_sidebar': '#8B4513',
    'accent': '#654321', 'text_light': '#333333', 'text_muted': '#666666',
    'success': '#2ecc71', 'warning': '#f39c12', 'danger': '#e74c3c', 'info': '#5DADE2',
}


class ReportsPage:
    def __init__(self, parent, db: DatabaseManager):
        self.parent = parent
        self.db = db
        self.build_ui()
        self.load_report()

    def build_ui(self):
        # Filter toolbar
        filter_frame = tk.Frame(self.parent, bg=COLORS['bg_card'])
        filter_frame.pack(fill='x', pady=(0, 10), padx=2)

        tk.Label(filter_frame, text="📅 Date:", bg=COLORS['bg_card'], fg=COLORS['text_muted'],
                 font=('Segoe UI', 10)).pack(side='left', padx=(15, 5), pady=10)
        self.date_var = tk.StringVar(value=str(date.today()))
        tk.Entry(filter_frame, textvariable=self.date_var, width=12, font=('Segoe UI', 10),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light'],
                 insertbackground=COLORS['text_light']).pack(side='left', padx=5)

        tk.Label(filter_frame, text="Class:", bg=COLORS['bg_card'], fg=COLORS['text_muted'],
                 font=('Segoe UI', 10)).pack(side='left', padx=(15, 5))
        self.class_var = tk.StringVar(value='All')
        classes = ['All'] + self.db.get_classes()
        self.class_combo = ttk.Combobox(filter_frame, textvariable=self.class_var,
                                         values=classes, width=12, state='readonly')
        self.class_combo.pack(side='left', padx=5)

        tk.Label(filter_frame, text="Student:", bg=COLORS['bg_card'], fg=COLORS['text_muted'],
                 font=('Segoe UI', 10)).pack(side='left', padx=(15, 5))
        self.student_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.student_var, width=15, font=('Segoe UI', 10),
                 bg=COLORS['bg_dark'], fg=COLORS['text_light'],
                 insertbackground=COLORS['text_light']).pack(side='left', padx=5)

        tk.Button(filter_frame, text="🔍 Search", command=self.load_report,
                  bg=COLORS['info'], fg='white', font=('Segoe UI', 10),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='left', padx=8)

        tk.Button(filter_frame, text="All Records", command=self.load_all,
                  bg=COLORS['bg_sidebar'], fg='white', font=('Segoe UI', 10),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='left', padx=3)

        tk.Button(filter_frame, text="Today", command=self.load_today,
                  bg=COLORS['bg_sidebar'], fg='white', font=('Segoe UI', 10),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='left', padx=3)

        tk.Button(filter_frame, text="This Week", command=self.load_week,
                  bg=COLORS['bg_sidebar'], fg='white', font=('Segoe UI', 10),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='left', padx=3)

        # Export buttons
        tk.Button(filter_frame, text="📥 Export CSV", command=self.export_csv,
                  bg=COLORS['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='right', padx=5, pady=8)

        tk.Button(filter_frame, text="📄 Generate PDF", command=self.generate_pdf,
                  bg='#7B1FA2', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='right', padx=5, pady=8)

        tk.Button(filter_frame, text="📊 Export Excel", command=self.export_excel,
                  bg=COLORS['warning'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side='right', padx=5, pady=8)

        # Summary cards
        self.summary_frame = tk.Frame(self.parent, bg=COLORS['bg_dark'])
        self.summary_frame.pack(fill='x', pady=(0, 10))

        # Table
        cols = ('ID', 'Student ID', 'Full Name', 'Class', 'Date', 'Time In', 'Time Out', 'Status', 'Marked By')
        frame = tk.Frame(self.parent, bg=COLORS['bg_dark'])
        frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Rep.Treeview", background=COLORS['bg_card'],
                        foreground=COLORS['text_light'], rowheight=28,
                        fieldbackground=COLORS['bg_card'], font=('Segoe UI', 10))
        style.configure("Rep.Treeview.Heading", background=COLORS['bg_sidebar'],
                        foreground=COLORS['text_light'], font=('Segoe UI', 10, 'bold'))
        style.map("Rep.Treeview", background=[('selected', COLORS['accent'])])

        self.tree = ttk.Treeview(frame, columns=cols, show='headings', style="Rep.Treeview")
        widths = [50, 100, 150, 100, 100, 90, 90, 80, 120]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=w, anchor='center')

        sy = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side='right', fill='y')
        sx.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        self.records = []

    def load_report(self, records=None):
        if records is None:
            date_filter = self.date_var.get().strip() or None
            class_filter = self.class_var.get() if self.class_var.get() != 'All' else None
            student_filter = self.student_var.get().strip() or None
            try:
                if date_filter:
                    datetime.strptime(date_filter, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Date format: YYYY-MM-DD")
                return
            records = self.db.get_attendance(date_filter, class_filter, student_filter)

        self.records = records
        self.tree.delete(*self.tree.get_children())
        present = late = absent = 0
        for rec in records:
            s = rec.get('status', '')
            if s == 'present': present += 1
            elif s == 'late': late += 1
            else: absent += 1
            tag = s
            self.tree.insert('', 'end', values=(
                rec.get('id', ''), rec.get('student_id', ''),
                rec.get('full_name', ''), rec.get('class_name', ''),
                str(rec.get('date', '')), str(rec.get('time_in', '') or ''),
                str(rec.get('time_out', '') or ''), s.upper() if s else '',
                rec.get('marked_by', '')
            ), tags=(tag,))
        self.tree.tag_configure('present', foreground=COLORS['success'])
        self.tree.tag_configure('late', foreground=COLORS['warning'])
        self.tree.tag_configure('absent', foreground=COLORS['danger'])
        self._update_summary(len(records), present, late, absent)

    def _update_summary(self, total, present, late, absent):
        for w in self.summary_frame.winfo_children():
            w.destroy()
        cards = [
            ("Total Records", total, COLORS['info']),
            ("Present", present, COLORS['success']),
            ("Late", late, COLORS['warning']),
            ("Absent", absent, COLORS['danger']),
        ]
        for title, val, color in cards:
            c = tk.Frame(self.summary_frame, bg=COLORS['bg_card'])
            c.pack(side='left', padx=8, pady=5)
            tk.Label(c, text=str(val), font=('Segoe UI', 22, 'bold'),
                     bg=COLORS['bg_card'], fg=color).pack(padx=25, pady=(8, 2))
            tk.Label(c, text=title, font=('Segoe UI', 9),
                     bg=COLORS['bg_card'], fg=COLORS['text_muted']).pack(padx=25, pady=(0, 8))

    def load_today(self):
        self.date_var.set(str(date.today()))
        self.class_var.set('All')
        self.student_var.set('')
        self.load_report()

    def load_week(self):
        self.date_var.set('')
        week_ago = date.today() - timedelta(days=7)
        records = self.db.get_attendance()
        week_records = [r for r in records if r.get('date') and r['date'] >= week_ago]
        self.load_report(week_records)

    def load_all(self):
        self.date_var.set('')
        self.class_var.set('All')
        self.student_var.set('')
        self.load_report(self.db.get_attendance())

    def sort_column(self, col):
        pass  # Can implement sort


    def generate_pdf(self):
        try:
            from pdf_reports import PDFReportGenerator
            gen = PDFReportGenerator(self.db)
            gen.show_dialog(self.parent)
        except ImportError:
            from tkinter import messagebox
            messagebox.showerror("Missing File",
                "pdf_reports.py not found in your project folder.\n"
                "Make sure you copied all the new files.")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        if not self.records:
            messagebox.showwarning("No Data", "No records to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')],
                                             initialfile=f"attendance_{date.today()}.csv")
        if path:
            pd.DataFrame(self.records).to_csv(path, index=False)
            messagebox.showinfo("Exported", f"CSV saved to:\n{path}")

    def export_excel(self):
        if not self.records:
            messagebox.showwarning("No Data", "No records to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')],
                                             initialfile=f"attendance_{date.today()}.xlsx")
        if path:
            pd.DataFrame(self.records).to_excel(path, index=False)
            messagebox.showinfo("Exported", f"Excel saved to:\n{path}")