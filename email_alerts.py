"""
Email Alerts Module — Automated Email Notifications
====================================================
Sends beautiful HTML email alerts for:
  • Daily absent student notifications
  • Weekly attendance summary
  • Monthly PDF report attachment

SETUP (One time):
-----------------
1. Enable Gmail "App Password":
   Google Account → Security → 2-Step Verification → App Passwords
   Create an App Password for "Mail" and paste it below.

2. Fill in your Gmail address and App Password below.

3. Set ENABLED = True to send real emails.

pip install (already in requirements — uses smtplib, built-in)
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from datetime             import date, datetime

# ══════════════════════════════════════════════════════════════
#  ✏️  YOUR EMAIL CONFIG
# ══════════════════════════════════════════════════════════════
SENDER_EMAIL    = 'your_gmail@gmail.com'      # ← Your Gmail address
SENDER_PASSWORD = 'xxxx xxxx xxxx xxxx'       # ← Gmail App Password (16 chars)
SENDER_NAME     = "Vanita Vishram Attendance"

CC_EMAILS       = []   # e.g. ['principal@vvwu.ac.in', 'hod@vvwu.ac.in']
ENABLED         = False  # Set True to send real emails
# ══════════════════════════════════════════════════════════════

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT   = 587
UNIVERSITY  = "Vanita Vishram Women's University"


def _build_absent_html(student_name, student_id, class_name, date_str):
    """Build styled HTML email for absent alert."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f5f5f5;font-family:Segoe UI,Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:30px 0;">
        <tr><td align="center">
          <table width="580" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:8px;overflow:hidden;
                        box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <!-- Header -->
            <tr>
              <td style="background:#8B4513;padding:25px 30px;text-align:center;">
                <h1 style="color:#ffffff;margin:0;font-size:20px;font-weight:700;">
                  {UNIVERSITY}
                </h1>
                <p style="color:#f0d0b0;margin:5px 0 0;font-size:13px;">
                  Department of Computer Science
                </p>
              </td>
            </tr>
            <!-- Alert Banner -->
            <tr>
              <td style="background:#FFF3CD;padding:15px 30px;border-left:5px solid #F39C12;">
                <p style="margin:0;font-size:15px;font-weight:600;color:#856404;">
                  ⚠️  Attendance Alert — {date_str}
                </p>
              </td>
            </tr>
            <!-- Body -->
            <tr>
              <td style="padding:30px;">
                <p style="font-size:15px;color:#333;margin-top:0;">Dear Parent / Guardian,</p>
                <p style="font-size:14px;color:#555;line-height:1.7;">
                  This is to inform you that your ward was marked
                  <strong style="color:#E74C3C;">ABSENT</strong> today.
                </p>
                <!-- Student Info Card -->
                <table width="100%" cellpadding="0" cellspacing="0"
                       style="background:#F8F4F0;border-radius:6px;
                              border:1px solid #DDD;margin:20px 0;">
                  <tr>
                    <td style="padding:20px;">
                      <table width="100%" cellpadding="6" cellspacing="0">
                        <tr>
                          <td style="color:#888;font-size:13px;width:40%;">Student Name</td>
                          <td style="color:#333;font-size:14px;font-weight:600;">
                            {student_name}
                          </td>
                        </tr>
                        <tr style="background:#fff;border-radius:4px;">
                          <td style="color:#888;font-size:13px;">Student ID</td>
                          <td style="color:#333;font-size:14px;">{student_id}</td>
                        </tr>
                        <tr>
                          <td style="color:#888;font-size:13px;">Class</td>
                          <td style="color:#333;font-size:14px;">{class_name}</td>
                        </tr>
                        <tr style="background:#fff;">
                          <td style="color:#888;font-size:13px;">Date</td>
                          <td style="color:#E74C3C;font-size:14px;font-weight:600;">
                            {date_str}
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
                <p style="font-size:13px;color:#666;line-height:1.7;">
                  If this absence is due to a genuine reason, please contact the college
                  administration. Regular attendance is important for academic performance.
                </p>
                <p style="font-size:13px;color:#666;">
                  For queries, contact: <a href="mailto:info@vvwu.ac.in"
                  style="color:#8B4513;">info@vvwu.ac.in</a>
                </p>
              </td>
            </tr>
            <!-- Footer -->
            <tr>
              <td style="background:#8B4513;padding:15px 30px;text-align:center;">
                <p style="color:#f0d0b0;margin:0;font-size:12px;">
                  This is an automated message from the Face Recognition Attendance System.
                  Please do not reply to this email.
                </p>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """


def _build_summary_html(summary_data, report_date):
    """Build styled HTML email for daily summary."""
    total   = summary_data.get('total', 0)
    present = summary_data.get('present', 0)
    absent  = summary_data.get('absent', 0)
    late    = summary_data.get('late', 0)
    pct     = round((present + late) / total * 100, 1) if total else 0

    rows_html = ''
    for cls, data in summary_data.get('classes', {}).items():
        t = data.get('present', 0) + data.get('absent', 0) + data.get('late', 0)
        p = round((data.get('present', 0) + data.get('late', 0)) / t * 100, 1) if t else 0
        color = '#27AE60' if p >= 75 else ('#F39C12' if p >= 60 else '#E74C3C')
        rows_html += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">{cls}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;">{t}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;color:#27AE60;">
            {data.get('present',0)}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;color:#E74C3C;">
            {data.get('absent',0)}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;
                     font-weight:600;color:{color};">{p}%</td>
        </tr>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Segoe UI,Arial,sans-serif;background:#f5f5f5;padding:20px;">
      <table width="600" align="center" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:8px;overflow:hidden;">
        <tr>
          <td style="background:#8B4513;padding:22px;text-align:center;">
            <h2 style="color:#fff;margin:0;font-size:18px;">
              📊 Daily Attendance Summary
            </h2>
            <p style="color:#f0d0b0;margin:6px 0 0;font-size:13px;">
              {report_date.strftime('%A, %d %B %Y')}  |  {UNIVERSITY}
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:25px;">
            <!-- Stats row -->
            <table width="100%" cellpadding="0" cellspacing="8" style="margin-bottom:20px;">
              <tr>
                <td align="center" style="background:#EBF5FB;padding:15px;border-radius:6px;">
                  <div style="font-size:28px;font-weight:700;color:#2980B9;">{total}</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">Total</div>
                </td>
                <td align="center" style="background:#EAFAF1;padding:15px;border-radius:6px;">
                  <div style="font-size:28px;font-weight:700;color:#27AE60;">{present}</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">Present</div>
                </td>
                <td align="center" style="background:#FEF9E7;padding:15px;border-radius:6px;">
                  <div style="font-size:28px;font-weight:700;color:#F39C12;">{late}</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">Late</div>
                </td>
                <td align="center" style="background:#FDEDEC;padding:15px;border-radius:6px;">
                  <div style="font-size:28px;font-weight:700;color:#E74C3C;">{absent}</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">Absent</div>
                </td>
                <td align="center"
                    style="background:#{'EAFAF1' if pct>=75 else 'FDEDEC'};
                           padding:15px;border-radius:6px;">
                  <div style="font-size:28px;font-weight:700;
                              color:#{'27AE60' if pct>=75 else 'E74C3C'};">{pct}%</div>
                  <div style="font-size:11px;color:#888;margin-top:4px;">Rate</div>
                </td>
              </tr>
            </table>
            <!-- Class table -->
            {f'''<table width="100%" cellpadding="0" cellspacing="0"
                        style="border:1px solid #eee;border-radius:6px;overflow:hidden;
                               font-size:13px;">
              <tr style="background:#8B4513;color:#fff;">
                <th style="padding:10px 12px;text-align:left;">Class</th>
                <th style="padding:10px 12px;">Total</th>
                <th style="padding:10px 12px;">Present</th>
                <th style="padding:10px 12px;">Absent</th>
                <th style="padding:10px 12px;">Rate</th>
              </tr>
              {rows_html}
            </table>''' if rows_html else ''}
          </td>
        </tr>
        <tr>
          <td style="background:#8B4513;padding:12px;text-align:center;">
            <p style="color:#f0d0b0;margin:0;font-size:11px;">
              Automated report — Face Recognition Attendance System
            </p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def send_absent_alert(student_name, student_id, class_name, parent_email, date_str=None):
    """
    Send absent alert email to parent.
    Returns (success: bool, message: str)
    """
    if not parent_email:
        print(f"[EMAIL] No email for {student_name} — skipping")
        return False, "No email address"

    if not ENABLED:
        print(f"[EMAIL DEMO] Would send absent alert for {student_name} to {parent_email}")
        return True, "Demo mode — email not sent"

    if date_str is None:
        date_str = date.today().strftime('%d %B %Y')

    try:
        msg              = MIMEMultipart('alternative')
        msg['Subject']   = f"Attendance Alert: {student_name} was Absent on {date_str}"
        msg['From']      = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To']        = parent_email
        if CC_EMAILS:
            msg['Cc']    = ', '.join(CC_EMAILS)

        html_part = MIMEText(
            _build_absent_html(student_name, student_id, class_name, date_str),
            'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            recipients = [parent_email] + CC_EMAILS
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

        print(f"[✅ EMAIL SENT] Absent alert → {parent_email}")
        return True, f"Email sent to {parent_email}"

    except Exception as e:
        err = str(e)
        print(f"[EMAIL ERROR] {err}")
        return False, f"Email error: {err}"


def send_daily_summary(admin_emails, db, report_date=None):
    """
    Send daily attendance summary email to admin(s).
    Returns list of (email, success, message) tuples.
    """
    if report_date is None:
        report_date = date.today()

    records = db.get_attendance(date_filter=str(report_date))
    total   = len(records)
    present = sum(1 for r in records if r.get('status') == 'present')
    absent  = sum(1 for r in records if r.get('status') == 'absent')
    late    = sum(1 for r in records if r.get('status') == 'late')

    # Class breakdown
    classes = {}
    for r in records:
        cls = r.get('class_name', 'Unknown')
        if cls not in classes:
            classes[cls] = {'present': 0, 'absent': 0, 'late': 0}
        s = (r.get('status') or '').lower()
        if s in classes[cls]:
            classes[cls][s] += 1

    summary_data = {
        'total': total, 'present': present,
        'absent': absent, 'late': late, 'classes': classes
    }

    if not ENABLED:
        print(f"[EMAIL DEMO] Would send daily summary. Set ENABLED=True.")
        return [(e, True, "Demo mode") for e in admin_emails]

    results = []
    for email in admin_emails:
        try:
            msg              = MIMEMultipart('alternative')
            msg['Subject']   = (f"Daily Attendance Summary — "
                                f"{report_date.strftime('%d %b %Y')} | {UNIVERSITY}")
            msg['From']      = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg['To']        = email

            html_part = MIMEText(
                _build_summary_html(summary_data, report_date), 'html')
            msg.attach(html_part)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, [email], msg.as_string())

            print(f"[✅ EMAIL SENT] Daily summary → {email}")
            results.append((email, True, "Sent"))

        except Exception as e:
            results.append((email, False, str(e)))

    return results


def send_report_with_attachment(recipient_emails, pdf_path, report_title="Attendance Report"):
    """
    Send an email with a PDF report as attachment.
    Returns (success: bool, message: str)
    """
    if not ENABLED:
        print(f"[EMAIL DEMO] Would send '{report_title}' PDF to {recipient_emails}")
        return True, "Demo mode"

    try:
        msg            = MIMEMultipart()
        msg['Subject'] = f"{report_title} — {UNIVERSITY}"
        msg['From']    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To']      = ', '.join(recipient_emails)

        body = MIMEText(
            f"<p>Dear Admin,</p>"
            f"<p>Please find attached the <b>{report_title}</b> for {UNIVERSITY}.</p>"
            f"<p>This report was automatically generated by the "
            f"Face Recognition Attendance System.</p>",
            'html')
        msg.attach(body)

        # Attach PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename="{os.path.basename(pdf_path)}"')
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_emails, msg.as_string())

        return True, f"Email with PDF sent to {recipient_emails}"

    except Exception as e:
        return False, f"Email error: {e}"
