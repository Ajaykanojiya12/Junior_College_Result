from app import db
from sqlalchemy import CheckConstraint
from datetime import datetime
from flask_login import UserMixin

def now():
    return datetime.utcnow()

# =====================================================
# ADMIN
# =====================================================
class Admin(db.Model, UserMixin):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    def get_id(self):
        return str(self.admin_id)

# =====================================================
# SUBJECTS
# =====================================================
class Subject(db.Model):
    __tablename__ = "subjects"
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_type = db.Column(db.String(50), nullable=False)  # CORE / OPTIONAL
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    marks = db.relationship("Mark", backref="subject", cascade="all, delete-orphan")
    teacher_allocations = db.relationship(
        "TeacherSubjectAllocation",
        backref="subject_ref",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "subject_type != 'OPTIONAL' OR subject_code IN ('HINDI','IT','MATHS','SP')",
            name="ck_optional_allowed_codes"
        ),
    )

# =====================================================
# TEACHERS
# =====================================================
class Teacher(db.Model, UserMixin):
    __tablename__ = "teachers"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    userid = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(
        db.Enum("ADMIN", "TEACHER", name="teacher_role_enum"),
        nullable=False,
        default="TEACHER"
    )
    
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    subject_allocations = db.relationship(
        "TeacherSubjectAllocation",
        backref="teacher_ref",
        cascade="all, delete-orphan"
    )

    marks_entered = db.relationship(
        "Mark",
        backref="entered_by_teacher",
        cascade="all, delete-orphan"
    )

    def __init__(
        self,
        name=None,
        userid=None,
        password_hash=None,
        email=None,
        role="TEACHER",
        active=True,
        **kwargs,
    ):
        # Accept common keyword args used across the codebase and
        # forward any additional kwargs to the SQLAlchemy base
        if name is not None:
            self.name = name
        if userid is not None:
            self.userid = userid
        if password_hash is not None:
            self.password_hash = password_hash
        if email is not None:
            self.email = email
        if role is not None:
            self.role = role
        if active is not None:
            self.active = active

        # Let SQLAlchemy handle any remaining kwargs
        try:
            super().__init__(**kwargs)
        except TypeError:
            # Older SQLAlchemy bases may not accept kwargs in super(); ignore
            pass

    def get_id(self):
        return str(self.teacher_id)

# =====================================================
# TEACHER-SUBJECT ALLOCATIONS
# =====================================================
class TeacherSubjectAllocation(db.Model):
    __tablename__ = "teacher_subject_allocations"
    allocation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    division = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("teacher_id", "subject_id", "division", name="uq_teacher_subject_div"),
    )

# =====================================================
# STUDENTS  ✅ FIXED
# =====================================================
class Student(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_no = db.Column(db.String(50), nullable=False, index=True)
    division = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)

    # ✅ REQUIRED FOR OPTIONAL SUBJECT LOGIC
    optional_subject = db.Column(db.String(20))      # HINDI / IT
    optional_subject_2 = db.Column(db.String(20))    # MATHS / SP

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("roll_no", "division", name="uq_roll_division"),
    )

# =====================================================
# MARKS  ✅ FIXED
# =====================================================
class Mark(db.Model):
    __tablename__ = "marks"
    mark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_no = db.Column(db.String(50), nullable=False, index=True)
    division = db.Column(db.String(10), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)

    unit1 = db.Column(db.Float, default=0.0)
    unit2 = db.Column(db.Float, default=0.0)
    internal = db.Column(db.Float, default=0.0)
    term = db.Column(db.Float, default=0.0)
    annual = db.Column(db.Float, default=0.0)

    tot = db.Column(db.Float, default=0.0)
    sub_avg = db.Column(db.Float, default=0.0)
    grace = db.Column(db.Float, default=0.0)

    entered_by = db.Column(
        db.Integer,
        db.ForeignKey("teachers.teacher_id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("roll_no", "division", "subject_id", name="uq_roll_div_subject"),
    )

# =====================================================
# RESULTS (FINAL MARKSHEET – AVG OUT OF 100)
# =====================================================
class Result(db.Model):
    __tablename__ = "results"
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_no = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(200))
    division = db.Column(db.String(10), nullable=False)

    # Final subject averages (out of 100)
    eng_avg = db.Column(db.Float)
    eng_grace = db.Column(db.Float, default=0.0)

    hindi_avg = db.Column(db.Float)
    hindi_grace = db.Column(db.Float, default=0.0)

    it_avg = db.Column(db.Float)
    it_grace = db.Column(db.Float, default=0.0)

    bk_avg = db.Column(db.Float)
    bk_grace = db.Column(db.Float, default=0.0)

    oc_avg = db.Column(db.Float)
    oc_grace = db.Column(db.Float, default=0.0)

    maths_avg = db.Column(db.Float)
    maths_grace = db.Column(db.Float, default=0.0)

    sp_avg = db.Column(db.Float)
    sp_grace = db.Column(db.Float, default=0.0)

    total_grace = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    evs_grade = db.Column(db.String(2))
    pe_grade = db.Column(db.String(2))

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("roll_no", "division", name="uq_result_roll_division"),
    )

    def __repr__(self):
        return f"<Result roll={self.roll_no} div={self.division}>"


# # =====================================================
# # PERMISSIONS
# # =====================================================
# class Permission(db.Model):
#     __tablename__ = "permissions"
#     permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
#     granted_to_admin_id = db.Column(db.Integer, db.ForeignKey("admins.admin_id", ondelete="SET NULL"))

#     db_name = db.Column(db.String(255), nullable=False)
#     table_name = db.Column(db.String(255), nullable=False)
#     column_name = db.Column(db.String(255))

#     can_read = db.Column(db.Boolean, default=False, nullable=False)
#     can_write = db.Column(db.Boolean, default=False, nullable=False)
#     confidential = db.Column(db.Boolean, default=False, nullable=False)

#     granted_by = db.Column(db.String(150))
#     granted_at = db.Column(db.DateTime, default=now, nullable=False)
