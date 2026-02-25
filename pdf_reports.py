"""
PDF Reports Module — Professional PDF Generation
=================================================
Generates college-grade attendance PDFs with:
  • Monthly Attendance Register
  • Daily Attendance Report
  • Student Individual Report
  • Defaulter List (below 75%)
  • Class Summary Report

Dependencies: pip install reportlab
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

# ── Brand Colors (matching Vanita Vishram theme) ────────────────────────────
BROWN       = colors.HexColor('#8B4513')
DARK_BROWN  = colors.HexColor('#654321')
CREAM       = colors.HexColor('#FFF8F0')
LIGHT_CREAM = colors.HexColor('#FDFAF7')
GOLD        = colors.HexColor('#C8860A')
GREEN       = colors.HexColor('#27AE60')
RED         = colors.HexColor('#E74C3C')
ORANGE      = colors.HexColor('#F39C12')
BLUE        = colors.HexColor('#2980B9')
GREY        = colors.HexColor('#666666')
LIGHT_GREY  = colors.HexColor('#F5F5F5')
WHITE       = colors.white
BLACK       = colors.black

UNIVERSITY  = "Vanita Vishram Women's University"
DEPARTMENT  = "Department of Computer Science"
SYSTEM_NAME = "Face Recognition Attendance System"


# ═══════════════════════════════════════════════════════════════════
#  Helper: Header / Footer builders
# ═══════════════════════════════════════════════════════════════════

def _header_footer(canvas, doc, report_title="Attendance Report"):
    """Draw page header and footer on every page."""
    canvas.saveState()
    w, h = doc.pagesize

    # ── Header bar ────────────────────────────────────────────
    canvas.setFillColor(BROWN)
    canvas.rect(0, h - 2.8*cm, w, 2.8*cm, fill=1, stroke=0)

    # University name
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(w / 2, h - 1.1*cm, UNIVERSITY)

    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(w / 2, h - 1.7*cm,
                             f"{DEPARTMENT}  |  {SYSTEM_NAME}")

    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(w / 2, h - 2.3*cm, report_title)

    # Gold accent line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(0, h - 2.9*cm, w, h - 2.9*cm)

    # ── Footer ────────────────────────────────────────────────
    canvas.setFillColor(BROWN)
    canvas.rect(0, 0, w, 1.1*cm, fill=1, stroke=0)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1*cm, 0.35*cm,
                      f"Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}")
    canvas.drawCentredString(w / 2, 0.35*cm, UNIVERSITY)
    canvas.drawRightString(w - 1*cm, 0.35*cm,
                           f"Page {canvas.getPageNumber()}")

    canvas.restoreState()


def _make_doc(path, title, landscape_mode=False):
    """Create a SimpleDocTemplate with common margins."""
    ps = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(
        path,
        pagesize=ps,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=3.5*cm,  bottomMargin=1.8*cm,
        title=title,
        author=UNIVERSITY,
        subject=SYSTEM_NAME,
    )
    return doc


def _styles():
    s = getSampleStyleSheet()
    base = dict(fontName='Helvetica', spaceAfter=4)

    s.add(ParagraphStyle('SectionTitle',
          fontName='Helvetica-Bold', fontSize=12, textColor=BROWN,
          spaceAfter=6, spaceBefore=10))

    s.add(ParagraphStyle('SubTitle',
          fontName='Helvetica-Bold', fontSize=10, textColor=DARK_BROWN,
          spaceAfter=4, spaceBefore=6))

    s.add(ParagraphStyle('BodySmall',
          fontName='Helvetica', fontSize=9, textColor=BLACK,
          spaceAfter=3))

    s.add(ParagraphStyle('CenterSmall',
          fontName='Helvetica', fontSize=9, textColor=BLACK,
          alignment=TA_CENTER, spaceAfter=3))

    s.add(ParagraphStyle('MetaInfo',
          fontName='Helvetica', fontSize=8, textColor=GREY,
          spaceAfter=2))

    s.add(ParagraphStyle('StatLabel',
          fontName='Helvetica-Bold', fontSize=22, textColor=BROWN,
          alignment=TA_CENTER, spaceAfter=0))

    s.add(ParagraphStyle('StatSub',
          fontName='Helvetica', fontSize=8, textColor=GREY,
          alignment=TA_CENTER, spaceAfter=0))
    return s


# ═══════════════════════════════════════════════════════════════════
#  1. DAILY ATTENDANCE REPORT
# ═══════════════════════════════════════════════════════════════════

def generate_daily_report(db, output_path, report_date=None, class_filter=None):
    """Generate a daily attendance PDF report."""

    if report_date is None:
        report_date = date.today()

    date_str  = str(report_date)
    title     = f"Daily Attendance Report — {report_date.strftime('%d %B %Y')}"
    records   = db.get_attendance(date_filter=date_str, class_filter=class_filter)

    doc   = _make_doc(output_path, title)
    story = []
    S     = _styles()

    # ── Summary bar ──────────────────────────────────────────
    total   = len(records)
    present = sum(1 for r in records if r.get('status') == 'present')
    late    = sum(1 for r in records if r.get('status') == 'late')
    absent  = sum(1 for r in records if r.get('status') == 'absent')
    pct     = round((present + late) / total * 100, 1) if total else 0

    story.append(Paragraph(f"Date: <b>{report_date.strftime('%A, %d %B %Y')}</b>" +
                           (f"   |   Class: <b>{class_filter}</b>" if class_filter else ""),
                           S['BodySmall']))
    story.append(Spacer(1, 6))

    # Stat cards as a table row
    stat_data = [
        [Paragraph(str(total),   S['StatLabel']),
         Paragraph(str(present), S['StatLabel']),
         Paragraph(str(late),    S['StatLabel']),
         Paragraph(str(absent),  S['StatLabel']),
         Paragraph(f"{pct}%",    S['StatLabel'])],
        [Paragraph("Total",   S['StatSub']),
         Paragraph("Present", S['StatSub']),
         Paragraph("Late",    S['StatSub']),
         Paragraph("Absent",  S['StatSub']),
         Paragraph("Rate",    S['StatSub'])],
    ]
    stat_table = Table(stat_data, colWidths=[3.5*cm]*5)
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CREAM),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#EAF9EE')),
        ('BACKGROUND', (3,0), (3,-1), colors.HexColor('#FDEEEE')),
        ('BOX',        (0,0), (-1,-1), 1, BROWN),
        ('INNERGRID',  (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 14))

    # ── Attendance table ──────────────────────────────────────
    story.append(Paragraph("Attendance Records", S['SectionTitle']))

    headers = ['#', 'Student ID', 'Full Name', 'Class', 'Time In', 'Time Out', 'Status', 'Marked By']
    rows    = [headers]
    for i, r in enumerate(records, 1):
        status = (r.get('status') or '').upper()
        rows.append([
            str(i),
            str(r.get('student_id', '')),
            str(r.get('full_name', '')),
            str(r.get('class_name', '')),
            str(r.get('time_in', '') or '—'),
            str(r.get('time_out', '') or '—'),
            status,
            str(r.get('marked_by', '') or 'System'),
        ])

    col_w = [0.8*cm, 2.2*cm, 4.5*cm, 2.5*cm, 2.2*cm, 2.2*cm, 1.8*cm, 2.8*cm]
    tbl   = Table(rows, colWidths=col_w, repeatRows=1)

    ts = TableStyle([
        # Header
        ('BACKGROUND',    (0,0), (-1,0),  BROWN),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  9),
        ('ALIGN',         (0,0), (-1,0),  'CENTER'),
        # Body
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('ALIGN',         (0,1), (1,-1),  'CENTER'),
        ('ALIGN',         (2,1), (2,-1),  'LEFT'),
        ('ALIGN',         (4,1), (6,-1),  'CENTER'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_CREAM]),
        ('GRID',          (0,0), (-1,-1), 0.4, LIGHT_GREY),
        ('BOX',           (0,0), (-1,-1), 1,   BROWN),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 4),
    ])
    # Colour status column
    for row_idx, r in enumerate(records, 1):
        s = (r.get('status') or '').lower()
        if s == 'present':
            ts.add('TEXTCOLOR', (6, row_idx), (6, row_idx), GREEN)
        elif s == 'late':
            ts.add('TEXTCOLOR', (6, row_idx), (6, row_idx), ORANGE)
        elif s == 'absent':
            ts.add('TEXTCOLOR', (6, row_idx), (6, row_idx), RED)
    tbl.setStyle(ts)
    story.append(tbl)

    if not records:
        story.append(Paragraph("No attendance records found for this date.", S['CenterSmall']))

    # Build
    doc.build(story,
              onFirstPage=lambda c, d: _header_footer(c, d, title),
              onLaterPages=lambda c, d: _header_footer(c, d, title))
    return output_path


# ═══════════════════════════════════════════════════════════════════
#  2. MONTHLY ATTENDANCE REGISTER
# ═══════════════════════════════════════════════════════════════════

def generate_monthly_register(db, output_path, year=None, month=None, class_filter=None):
    """Generate a monthly register in landscape format."""
    import calendar

    today = date.today()
    year  = year  or today.year
    month = month or today.month

    month_name = calendar.month_name[month]
    title      = f"Monthly Attendance Register — {month_name} {year}"
    if class_filter:
        title += f"  |  {class_filter}"

    # Days in month
    num_days = calendar.monthrange(year, month)[1]
    day_range = list(range(1, num_days + 1))

    # Fetch all records for month
    all_records = db.get_attendance()
    month_recs  = [r for r in all_records
                   if r.get('date') and
                   r['date'].year == year and r['date'].month == month]

    if class_filter and class_filter != 'All':
        month_recs = [r for r in month_recs if r.get('class_name') == class_filter]

    # Build student × day grid
    students = {}
    for r in month_recs:
        sid  = r.get('student_id', '')
        name = r.get('full_name', '')
        cls  = r.get('class_name', '')
        if sid not in students:
            students[sid] = {'name': name, 'class': cls, 'days': {}}
        d = r['date'].day if r.get('date') else None
        if d:
            students[sid]['days'][d] = (r.get('status') or 'absent')[0].upper()

    doc   = _make_doc(output_path, title, landscape_mode=True)
    story = []
    S     = _styles()

    story.append(Paragraph(
        f"Month: <b>{month_name} {year}</b>" +
        (f"   |   Class: <b>{class_filter}</b>" if class_filter else ""),
        S['BodySmall']))
    story.append(Spacer(1, 8))

    # Header row: Sr | Student ID | Name | Class | 1..31 | P | A | L | %
    hdr_fixed = ['Sr', 'Std ID', 'Full Name', 'Class']
    hdr_days  = [str(d) for d in day_range]
    hdr_stats = ['P', 'A', 'L', '%']
    header    = hdr_fixed + hdr_days + hdr_stats

    rows = [header]
    for i, (sid, info) in enumerate(sorted(students.items()), 1):
        p = sum(1 for v in info['days'].values() if v == 'P')
        a = sum(1 for v in info['days'].values() if v == 'A')
        l = sum(1 for v in info['days'].values() if v == 'L')
        pct = round((p + l) / num_days * 100, 0) if num_days else 0

        day_cells = [info['days'].get(d, '-') for d in day_range]
        row = [str(i), sid, info['name'], info['class']] + day_cells + \
              [str(p), str(a), str(l), f"{pct:.0f}%"]
        rows.append(row)

    # Column widths
    fixed_w = [0.7*cm, 1.8*cm, 4.0*cm, 2.0*cm]
    day_w   = [0.55*cm] * num_days
    stat_w  = [0.7*cm, 0.7*cm, 0.7*cm, 1.0*cm]
    col_w   = fixed_w + day_w + stat_w

    tbl = Table(rows, colWidths=col_w, repeatRows=1)
    ts  = TableStyle([
        ('BACKGROUND', (0,0), (-1,0),  BROWN),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 6.5),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (2,1), (2,-1),  'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_CREAM]),
        ('GRID',       (0,0), (-1,-1), 0.3, LIGHT_GREY),
        ('BOX',        (0,0), (-1,-1), 1,   BROWN),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ])
    # Highlight summary cols
    n = len(fixed_w) + num_days
    ts.add('BACKGROUND', (n, 0),   (-1, 0),   GOLD)
    ts.add('BACKGROUND', (n, 1),   (-1, -1),  colors.HexColor('#FFF5E0'))
    ts.add('FONTNAME',   (n, 1),   (-1, -1),  'Helvetica-Bold')
    tbl.setStyle(ts)

    story.append(tbl)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Legend:  P = Present   A = Absent   L = Late   - = No Record",
        S['MetaInfo']))

    doc.build(story,
              onFirstPage=lambda c, d: _header_footer(c, d, title),
              onLaterPages=lambda c, d: _header_footer(c, d, title))
    return output_path


# ═══════════════════════════════════════════════════════════════════
#  3. DEFAULTER LIST  (below 75 %)
# ═══════════════════════════════════════════════════════════════════

def generate_defaulter_list(db, output_path, threshold=75):
    """Generate list of students with attendance below threshold%."""

    title   = f"Attendance Defaulter List  (Below {threshold}%)"
    records = db.get_attendance()

    # Aggregate per student
    students = {}
    for r in records:
        sid  = r.get('student_id', '')
        if not sid:
            continue
        if sid not in students:
            students[sid] = {
                'name': r.get('full_name', ''),
                'class': r.get('class_name', ''),
                'total': 0, 'present': 0, 'late': 0, 'absent': 0
            }
        students[sid]['total'] += 1
        s = (r.get('status') or '').lower()
        if s == 'present': students[sid]['present'] += 1
        elif s == 'late':  students[sid]['late']    += 1
        else:              students[sid]['absent']   += 1

    defaulters = []
    for sid, info in students.items():
        pct = (info['present'] + info['late']) / info['total'] * 100 if info['total'] else 0
        if pct < threshold:
            defaulters.append({**info, 'student_id': sid, 'pct': round(pct, 1)})
    defaulters.sort(key=lambda x: x['pct'])

    doc   = _make_doc(output_path, title)
    story = []
    S     = _styles()

    story.append(Paragraph(
        f"Students with attendance below <b>{threshold}%</b>  |  "
        f"Generated: {date.today().strftime('%d %B %Y')}",
        S['BodySmall']))
    story.append(Spacer(1, 4))

    # Warning banner
    warn_data = [[Paragraph(
        f"⚠  <b>{len(defaulters)} student(s)</b> are below the required {threshold}% attendance. "
        "Immediate action recommended.",
        ParagraphStyle('Warn', fontName='Helvetica-Bold', fontSize=10,
                       textColor=colors.HexColor('#7B3F00')))]]
    warn_tbl = Table(warn_data, colWidths=[17*cm])
    warn_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3CD')),
        ('BOX',        (0,0), (-1,-1), 1.5, ORANGE),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ]))
    story.append(warn_tbl)
    story.append(Spacer(1, 12))

    headers = ['#', 'Student ID', 'Full Name', 'Class',
               'Total Days', 'Present', 'Late', 'Absent', 'Attendance %', 'Shortfall']
    rows    = [headers]
    for i, d in enumerate(defaulters, 1):
        shortfall = max(0, round(threshold - d['pct'], 1))
        rows.append([
            str(i), d['student_id'], d['name'], d['class'],
            str(d['total']), str(d['present']), str(d['late']), str(d['absent']),
            f"{d['pct']}%", f"{shortfall}%"
        ])

    col_w = [0.7*cm, 2.2*cm, 4.2*cm, 2.2*cm, 2*cm, 1.8*cm, 1.5*cm, 1.8*cm, 2.4*cm, 2*cm]
    tbl   = Table(rows, colWidths=col_w, repeatRows=1)
    ts    = TableStyle([
        ('BACKGROUND', (0,0), (-1,0),  colors.HexColor('#8B0000')),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (2,1), (2,-1),  'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, colors.HexColor('#FFF5F5')]),
        ('GRID',       (0,0), (-1,-1), 0.4, LIGHT_GREY),
        ('BOX',        (0,0), (-1,-1), 1, colors.HexColor('#8B0000')),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ])
    # Red % column
    for row_idx in range(1, len(defaulters)+1):
        ts.add('TEXTCOLOR', (8, row_idx), (8, row_idx), RED)
        ts.add('FONTNAME',  (8, row_idx), (8, row_idx), 'Helvetica-Bold')
    tbl.setStyle(ts)
    story.append(tbl)

    if not defaulters:
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "✅  No defaulters found. All students have attendance above threshold.",
            ParagraphStyle('Good', fontName='Helvetica-Bold', fontSize=11,
                           textColor=GREEN, alignment=TA_CENTER)))

    doc.build(story,
              onFirstPage=lambda c, d: _header_footer(c, d, title),
              onLaterPages=lambda c, d: _header_footer(c, d, title))
    return output_path


# ═══════════════════════════════════════════════════════════════════
#  4. CLASS SUMMARY REPORT
# ═══════════════════════════════════════════════════════════════════

def generate_class_summary(db, output_path, report_date=None):
    """Generate a class-wise attendance summary PDF."""

    if report_date is None:
        report_date = date.today()

    title   = f"Class-Wise Attendance Summary — {report_date.strftime('%d %B %Y')}"
    records = db.get_attendance(date_filter=str(report_date))

    # Group by class
    classes = {}
    for r in records:
        cls = r.get('class_name', 'Unknown')
        if cls not in classes:
            classes[cls] = {'present': 0, 'absent': 0, 'late': 0}
        s = (r.get('status') or '').lower()
        classes[cls][s if s in ('present','absent','late') else 'absent'] += 1

    doc   = _make_doc(output_path, title)
    story = []
    S     = _styles()

    story.append(Paragraph(
        f"Date: <b>{report_date.strftime('%A, %d %B %Y')}</b>  |  "
        f"Classes: <b>{len(classes)}</b>",
        S['BodySmall']))
    story.append(Spacer(1, 10))

    headers = ['#', 'Class', 'Total Students', 'Present', 'Late', 'Absent', 'Attendance %']
    rows    = [headers]
    grand   = {'total': 0, 'present': 0, 'late': 0, 'absent': 0}

    for i, (cls, data) in enumerate(sorted(classes.items()), 1):
        total = data['present'] + data['absent'] + data['late']
        pct   = round((data['present'] + data['late']) / total * 100, 1) if total else 0
        rows.append([str(i), cls, str(total),
                     str(data['present']), str(data['late']), str(data['absent']),
                     f"{pct}%"])
        for k in grand:
            grand[k] += data.get(k, 0) if k != 'total' else total

    # Grand total row
    grand_pct = round((grand['present'] + grand['late']) / grand['total'] * 100, 1) \
                if grand['total'] else 0
    rows.append(['', 'TOTAL', str(grand['total']),
                 str(grand['present']), str(grand['late']), str(grand['absent']),
                 f"{grand_pct}%"])

    col_w = [0.8*cm, 4*cm, 3.2*cm, 2.5*cm, 2*cm, 2*cm, 3*cm]
    tbl   = Table(rows, colWidths=col_w, repeatRows=1)
    ts    = TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  BROWN),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',       (1,1), (1,-1),  'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [WHITE, LIGHT_CREAM]),
        ('BACKGROUND',  (0,-1), (-1,-1), colors.HexColor('#FFF3CD')),
        ('FONTNAME',    (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID',        (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('BOX',         (0,0), (-1,-1), 1.5, BROWN),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ])
    # Colour attendance %
    for row_idx in range(1, len(classes)+1):
        pct_val = float(rows[row_idx][6].replace('%','')) if rows[row_idx][6] else 0
        color   = GREEN if pct_val >= 75 else (ORANGE if pct_val >= 60 else RED)
        ts.add('TEXTCOLOR', (6, row_idx), (6, row_idx), color)
        ts.add('FONTNAME',  (6, row_idx), (6, row_idx), 'Helvetica-Bold')
    tbl.setStyle(ts)
    story.append(tbl)

    doc.build(story,
              onFirstPage=lambda c, d: _header_footer(c, d, title),
              onLaterPages=lambda c, d: _header_footer(c, d, title))
    return output_path


# ═══════════════════════════════════════════════════════════════════
#  5. STUDENT INDIVIDUAL REPORT
# ═══════════════════════════════════════════════════════════════════

def generate_student_report(db, output_path, student_id):
    """Generate individual attendance report for a single student."""

    records = db.get_attendance(student_filter=student_id)
    if not records:
        raise ValueError(f"No attendance records found for student ID: {student_id}")

    student_name = records[0].get('full_name', student_id)
    class_name   = records[0].get('class_name', '')
    title        = f"Student Attendance Report — {student_name}"

    doc   = _make_doc(output_path, title)
    story = []
    S     = _styles()

    # Student info box
    total   = len(records)
    present = sum(1 for r in records if r.get('status') == 'present')
    late    = sum(1 for r in records if r.get('status') == 'late')
    absent  = sum(1 for r in records if r.get('status') == 'absent')
    pct     = round((present + late) / total * 100, 1) if total else 0

    info_data = [
        [Paragraph('<b>Student Name:</b>',   S['BodySmall']),
         Paragraph(student_name,             S['BodySmall']),
         Paragraph('<b>Student ID:</b>',     S['BodySmall']),
         Paragraph(str(student_id),          S['BodySmall'])],
        [Paragraph('<b>Class:</b>',          S['BodySmall']),
         Paragraph(class_name,              S['BodySmall']),
         Paragraph('<b>Report Date:</b>',    S['BodySmall']),
         Paragraph(date.today().strftime('%d %B %Y'), S['BodySmall'])],
    ]
    info_tbl = Table(info_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    info_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CREAM),
        ('BOX',        (0,0), (-1,-1), 1, BROWN),
        ('INNERGRID',  (0,0), (-1,-1), 0.3, LIGHT_GREY),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 10))

    # Stats row
    status_color = GREEN if pct >= 75 else (ORANGE if pct >= 60 else RED)
    stat_data = [
        [Paragraph(str(total),   S['StatLabel']),
         Paragraph(str(present), S['StatLabel']),
         Paragraph(str(late),    S['StatLabel']),
         Paragraph(str(absent),  S['StatLabel']),
         Paragraph(f"{pct}%",
                   ParagraphStyle('PctStat', fontName='Helvetica-Bold',
                                  fontSize=22, textColor=status_color,
                                  alignment=TA_CENTER))],
        [Paragraph("Total Days",  S['StatSub']),
         Paragraph("Present",     S['StatSub']),
         Paragraph("Late",        S['StatSub']),
         Paragraph("Absent",      S['StatSub']),
         Paragraph("Attendance",  S['StatSub'])],
    ]
    stat_tbl = Table(stat_data, colWidths=[3.5*cm]*5)
    stat_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F4FF')),
        ('BOX',        (0,0), (-1,-1), 1, BROWN),
        ('INNERGRID',  (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(stat_tbl)
    story.append(Spacer(1, 12))

    # Attendance %  threshold note
    note_color = GREEN if pct >= 75 else RED
    note_text  = (f"✅  Attendance is above 75% requirement."
                  if pct >= 75
                  else f"⚠  Attendance is BELOW 75% requirement! Student needs {round(75 - pct, 1)}% more.")
    story.append(Paragraph(note_text,
                            ParagraphStyle('Note', fontName='Helvetica-Bold', fontSize=10,
                                           textColor=note_color)))
    story.append(Spacer(1, 10))

    # Detailed records
    story.append(Paragraph("Attendance Details", S['SectionTitle']))

    headers = ['#', 'Date', 'Day', 'Time In', 'Time Out', 'Status', 'Marked By']
    rows    = [headers]
    for i, r in enumerate(sorted(records, key=lambda x: x.get('date', date.min)), 1):
        d   = r.get('date')
        day = d.strftime('%A') if d else ''
        rows.append([
            str(i),
            str(d) if d else '',
            day,
            str(r.get('time_in',  '') or '—'),
            str(r.get('time_out', '') or '—'),
            (r.get('status') or '').upper(),
            str(r.get('marked_by', '') or 'System'),
        ])

    col_w = [0.8*cm, 2.5*cm, 2.5*cm, 2.2*cm, 2.2*cm, 2*cm, 3*cm]
    tbl   = Table(rows, colWidths=col_w, repeatRows=1)
    ts    = TableStyle([
        ('BACKGROUND', (0,0), (-1,0),  BROWN),
        ('TEXTCOLOR',  (0,0), (-1,0),  WHITE),
        ('FONTNAME',   (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_CREAM]),
        ('GRID',       (0,0), (-1,-1), 0.4, LIGHT_GREY),
        ('BOX',        (0,0), (-1,-1), 1,   BROWN),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ])
    for row_idx, r in enumerate(records, 1):
        s = (r.get('status') or '').lower()
        if s == 'present': ts.add('TEXTCOLOR', (5, row_idx), (5, row_idx), GREEN)
        elif s == 'late':  ts.add('TEXTCOLOR', (5, row_idx), (5, row_idx), ORANGE)
        else:              ts.add('TEXTCOLOR', (5, row_idx), (5, row_idx), RED)
    tbl.setStyle(ts)
    story.append(tbl)

    doc.build(story,
              onFirstPage=lambda c, d: _header_footer(c, d, title),
              onLaterPages=lambda c, d: _header_footer(c, d, title))
    return output_path


# ═══════════════════════════════════════════════════════════════════
#  GUI DIALOG — Launched from Reports page
# ═══════════════════════════════════════════════════════════════════

class PDFReportGenerator:
    """GUI dialog for selecting and generating PDF reports."""

    COLORS = {
        'bg': '#f5f5f0', 'card': '#ffffff', 'sidebar': '#8B4513',
        'accent': '#654321', 'text': '#333333', 'muted': '#666666',
    }

    def __init__(self, db):
        self.db = db

    def show_dialog(self, parent):
        win = tk.Toplevel(parent)
        win.title("Generate PDF Report")
        win.geometry("500x540")
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, False)
        win.grab_set()

        C = self.COLORS

        # Title bar
        tk.Frame(win, bg=C['sidebar'], height=55).pack(fill='x')
        tk.Label(win, text="📄  Generate PDF Report",
                 font=('Segoe UI', 14, 'bold'),
                 bg=C['sidebar'], fg='white').place(x=20, y=15)

        body = tk.Frame(win, bg=C['bg'])
        body.pack(fill='both', expand=True, pady=(10, 0), padx=15)

        # Report type
        tk.Label(body, text="Report Type", font=('Segoe UI', 10, 'bold'),
                 bg=C['bg'], fg=C['text']).pack(anchor='w', pady=(8, 2))

        self.report_type = tk.StringVar(value='daily')
        types = [
            ("📅  Daily Attendance Report",    'daily'),
            ("📆  Monthly Attendance Register",'monthly'),
            ("⚠️   Defaulter List (< 75%)",    'defaulter'),
            ("🏫  Class-Wise Summary",         'class_summary'),
            ("👤  Student Individual Report",  'student'),
        ]
        for label, val in types:
            tk.Radiobutton(body, text=label, variable=self.report_type,
                           value=val, bg=C['bg'], fg=C['text'],
                           font=('Segoe UI', 10),
                           activebackground=C['bg'],
                           command=self._toggle_fields).pack(anchor='w', padx=10)

        sep = tk.Frame(body, bg=C['sidebar'], height=1)
        sep.pack(fill='x', pady=10)

        # Dynamic fields frame
        self.fields_frame = tk.Frame(body, bg=C['bg'])
        self.fields_frame.pack(fill='x')

        self._build_fields()

        # Buttons
        btn_frame = tk.Frame(win, bg=C['bg'])
        btn_frame.pack(fill='x', padx=15, pady=12)

        tk.Button(btn_frame, text="Cancel", command=win.destroy,
                  bg='#cccccc', fg=C['text'], font=('Segoe UI', 10),
                  relief='flat', padx=20, pady=6, cursor='hand2').pack(side='right', padx=4)

        tk.Button(btn_frame, text="📄  Generate PDF",
                  command=lambda: self._generate(win),
                  bg=C['sidebar'], fg='white', font=('Segoe UI', 10, 'bold'),
                  relief='flat', padx=20, pady=6, cursor='hand2').pack(side='right', padx=4)

    def _clear_fields(self):
        for w in self.fields_frame.winfo_children():
            w.destroy()

    def _lbl(self, text):
        tk.Label(self.fields_frame, text=text, font=('Segoe UI', 10),
                 bg=self.COLORS['bg'], fg=self.COLORS['text']).pack(anchor='w', pady=(6, 1))

    def _build_fields(self):
        self._clear_fields()
        rt = self.report_type.get()
        C  = self.COLORS

        if rt == 'daily':
            self._lbl("Date (YYYY-MM-DD):")
            self.date_var = tk.StringVar(value=str(date.today()))
            tk.Entry(self.fields_frame, textvariable=self.date_var, width=18,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)
            self._lbl("Class (leave blank for All):")
            self.class_var = tk.StringVar()
            tk.Entry(self.fields_frame, textvariable=self.class_var, width=18,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)

        elif rt == 'monthly':
            self._lbl("Year:")
            self.year_var = tk.StringVar(value=str(date.today().year))
            tk.Entry(self.fields_frame, textvariable=self.year_var, width=10,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)
            self._lbl("Month (1-12):")
            self.month_var = tk.StringVar(value=str(date.today().month))
            tk.Entry(self.fields_frame, textvariable=self.month_var, width=10,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)
            self._lbl("Class (leave blank for All):")
            self.class_var = tk.StringVar()
            tk.Entry(self.fields_frame, textvariable=self.class_var, width=18,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)

        elif rt == 'defaulter':
            self._lbl("Threshold % (default 75):")
            self.threshold_var = tk.StringVar(value='75')
            tk.Entry(self.fields_frame, textvariable=self.threshold_var, width=10,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)

        elif rt == 'class_summary':
            self._lbl("Date (YYYY-MM-DD):")
            self.date_var = tk.StringVar(value=str(date.today()))
            tk.Entry(self.fields_frame, textvariable=self.date_var, width=18,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)

        elif rt == 'student':
            self._lbl("Student ID:")
            self.student_id_var = tk.StringVar()
            tk.Entry(self.fields_frame, textvariable=self.student_id_var, width=18,
                     font=('Segoe UI', 10)).pack(anchor='w', padx=10)

    def _toggle_fields(self):
        self._build_fields()

    def _generate(self, win):
        rt = self.report_type.get()

        # Choose save path
        default_name = {
            'daily':        f"daily_report_{date.today()}.pdf",
            'monthly':      f"monthly_register_{date.today().strftime('%Y_%m')}.pdf",
            'defaulter':    f"defaulter_list_{date.today()}.pdf",
            'class_summary':f"class_summary_{date.today()}.pdf",
            'student':      f"student_report.pdf",
        }.get(rt, "report.pdf")

        path = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF Files', '*.pdf')],
            initialfile=default_name,
            title="Save PDF Report As")

        if not path:
            return

        try:
            if rt == 'daily':
                d_str = getattr(self, 'date_var', tk.StringVar()).get()
                d = datetime.strptime(d_str, '%Y-%m-%d').date() if d_str else date.today()
                cls = getattr(self, 'class_var', tk.StringVar()).get().strip() or None
                generate_daily_report(self.db, path, d, cls)

            elif rt == 'monthly':
                y   = int(self.year_var.get() or date.today().year)
                m   = int(self.month_var.get() or date.today().month)
                cls = self.class_var.get().strip() or None
                generate_monthly_register(self.db, path, y, m, cls)

            elif rt == 'defaulter':
                thr = int(self.threshold_var.get() or 75)
                generate_defaulter_list(self.db, path, thr)

            elif rt == 'class_summary':
                d_str = self.date_var.get()
                d = datetime.strptime(d_str, '%Y-%m-%d').date() if d_str else date.today()
                generate_class_summary(self.db, path, d)

            elif rt == 'student':
                sid = self.student_id_var.get().strip()
                if not sid:
                    messagebox.showerror("Error", "Please enter a Student ID.", parent=win)
                    return
                generate_student_report(self.db, path, sid)

            messagebox.showinfo("Success",
                f"PDF report saved successfully!\n\n{path}", parent=win)
            win.destroy()

            # Try to open the PDF
            try:
                import subprocess, sys
                if sys.platform == 'win32':
                    os.startfile(path)
                elif sys.platform == 'darwin':
                    subprocess.call(['open', path])
                else:
                    subprocess.call(['xdg-open', path])
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("PDF Generation Error", str(e), parent=win)
