"""
Populate the database with sample data: subjects (if missing), 10 teachers,
allocations, students and some marks for demonstration.
Run with: python backend/scripts/populate_sample_data.py
"""

import os, sys
# ensure backend package root is on sys.path when run from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from werkzeug.security import generate_password_hash
from models import Subject, Teacher, Student, TeacherSubjectAllocation, Mark, Admin

SUBJECTS = [
    ("ENG", "English", "CORE"),
    ("ECO", "Economics", "CORE"),
    ("BK", "Book Keeping", "CORE"),
    ("OC", "Organization of Commerce", "CORE"),
    ("HINDI", "Hindi", "OPTIONAL"),
    ("IT", "Information Technology", "OPTIONAL"),
    ("MATHS", "Mathematics", "OPTIONAL"),
    ("SP", "Statistics & Probability", "OPTIONAL"),
]

TEACHERS = [
    {"userid": f"teacher{i}", "name": f"Teacher {i}", "password": "pass1234", "email": f"t{i}@example.com"}
    for i in range(1, 11)
]

# Simple allocation plan: map teacher index -> subject codes and division(s)
ALLOC_MAP = {
    1: [("ENG", "A")],
    2: [("ECO", "A")],
    3: [("BK", "B")],
    4: [("OC", "B")],
    5: [("HINDI", "A")],
    6: [("IT", "B")],
    7: [("MATHS", "C")],
    8: [("SP", "C")],
    9: [("ENG", "C"), ("ECO","C")],
    10: [("IT", "A"), ("HINDI","B")]
}

# Create sample students across divisions A/B/C; include optional subject assignments
STUDENTS = []
for div in ["A", "B", "C"]:
    for r in range(1, 11):
        roll = f"{div}-{r:02d}"
        name = f"Student {div}{r:02d}"
        # assign optional subjects deterministically
        optional = "HINDI" if (r % 2 == 0) else "IT"
        optional2 = "MATHS" if (r % 3 == 0) else "SP"
        STUDENTS.append({"roll_no": roll, "division": div, "name": name, "optional_subject": optional, "optional_subject_2": optional2})


def safe_commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Commit failed:", e)


def main():
    app = create_app()
    with app.app_context():
        print("Seeding subjects...")
        for code, name, typ in SUBJECTS:
            existing = Subject.query.filter_by(subject_code=code).first()
            if not existing:
                s = Subject()
                s.subject_code = code
                s.subject_name = name
                s.subject_type = typ
                db.session.add(s)
        safe_commit()

        print("Ensuring admin exists...")
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin()
            admin.username = 'admin'
            admin.password_hash = generate_password_hash('admin123')
            admin.email = 'admin@example.com'
            admin.active = True
            db.session.add(admin)
            safe_commit()
            print('Admin created: username=admin password=admin123')

        print("Seeding teachers...")
        created_teachers = []
        for i, t in enumerate(TEACHERS, start=1):
            existing = Teacher.query.filter_by(userid=t['userid']).first()
            if existing:
                created_teachers.append(existing)
                continue
            teacher = Teacher()
            teacher.name = t['name']
            teacher.userid = t['userid']
            teacher.password_hash = generate_password_hash(t['password'])
            teacher.email = t['email']
            teacher.role = 'TEACHER'
            teacher.active = True
            db.session.add(teacher)
            created_teachers.append(teacher)
        safe_commit()

        # refresh teacher ids
        teachers = {t.userid: t for t in Teacher.query.all()}

        print("Seeding allocations...")
        for idx, allocs in ALLOC_MAP.items():
            t_userid = f"teacher{idx}"
            teacher = teachers.get(t_userid)
            if not teacher:
                continue
            for subject_code, division in allocs:
                subj = Subject.query.filter_by(subject_code=subject_code).first()
                if not subj:
                    print("Missing subject", subject_code)
                    continue
                exists = TeacherSubjectAllocation.query.filter_by(teacher_id=teacher.teacher_id, subject_id=subj.subject_id, division=division).first()
                if not exists:
                    a = TeacherSubjectAllocation()
                    a.teacher_id = teacher.teacher_id
                    a.subject_id = subj.subject_id
                    a.division = division
                    db.session.add(a)
        safe_commit()

        print("Seeding students...")
        for s in STUDENTS:
            exists = Student.query.filter_by(roll_no=s['roll_no'], division=s['division']).first()
            if exists:
                continue
            st = Student()
            st.roll_no = s['roll_no']
            st.division = s['division']
            st.name = s['name']
            st.optional_subject = s['optional_subject']
            st.optional_subject_2 = s['optional_subject_2']
            db.session.add(st)
        safe_commit()

        # Optionally add a few marks for demo
        print("Seeding demo marks for a couple of teacher-subject pairs...")
        # pick teacher1 ENG A, teacher5 HINDI A
        def add_mark_if_missing(roll_no, division, subject_code, unit1=10, unit2=12, term=30, annual=60):
            subject = Subject.query.filter_by(subject_code=subject_code).first()
            if not subject:
                return
            existing = Mark.query.filter_by(roll_no=roll_no, division=division, subject_id=subject.subject_id).first()
            if existing:
                return
            tot = unit1 + unit2 + term + annual
            sub_avg = round(tot / 2, 2)
            m = Mark()
            m.roll_no = roll_no
            m.division = division
            m.subject_id = subject.subject_id
            m.unit1 = unit1
            m.unit2 = unit2
            m.term = term
            m.annual = annual
            m.tot = tot
            m.sub_avg = sub_avg
            m.entered_by = None
            db.session.add(m)

        # add marks for first 3 students in A
        for r in range(1,4):
            roll = f"A-{r:02d}"
            add_mark_if_missing(roll, "A", "ENG", 12, 13, 35, 70)
            add_mark_if_missing(roll, "A", "HINDI", 10, 11, 30, 60)
        safe_commit()

        print("Sample data population complete.")


if __name__ == '__main__':
    main()
