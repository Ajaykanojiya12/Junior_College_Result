# # backend/db_utils.py

# import re
# import logging
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import SQLAlchemyError
# from app import db
# import config

# # Only letters, digits, underscores allowed in DB names
# DB_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


# def _validate_db_name(db_name: str):
#     if not db_name or not DB_NAME_RE.match(db_name):
#         raise ValueError("Invalid database name. Only letters, digits and underscores are allowed.")


# def build_batch_db_uri(db_name: str) -> str:
#     """
#     Build a MySQL URI for SQLAlchemy using configured MySQL credentials.
#     """
#     user = config.MYSQL_USER
#     pwd = config.MYSQL_PASSWORD
#     host = config.MYSQL_HOST
#     port = config.MYSQL_PORT
#     return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db_name}"


# def create_database_and_schema(db_name: str) -> bool:
#     """
#     Creates a new batch database and required tables.
#     Schema strictly matches models.py and final ERD.
#     """
#     _validate_db_name(db_name)

#     # -------------------------------------------------
#     # 1. Create database using admin connection
#     # -------------------------------------------------
#     engine_admin = db.get_engine()
#     create_db_sql = text(
#         f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
#         "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
#     )

#     try:
#         with engine_admin.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
#             conn.execute(create_db_sql)
#             logging.info(f"Database '{db_name}' created or already exists.")
#     except SQLAlchemyError as e:
#         logging.exception("Error creating database")
#         raise e

#     # -------------------------------------------------
#     # 2. Connect to batch DB and create tables
#     # -------------------------------------------------
#     batch_uri = build_batch_db_uri(db_name)
#     engine_batch = create_engine(batch_uri, pool_pre_ping=True)

#     try:
#         with engine_batch.connect() as conn:

#             # -----------------------------
#             # STUDENTS TABLE
#             # -----------------------------
#             conn.execute(text("""
#             CREATE TABLE IF NOT EXISTS students (
#                 student_id INT AUTO_INCREMENT PRIMARY KEY,
#                 roll_no VARCHAR(50) NOT NULL,
#                 division VARCHAR(10) NOT NULL,
#                 name VARCHAR(200) NOT NULL,
#                 optional_subject VARCHAR(20),
#                 optional_subject_2 VARCHAR(20),
#                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                 UNIQUE KEY uq_roll_division (roll_no, division)
#             ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
#             """))

#             logging.info(f"'students' table ensured in database '{db_name}'.")

#             # -----------------------------
#             # MARKS TABLE
#             # -----------------------------
#             conn.execute(text("""
#             CREATE TABLE IF NOT EXISTS marks (
#                 mark_id INT AUTO_INCREMENT PRIMARY KEY,
#                 roll_no VARCHAR(50) NOT NULL,
#                 division VARCHAR(10) NOT NULL,
#                 subject_id INT NOT NULL,
#                 unit1 FLOAT DEFAULT 0,
#                 unit2 FLOAT DEFAULT 0,
#                 internal FLOAT DEFAULT 0,
#                 term FLOAT DEFAULT 0,
#                 annual FLOAT DEFAULT 0,
#                 tot FLOAT DEFAULT 0,
#                 sub_avg FLOAT DEFAULT 0,
#                 grace FLOAT DEFAULT 0,
#                 entered_by INT NULL,
#                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                 UNIQUE KEY uq_roll_div_subject (roll_no, division, subject_id)
#             ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
#             """))

#             logging.info(f"'marks' table ensured in database '{db_name}'.")

#             conn.commit()

#     finally:
#         engine_batch.dispose()

#     return True
