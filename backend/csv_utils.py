# backend/csv_utils.py
"""
Utilities for exporting data to CSV format
"""
import csv
from io import StringIO
from flask import make_response
from datetime import datetime

def generate_csv_response(filename, headers, rows):
    """
    Generate a CSV response for download
    
    Args:
        filename: Name of the file to download
        headers: List of column headers
        rows: List of rows, where each row is a dict or list
    
    Returns:
        Flask response with CSV file
    """
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(headers)
    
    # Write rows
    if rows and isinstance(rows[0], dict):
        for row in rows:
            writer.writerow([row.get(header, "") for header in headers])
    else:
        writer.writerows(rows)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-Type"] = "text/csv"
    return output

def export_teachers_csv(teachers):
    """Export teachers list to CSV"""
    headers = ["Teacher ID", "Name", "User ID", "Subject", "Email", "Active", "Created At"]
    rows = [
        [
            t.teacher_id,
            t.name,
            t.userid,
            t.assigned_subject,
            t.email or "",
            "Yes" if t.active else "No",
            t.created_at.isoformat() if t.created_at else ""
        ]
        for t in teachers
    ]
    return generate_csv_response(
        f"teachers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        headers,
        rows
    )


def export_marks_csv(marks_data):
    """Export marks data to CSV"""
    headers = ["Student ID", "Roll No", "Name", "Subject", "Exam Type", "Score", "Max Marks", "Entered By", "Entered At"]
    rows = [
        [
            m.get("student_id", ""),
            m.get("roll_no", ""),
            m.get("name", ""),
            m.get("subject_code", ""),
            m.get("exam_type", ""),
            m.get("score", ""),
            m.get("max_marks", ""),
            m.get("entered_by", ""),
            m.get("entered_at", "")
        ]
        for m in marks_data
    ]
    return generate_csv_response(
        f"marks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        headers,
        rows
    )

def export_students_csv(students_data):
    """Export students list to CSV"""
    headers = ["Student ID", "Roll No", "Name", "DOB", "Class Year", "Section", "Created At"]
    rows = [
        [
            s.get("student_id", ""),
            s.get("roll_no", ""),
            s.get("name", ""),
            s.get("dob", ""),
            s.get("class_year", ""),
            s.get("section", ""),
            s.get("created_at", "")
        ]
        for s in students_data
    ]
    return generate_csv_response(
        f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        headers,
        rows
    )
