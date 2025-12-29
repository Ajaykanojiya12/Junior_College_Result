# schemas.py
from marshmallow import Schema, fields, validate

# ------------------------------
# Pagination Schema
# ------------------------------
class PaginationSchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    search = fields.Str(allow_none=True)

# ------------------------------
# Login
# ------------------------------
class LoginSchema(Schema):
    userid = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    password = fields.Str(required=True, validate=validate.Length(min=1))

# ------------------------------
# Teachers
# ------------------------------
class AddTeacherSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    userid = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(allow_none=True)

class UpdateTeacherSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    email = fields.Email(allow_none=True)
    assigned_subject = fields.Str(validate=validate.Length(min=1, max=100))
    active = fields.Bool()

# ------------------------------
# Students
# ------------------------------
class StudentSchema(Schema):
    student_id = fields.Int()
    roll_no = fields.Str(required=True)
    division = fields.Str(required=True)
    name = fields.Str(required=True)
    optional_subject = fields.Str(allow_none=True)
    optional_subject_2 = fields.Str(allow_none=True)
    created_at = fields.DateTime()


# ------------------------------
# Enter Marks
# ------------------------------
class EnterMarkSchema(Schema):
    roll_no = fields.Str(required=True)
    division = fields.Str(required=True)
    subject_id = fields.Int(required=True)

    unit1 = fields.Float(required=True, validate=validate.Range(min=0, max=25))
    unit2 = fields.Float(required=True, validate=validate.Range(min=0, max=25))
    term = fields.Float(required=True, validate=validate.Range(min=0, max=50))
    annual = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    grace = fields.Float(load_default=0.0)


class UpdateMarkSchema(Schema):
    # Allow frontend to send identifying fields as well so Marshmallow doesn't
    # reject unknown keys when updating marks. These are optional for update.
    roll_no = fields.Str(required=False)
    division = fields.Str(required=False)
    subject_id = fields.Int(required=False)

    unit1 = fields.Float(required=True, validate=validate.Range(min=0, max=25))
    unit2 = fields.Float(required=True, validate=validate.Range(min=0, max=25))
    term = fields.Float(required=True, validate=validate.Range(min=0, max=50))
    annual = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    grace = fields.Float(load_default=0.0)


# ------------------------------
# Results (FINAL – AVG)
# ------------------------------
class ResultSchema(Schema):
    result_id = fields.Int()
    roll_no = fields.Str()
    name = fields.Str()
    division = fields.Str()

    eng_avg = fields.Float()
    eng_grace = fields.Float()

    hindi_avg = fields.Float()
    hindi_grace = fields.Float()

    it_avg = fields.Float()
    it_grace = fields.Float()

    bk_avg = fields.Float()
    bk_grace = fields.Float()

    oc_avg = fields.Float()
    oc_grace = fields.Float()

    maths_avg = fields.Float()
    maths_grace = fields.Float()

    sp_avg = fields.Float()
    sp_grace = fields.Float()

    total_grace = fields.Float()
    percentage = fields.Float()
    is_published = fields.Bool()

    evs_grade = fields.Str()
    pe_grade = fields.Str()

    created_at = fields.DateTime()
    updated_at = fields.DateTime()


# ------------------------------
# Subject Schema
# ------------------------------
class SubjectSchema(Schema):
    subject_id = fields.Int()
    subject_code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    subject_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    subject_type = fields.Str(required=True)
    active = fields.Bool()

# ------------------------------
# Allocate Subject Schema
# ------------------------------
class AllocateSubjectSchema(Schema):
    teacher_id = fields.Int(required=True)
    subject_id = fields.Int(required=True)
    division = fields.Str(required=True, validate=validate.OneOf(['A', 'B', 'C']))

# ------------------------------
# Change Password Schema
# ------------------------------
class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, validate=validate.Length(min=1))
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True, validate=validate.Length(min=6))
