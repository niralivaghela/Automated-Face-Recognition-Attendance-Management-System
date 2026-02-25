"""
Database Manager - MySQL + CSV Support
Face Attendance System
"""
import mysql.connector
import csv
import os
import pandas as pd
from datetime import datetime, date, timedelta
import hashlib
import secrets


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',       # <-- Change to your MySQL password
    'database': 'face_attendance_db'
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self.csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance_csv')
        os.makedirs(self.csv_dir, exist_ok=True)

    def get_connection(self):
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error:
            cfg = {k: v for k, v in self.config.items() if k != 'database'}
            conn = mysql.connector.connect(**cfg)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            conn.commit()
            conn.close()
            return mysql.connector.connect(**self.config)

    def initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                full_name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                google_id VARCHAR(200),
                reset_token VARCHAR(100),
                reset_expiry DATETIME,
                login_method VARCHAR(20) DEFAULT 'password',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Auto-add missing columns to existing admin table
        new_cols = [
            ("phone",        "VARCHAR(20) DEFAULT NULL"),
            ("google_id",    "VARCHAR(200) DEFAULT NULL"),
            ("reset_token",  "VARCHAR(100) DEFAULT NULL"),
            ("reset_expiry", "DATETIME DEFAULT NULL"),
            ("login_method", "VARCHAR(20) DEFAULT 'password'"),
            ("role",         "VARCHAR(20) DEFAULT 'admin'"),
        ]
        for col, definition in new_cols:
            try:
                cursor.execute(f"ALTER TABLE admin ADD COLUMN {col} {definition}")
                conn.commit()
            except mysql.connector.Error:
                pass  # Column already exists

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                class_name VARCHAR(50),
                section VARCHAR(10),
                email VARCHAR(100),
                phone VARCHAR(20),
                face_encoding LONGBLOB,
                photo_path VARCHAR(255),
                status ENUM('active','inactive') DEFAULT 'active',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                full_name VARCHAR(100),
                class_name VARCHAR(50),
                date DATE NOT NULL,
                time_in TIME,
                time_out TIME,
                status ENUM('present','absent','late') DEFAULT 'present',
                marked_by VARCHAR(50) DEFAULT 'face_recognition',
                UNIQUE KEY unique_attendance (student_id, date)
            )
        """)

        # Activity log table (recreate if missing performed_by)
        cursor.execute("SHOW TABLES LIKE 'activity_log'")
        if cursor.fetchone():
            cursor.execute("SHOW COLUMNS FROM activity_log LIKE 'performed_by'")
            if not cursor.fetchone():
                cursor.execute("DROP TABLE activity_log")
                conn.commit()

        # Check and fix activity_log table columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                action VARCHAR(100),
                performed_by VARCHAR(50),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Auto-fix: add missing columns if table was created without them
        cursor.execute("SHOW COLUMNS FROM activity_log")
        existing_cols = [row[0] for row in cursor.fetchall()]
        if 'performed_by' not in existing_cols:
            cursor.execute("ALTER TABLE activity_log ADD COLUMN performed_by VARCHAR(50) AFTER action")
        if 'details' not in existing_cols:
            cursor.execute("ALTER TABLE activity_log ADD COLUMN details TEXT AFTER performed_by")
        if 'timestamp' not in existing_cols:
            cursor.execute("ALTER TABLE activity_log ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER details")

        # OTP table for phone login
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_store (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone VARCHAR(20) NOT NULL,
                otp VARCHAR(10) NOT NULL,
                expiry DATETIME NOT NULL,
                used TINYINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Student Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                exam_type VARCHAR(50) DEFAULT 'Internal',
                marks DECIMAL(6,2),
                max_marks DECIMAL(6,2) DEFAULT 100,
                grade VARCHAR(5),
                semester VARCHAR(20),
                result_date DATE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Student Fees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_fees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                fee_type VARCHAR(100) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                paid_amount DECIMAL(10,2) DEFAULT 0,
                due_date DATE,
                paid_date DATE,
                status ENUM('paid','pending','partial','overdue') DEFAULT 'pending',
                semester VARCHAR(20),
                academic_year VARCHAR(20),
                receipt_no VARCHAR(50),
                remarks TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Default admin
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO admin (username, password, full_name, email) VALUES (%s,%s,%s,%s)",
                ('admin', hash_password('admin123'), 'System Admin', 'admin@school.com')
            )

        conn.commit()
        cursor.close()
        conn.close()

    # ════════════════════════════════════════════════════════
    # ADMIN AUTH
    # ════════════════════════════════════════════════════════

    def verify_admin(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, hash_password(password))
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def verify_admin_by_email(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM admin WHERE email=%s AND password=%s",
            (email, hash_password(password))
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def verify_admin_by_phone_password(self, phone, password):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM admin WHERE phone=%s AND password=%s",
            (phone, hash_password(password))
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_admin_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_admin_by_phone(self, phone):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM admin WHERE phone=%s", (phone,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_admin_by_google_id(self, google_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM admin WHERE google_id=%s", (google_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def username_exists(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin WHERE username=%s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None

    def email_exists(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin WHERE email=%s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None

    def register_admin(self, username, password, full_name, email, phone=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO admin (username, password, full_name, email, phone, login_method)
                   VALUES (%s,%s,%s,%s,%s,'password')""",
                (username, hash_password(password), full_name,
                 email or None, phone or None)
            )
            conn.commit()
            return True, "Registration successful!"
        except mysql.connector.IntegrityError as e:
            err = str(e).lower()
            if 'username' in err:
                return False, "Username already exists!"
            elif 'email' in err:
                return False, "Email already registered!"
            elif 'phone' in err:
                return False, "Phone number already registered!"
            return False, f"Registration failed: {e}"
        finally:
            cursor.close()
            conn.close()

    # ── Forgot Password ──────────────────────────────────────

    def save_reset_token(self, email):
        token = secrets.token_hex(16)
        expiry = datetime.now() + timedelta(minutes=15)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admin SET reset_token=%s, reset_expiry=%s WHERE email=%s",
            (token, expiry, email)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return token if affected > 0 else None

    def verify_reset_token(self, token):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM admin WHERE reset_token=%s AND reset_expiry > NOW()",
            (token,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def reset_password_with_token(self, token, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE admin SET password=%s, reset_token=NULL, reset_expiry=NULL
               WHERE reset_token=%s AND reset_expiry > NOW()""",
            (hash_password(new_password), token)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return affected > 0

    def reset_password_by_email(self, email, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admin SET password=%s WHERE email=%s",
            (hash_password(new_password), email)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return affected > 0

    def change_password(self, username, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admin SET password=%s WHERE username=%s",
            (hash_password(new_password), username)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def change_password_by_email(self, email, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admin SET password=%s, reset_token=NULL, reset_expiry=NULL WHERE email=%s",
            (hash_password(new_password), email)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return affected > 0

    def update_student_photo(self, student_id, photo_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET photo_path=%s WHERE student_id=%s",
                       (photo_path, student_id))
        conn.commit()
        cursor.close()
        conn.close()

    # ── Results ──────────────────────────────────────────────

    def add_student_result(self, student_id, subject, exam_type, marks,
                            max_marks, grade, semester, result_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO student_results
               (student_id, subject, exam_type, marks, max_marks, grade, semester, result_date)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (student_id, subject, exam_type or 'Internal', marks,
             max_marks or 100, grade, semester, result_date or None)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def get_student_results(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM student_results WHERE student_id=%s ORDER BY result_date DESC",
            (student_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def delete_student_result(self, result_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_results WHERE id=%s", (result_id,))
        conn.commit()
        cursor.close()
        conn.close()

    # ── OTP for Phone Login ──────────────────────────────────

    def save_otp(self, phone, otp):
        expiry = datetime.now() + timedelta(minutes=5)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otp_store WHERE phone=%s", (phone,))
        cursor.execute(
            "INSERT INTO otp_store (phone, otp, expiry) VALUES (%s,%s,%s)",
            (phone, otp, expiry)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def verify_otp(self, phone, otp):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM otp_store WHERE phone=%s AND otp=%s AND expiry > NOW() AND used=0",
            (phone, otp)
        )
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE otp_store SET used=1 WHERE id=%s", (result['id'],))
            conn.commit()
        cursor.close()
        conn.close()
        return result is not None

    # ── Google OAuth ─────────────────────────────────────────

    def google_login_or_register(self, google_id, email, full_name):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM admin WHERE google_id=%s", (google_id,))
        admin = cursor.fetchone()
        if admin:
            cursor.close()
            conn.close()
            return admin, False

        cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
        admin = cursor.fetchone()
        if admin:
            cursor2 = conn.cursor()
            cursor2.execute("UPDATE admin SET google_id=%s WHERE email=%s", (google_id, email))
            conn.commit()
            cursor2.close()
            cursor.close()
            conn.close()
            return admin, False

        # New user
        username = email.split('@')[0]
        base = username
        suffix = 1
        cursor.execute("SELECT id FROM admin WHERE username=%s", (username,))
        while cursor.fetchone():
            username = f"{base}{suffix}"
            suffix += 1
            cursor.execute("SELECT id FROM admin WHERE username=%s", (username,))

        dummy_pass = hash_password(secrets.token_hex(16))
        cursor2 = conn.cursor()
        cursor2.execute(
            """INSERT INTO admin (username, password, full_name, email, google_id, login_method)
               VALUES (%s,%s,%s,%s,%s,'google')""",
            (username, dummy_pass, full_name, email, google_id)
        )
        conn.commit()
        cursor2.close()
        cursor.close()
        conn.close()
        return self.get_admin_by_email(email), True

    # ── General ──────────────────────────────────────────────

    def get_all_admins(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT id, username, full_name, email, phone, login_method, created_at FROM admin")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_admin_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def update_admin_profile(self, username, full_name, email, phone=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admin SET full_name=%s, email=%s, phone=%s WHERE username=%s",
            (full_name, email or None, phone or None, username)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def add_admin(self, username, password, full_name, email, phone=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin (username, password, full_name, email, phone) VALUES (%s,%s,%s,%s,%s)",
            (username, hash_password(password), full_name, email, phone or None)
        )
        conn.commit()
        cursor.close()
        conn.close()

    # ════════════════════════════════════════════════════════
    # STUDENTS
    # ════════════════════════════════════════════════════════

    def add_student(self, student_id, full_name, class_name, section, email, phone, face_encoding, photo_path):
        import pickle
        conn = self.get_connection()
        cursor = conn.cursor()
        enc_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
        cursor.execute(
            """INSERT INTO students (student_id, full_name, class_name, section, email, phone, face_encoding, photo_path)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (student_id, full_name, class_name, section, email, phone, enc_blob, photo_path)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def update_student(self, student_id, full_name, class_name, section, email, phone):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET full_name=%s, class_name=%s, section=%s, email=%s, phone=%s WHERE student_id=%s",
            (full_name, class_name, section, email, phone, student_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def update_student_face(self, student_id, face_encoding, photo_path):
        import pickle
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET face_encoding=%s, photo_path=%s WHERE student_id=%s",
            (pickle.dumps(face_encoding), photo_path, student_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
        cursor.execute("DELETE FROM attendance WHERE student_id=%s", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_students(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT student_id, full_name, class_name, section, email, phone, status, registered_at FROM students")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_student_by_id(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_all_face_encodings(self):
        """Returns list of (student_id, full_name, class_name, numpy_array)"""
        import pickle
        import numpy as np
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id, full_name, class_name, face_encoding "
            "FROM students WHERE status='active' AND face_encoding IS NOT NULL"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        result = []
        for row in rows:
            try:
                raw = pickle.loads(row[3])
                enc = np.array(raw, dtype=np.float32)
                result.append((row[0], row[1], row[2], enc))
            except Exception:
                pass
        return result

    def toggle_student_status(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET status = IF(status='active','inactive','active') WHERE student_id=%s", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()

    # ════════════════════════════════════════════════════════
    # ATTENDANCE
    # ════════════════════════════════════════════════════════

    def mark_attendance(self, student_id, full_name, class_name, status='present'):
        today = date.today()
        now = datetime.now().strftime('%H:%M:%S')
        if status == 'present' and now > '09:00:00':
            status = 'late'
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO attendance (student_id, full_name, class_name, date, time_in, status)
                   VALUES (%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE time_out=%s""",
                (student_id, full_name, class_name, today, now, status, now)
            )
            conn.commit()
            self._append_to_csv(student_id, full_name, class_name, today, now, status)
            return True
        except:
            return False
        finally:
            cursor.close()
            conn.close()

    def _append_to_csv(self, student_id, full_name, class_name, att_date, time_in, status):
        csv_file = os.path.join(self.csv_dir, f"attendance_{att_date}.csv")
        file_exists = os.path.exists(csv_file)
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Student ID', 'Full Name', 'Class', 'Date', 'Time In', 'Status'])
            writer.writerow([student_id, full_name, class_name, att_date, time_in, status])

    def get_attendance(self, filter_date=None, filter_class=None, filter_student=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = "SELECT * FROM attendance WHERE 1=1"
        params = []
        if filter_date:
            query += " AND date=%s"
            params.append(filter_date)
        if filter_class:
            query += " AND class_name=%s"
            params.append(filter_class)
        if filter_student:
            query += " AND (student_id=%s OR full_name LIKE %s)"
            params.extend([filter_student, f'%{filter_student}%'])
        query += " ORDER BY date DESC, time_in DESC"
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_today_attendance(self):
        return self.get_attendance(filter_date=date.today())

    def get_attendance_stats(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            today = date.today()
            cursor.execute("SELECT COUNT(*) as total FROM students WHERE status='active'")
            total = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) as present FROM attendance WHERE date=%s AND status IN ('present','late')", (today,))
            present = cursor.fetchone()['present']
            cursor.execute("SELECT COUNT(*) as late FROM attendance WHERE date=%s AND status='late'", (today,))
            late = cursor.fetchone()['late']
            cursor.close()
            conn.close()
            return {'total_students': total, 'present_today': present,
                    'absent_today': total - present, 'late_today': late}
        except Exception:
            raise

    def export_attendance_csv(self, filepath, filter_date=None, filter_class=None):
        records = self.get_attendance(filter_date=filter_date, filter_class=filter_class)
        if not records:
            return False
        pd.DataFrame(records).to_csv(filepath, index=False)
        return True

    def export_attendance_excel(self, filepath, filter_date=None, filter_class=None):
        records = self.get_attendance(filter_date=filter_date, filter_class=filter_class)
        if not records:
            return False
        pd.DataFrame(records).to_excel(filepath, index=False)
        return True

    # ════════════════════════════════════════════════════════
    # ACTIVITY LOG
    # ════════════════════════════════════════════════════════

    def log_activity(self, action, performed_by, details=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_log (action, performed_by, details) VALUES (%s,%s,%s)",
            (action, performed_by, details)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def get_activity_log(self, limit=100):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT %s", (limit,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_classes(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT class_name FROM students WHERE class_name IS NOT NULL ORDER BY class_name")
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result

    # ════════════════════════════════════════════════════════
    # ROLE-BASED USER SYSTEM
    # ════════════════════════════════════════════════════════

    def verify_user_by_role(self, username, password, role):
        """Verify login for admin/teacher — role stored in admin table."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s AND role=%s",
            (username, hash_password(password), role)
        )
        result = cursor.fetchone()
        if not result:
            # also try email login
            cursor.execute(
                "SELECT * FROM admin WHERE email=%s AND password=%s AND role=%s",
                (username, hash_password(password), role)
            )
            result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def verify_student_login(self, student_id, password):
        """
        Student logs in with their Student ID and phone number as password.
        Password = student's phone number saved in DB.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM students WHERE student_id=%s AND phone=%s AND status='active'",
            (student_id, password)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def add_teacher(self, username, password, full_name, email, phone=''):
        """Register a teacher account (role='teacher' in admin table)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO admin (username, password, full_name, email, phone, login_method, role)
                   VALUES (%s,%s,%s,%s,%s,'password','teacher')""",
                (username, hash_password(password), full_name, email or None, phone or None)
            )
            conn.commit()
            return True, "Teacher registered successfully!"
        except mysql.connector.IntegrityError as e:
            err = str(e).lower()
            if 'username' in err:
                return False, "Username already exists!"
            elif 'email' in err:
                return False, "Email already registered!"
            return False, f"Registration failed: {e}"
        finally:
            cursor.close()
            conn.close()

    def get_all_teachers(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT id, username, full_name, email, phone, created_at FROM admin WHERE role='teacher'"
        )
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def get_student_attendance_summary(self, student_id):
        """Get attendance summary stats for a student."""
        records = self.get_attendance(filter_student=student_id)
        total   = len(records)
        present = sum(1 for r in records if r.get('status') in ('present', 'late'))
        absent  = total - present
        pct     = round(present / total * 100, 1) if total else 0.0
        return {
            'records': records,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': pct
        }

    def get_weekly_attendance(self, student_id):
        """Get last 7 days attendance for a student."""
        from datetime import date, timedelta
        records = self.get_attendance(filter_student=student_id)
        today   = date.today()
        week_ago = today - timedelta(days=6)
        weekly  = [r for r in records
                   if r.get('date') and r['date'] >= week_ago]
        return sorted(weekly, key=lambda x: x.get('date', date.min))
    def get_monthly_attendance(self, student_id, year=None, month=None):
        """Get attendance for a specific month for a student."""
        import calendar
        from datetime import date
        today = date.today()
        year  = year  or today.year
        month = month or today.month
        records = self.get_attendance(filter_student=student_id)
        monthly = [r for r in records
                   if r.get('date') and
                   r['date'].year == year and r['date'].month == month]
        return sorted(monthly, key=lambda x: x.get('date', date.min))

    # ════════════════════════════════════════════════════════
    # FEES
    # ════════════════════════════════════════════════════════

    def add_fee(self, student_id, fee_type, amount, due_date, semester='',
                academic_year='', receipt_no='', remarks='',
                paid_amount=0, paid_date=None, status='pending'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO student_fees
               (student_id, fee_type, amount, paid_amount, due_date, paid_date,
                status, semester, academic_year, receipt_no, remarks)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (student_id, fee_type, amount, paid_amount or 0,
             due_date or None, paid_date or None,
             status, semester, academic_year, receipt_no, remarks)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def get_student_fees(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM student_fees WHERE student_id=%s ORDER BY due_date DESC",
            (student_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def update_fee_payment(self, fee_id, paid_amount, paid_date, status, receipt_no=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE student_fees
               SET paid_amount=%s, paid_date=%s, status=%s, receipt_no=%s
               WHERE id=%s""",
            (paid_amount, paid_date or None, status, receipt_no, fee_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def delete_fee(self, fee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_fees WHERE id=%s", (fee_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def get_fees_summary(self, student_id):
        fees = self.get_student_fees(student_id)
        total_amount = sum(float(f.get('amount') or 0) for f in fees)
        total_paid   = sum(float(f.get('paid_amount') or 0) for f in fees)
        total_due    = total_amount - total_paid
        paid_count   = sum(1 for f in fees if f.get('status') == 'paid')
        pending      = sum(1 for f in fees if f.get('status') in ('pending','overdue','partial'))
        return {
            'fees': fees,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'paid_count': paid_count,
            'pending_count': pending,
        }