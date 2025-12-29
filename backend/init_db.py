#!/usr/bin/env python
"""Initialize the database with all required tables."""

import pymysql
import sys
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from app import create_app, db
from models import Subject, Admin, Teacher, Student
from sqlalchemy import func
# Optionally populate sample data if not present
try:
    from scripts.populate_sample_data import main as populate_sample_main
except Exception:
    populate_sample_main = None
from werkzeug.security import generate_password_hash

def create_database_if_not_exists():
    """Create the main database if it doesn't exist."""
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
            connection.commit()
        connection.close()
        print(f"✓ Database '{MYSQL_DB}' ready")
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        sys.exit(1)

def init_database():
    print("Initializing database...")

    create_database_if_not_exists()

    app = create_app()
    with app.app_context():
        db.create_all()
        print("✓ All tables created")

        # Seed ONLY subjects (master data)
        subjects_data = [
            {"subject_code": "ENG", "subject_name": "English", "subject_type": "CORE"},
            {"subject_code": "HINDI", "subject_name": "Hindi", "subject_type": "OPTIONAL"},
            {"subject_code": "IT", "subject_name": "Information Technology", "subject_type": "OPTIONAL"},
            {"subject_code": "ECO", "subject_name": "Economics", "subject_type": "CORE"},
            {"subject_code": "BK", "subject_name": "Book Keeping", "subject_type": "CORE"},
            {"subject_code": "OC", "subject_name": "Organization of Commerce", "subject_type": "CORE"},
            {"subject_code": "MATHS", "subject_name": "Mathematics", "subject_type": "OPTIONAL"},
            {"subject_code": "SP", "subject_name": "Statistics & Probability", "subject_type": "OPTIONAL"},
            {"subject_code": "EVS", "subject_name": "Environmental Studies", "subject_type": "CORE"},
            {"subject_code": "PE", "subject_name": "Physical Education", "subject_type": "CORE"},
        ]

        if Subject.query.count() == 0:
            for data in subjects_data:
                db.session.add(Subject(**data))
            db.session.commit()
            print("✓ Subjects seeded")

        # Seed a default admin user for local development if none exist.
        # Use explicit attribute assignment to avoid passing unexpected
        # constructor kwargs (static analyzers flag these in some setups).
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            # Determine a safe admin_id that does not collide with teacher ids
            max_teacher_id = db.session.query(func.max(Teacher.teacher_id)).scalar() or 0
            max_admin_id = db.session.query(func.max(Admin.admin_id)).scalar() or 0
            desired_admin_id = max(max_teacher_id + 1, max_admin_id + 1)

            admin = Admin()
            # set a non-colliding primary key before insert to avoid id overlap
            admin.admin_id = desired_admin_id
            admin.username = 'admin'
            admin.password_hash = generate_password_hash('admin123')
            admin.email = 'admin@example.com'
            admin.active = True

            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin created (username: admin, password: admin123)")

        # If there are no teachers or students, populate sample data
        try:
            teacher_count = Teacher.query.count()
            student_count = Student.query.count()
        except Exception:
            teacher_count = 0
            student_count = 0

        if (teacher_count == 0 or student_count == 0) and populate_sample_main:
            print("Seeding sample teachers, allocations and students...")
            try:
                populate_sample_main()
                print("✓ Sample data populated")
            except Exception as e:
                print("✗ Sample data population failed:", e)

    print("✓ Database initialization complete")


if __name__ == "__main__":
    try:
        init_database()
        print("\n✓ Database initialization complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
