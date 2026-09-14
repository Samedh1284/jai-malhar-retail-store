from getpass import getpass

from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import Admin


def create_admin():
    print("\n=== Create Admin Account ===")

    username = input("Enter admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    if not password:
        print("Password cannot be empty.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    existing_admin = Admin.query.filter_by(
        username=username
    ).first()

    if existing_admin:
        print("This admin username already exists.")
        return

    password_hash = generate_password_hash(password)

    admin = Admin(
        username=username,
        password_hash=password_hash
    )

    db.session.add(admin)
    db.session.commit()

    print("\nAdmin account created successfully.")


def initialize_database():
    print("Creating database tables...")

    with app.app_context():
        db.create_all()

        print("Database tables created successfully.")

        create_admin()


if __name__ == "__main__":
    initialize_database()