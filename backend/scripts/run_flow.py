import requests
import sys
import os
# ensure parent directory (backend) is on sys.path for local imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app, db
from werkzeug.security import generate_password_hash
from models import Teacher, Student, TeacherSubjectAllocation, Subject
import time

BASE = "http://127.0.0.1:5000"

# Seed teacher, students and allocation directly using app context
app = create_app()
with app.app_context():
    # create teacher t1 if not exists
    t = Teacher.query.filter_by(userid="t1").first()
    if not t:
        t = Teacher()
        t.name = "Teacher One"
        t.userid = "t1"
        t.password_hash = generate_password_hash("t1pass")
        t.role = "TEACHER"
        t.active = True
        db.session.add(t)
        db.session.commit()
    teacher_id = t.teacher_id

    # get ENG subject id
    eng = Subject.query.filter_by(subject_code="ENG").first()
    if not eng:
        raise SystemExit("ENG subject not found")
    subject_id = eng.subject_id

    # create allocation for division A
    alloc = TeacherSubjectAllocation.query.filter_by(teacher_id=teacher_id, subject_id=subject_id, division="A").first()
    if not alloc:
        alloc = TeacherSubjectAllocation()
        alloc.teacher_id = teacher_id
        alloc.subject_id = subject_id
        alloc.division = "A"
        db.session.add(alloc)
        db.session.commit()

    # create 3 students in division A
    students = []
    for rn in ("01", "02", "03"):
        s = Student.query.filter_by(roll_no=rn, division="A").first()
        if not s:
            s = Student()
            s.roll_no = rn
            s.division = "A"
            s.name = f"Student {rn}"
            db.session.add(s)
            db.session.commit()
        students.append(s.roll_no)

print("Seeded teacher and students")

# login as teacher
r = requests.post(BASE + "/auth/login", json={"userid": "t1", "password": "t1pass"})
r.raise_for_status()
data = r.json()
token = data["token"]
headers = {"Authorization": f"Bearer {token}"}
print("Logged in as t1")

# helper to enter marks
def enter_mark(roll_no, unit1=10, unit2=10, term=20, annual=40):
    payload = {
        "roll_no": roll_no,
        "division": "A",
        "subject_id": subject_id,
        "unit1": unit1,
        "unit2": unit2,
        "term": term,
        "annual": annual
    }
    resp = requests.post(BASE + "/teacher/marks", json=payload, headers=headers)
    return resp
    

# enter marks for first two students only
print("Entering marks for 2 students (partial)")
for rn in students[:2]:
    r = enter_mark(rn)
    print(r.status_code, r.text)

# get mark id for first student
# fetch via simple API: not available; we'll query results by calling teacher students then marks table via backend API
# attempt to set grace by updating the mark -> should be forbidden
# find mark id by calling admin endpoint? no. Use direct DB lookup via app context
from app import create_app as _create_app
app = _create_app()
with app.app_context():
    from models import Mark
    m = Mark.query.filter_by(roll_no=students[0], division="A", subject_id=subject_id).first()
    if not m:
        print("Mark not found for", students[0])
        raise SystemExit(1)
    mark_id = m.mark_id

print("Attempting to set grace before all marks submitted (should be 403)")
resp = requests.put(BASE + f"/teacher/marks/{mark_id}", json={"unit1":10,"unit2":10,"term":20,"annual":40,"grace":2}, headers=headers)
print(resp.status_code, resp.text)

# enter marks for remaining student
print("Entering marks for remaining student to complete set")
resp = enter_mark(students[2])
print(resp.status_code, resp.text)

# now try to set grace again
print("Attempting to set grace after all marks submitted (should be allowed)")
resp = requests.put(BASE + f"/teacher/marks/{mark_id}", json={"unit1":10,"unit2":10,"term":20,"annual":40,"grace":2}, headers=headers)
print(resp.status_code, resp.text)

# fetch complete table
print("Fetching complete table")
resp = requests.get(BASE + "/teacher/complete-table", params={"division":"A"}, headers=headers)
print(resp.status_code)
print(resp.json())