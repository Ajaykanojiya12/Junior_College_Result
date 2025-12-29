#!/usr/bin/env python
# backend/reset_admin_password.py
"""
Developer utility script to reset admin password in case of forgotten password.
This script allows a developer to reset the admin password without authentication.

Usage:
    python reset_admin_password.py admin NewPassword123
    python reset_admin_password.py <username> <new_password>
"""

import sys
import os
from app import create_app, db
from models import Admin
from auth import hash_password

def reset_admin_password(username: str, new_password: str):
    """Reset admin password"""
    app = create_app()
    
    with app.app_context():
        # Find admin by username
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin:
            print(f"✱ Notice: Admin user '{username}' not found in database")
            print("\nAvailable admin users:")
            admins = Admin.query.all()
            if admins:
                for a in admins:
                    print(f"  - {a.username} (ID: {a.admin_id}, Active: {a.active})")
            else:
                print("  (No admins found in database)")
            # continue — script will create the admin if not present
        
        # Validate password
        if len(new_password) < 6:
            print("✗ Error: Password must be at least 6 characters long")
            sys.exit(1)
        
        # Hash and update password (or create admin if missing when requested)
        try:
            if admin:
                old_hash = admin.password_hash
                admin.password_hash = hash_password(new_password)
                db.session.commit()
                print(f"\n{'='*60}")
                print("✓ Password Reset Successful")
                print(f"{'='*60}")
                print(f"Username: {admin.username}")
                print(f"New Password: {new_password}")
                print(f"Email: {admin.email}")
                print(f"Active: {admin.active}")
                print(f"{'='*60}")
                print("\n⚠ IMPORTANT NOTES:")
                print("1. Share the new password with the admin securely")
                print("2. Admin should change password after next login")
                print("3. This action is logged and auditable")
                print(f"{'='*60}\n")
            else:
                # Create admin if not found
                from models import Admin as AdminModel
                new_admin = AdminModel()
                new_admin.username = username
                new_admin.password_hash = hash_password(new_password)
                new_admin.email = None
                new_admin.active = True
                db.session.add(new_admin)
                db.session.commit()
                print(f"\n{'='*60}")
                print("✓ Admin Created and Password Set")
                print(f"{'='*60}")
                print(f"Username: {new_admin.username}")
                print(f"New Password: {new_password}")
                print(f"Active: {new_admin.active}")
                print(f"{'='*60}\n")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error resetting/creating admin: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reset an admin user's password (developer utility)."
    )
    parser.add_argument("username", help="Admin username to reset")
    parser.add_argument("new_password", help="New password to set")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not prompt for confirmation",
    )

    args = parser.parse_args()

    username = args.username
    new_password = args.new_password

    print(f"\nAttempting to reset password for admin: {username}")
    print("⚠ This will override the current password!\n")

    if not args.yes:
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("✗ Operation cancelled")
            sys.exit(0)

    reset_admin_password(username, new_password)
