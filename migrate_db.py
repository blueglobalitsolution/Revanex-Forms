import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust path to find backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import DATABASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD
from backend.models import User, Form
from backend.routes.auth import hash_password

def run_migration():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    # 1. Alter forms table to add user_id column and foreign key constraint
    with engine.begin() as conn:
        print("Checking/Applying schema migration...")
        
        # Add user_id column if it doesn't exist
        try:
            conn.execute(text("ALTER TABLE forms ADD COLUMN user_id INT NULL;"))
            print("- Added 'user_id' column to 'forms' table.")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("- 'user_id' column already exists.")
            else:
                print(f"Error adding user_id column: {e}")
                
        # Add email column to users table if it doesn't exist
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL;"))
            print("- Added 'email' column to 'users' table.")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("- 'email' column already exists in 'users' table.")
            else:
                print(f"Error adding email column to users: {e}")
                
        # Add foreign key constraint if it doesn't exist
        try:
            conn.execute(text(
                "ALTER TABLE forms ADD CONSTRAINT fk_forms_user "
                "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"
            ))
            print("- Added foreign key constraint 'fk_forms_user'.")
        except Exception as e:
            if "Duplicate key name" in str(e) or "1212" in str(e) or "Duplicate foreign key constraint" in str(e) or "1022" in str(e) or "already exists" in str(e):
                print("- Foreign key constraint already exists.")
            else:
                print(f"Note: Foreign key constraint setup bypassed (or already exists): {e}")

    # 2. Seed default admin user and claim orphaned forms
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print(f"No users found. Seeding default admin user '{ADMIN_USERNAME}'...")
            hashed = hash_password(ADMIN_PASSWORD)
            admin_user = User(username=ADMIN_USERNAME, hashed_password=hashed)
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"- Default admin user '{ADMIN_USERNAME}' seeded successfully.")
            
            # Associate orphaned forms
            orphans_count = db.query(Form).filter(Form.user_id == None).count()
            if orphans_count > 0:
                db.query(Form).filter(Form.user_id == None).update({Form.user_id: admin_user.id})
                db.commit()
                print(f"- Claimed {orphans_count} existing orphaned form(s) for '{ADMIN_USERNAME}'.")
        else:
            print(f"Database already has {user_count} user(s). Seeding skipped.")
            
            # Check if there are orphaned forms that need to be assigned to the first user
            first_user = db.query(User).order_by(User.id.asc()).first()
            orphans_count = db.query(Form).filter(Form.user_id == None).count()
            if first_user and orphans_count > 0:
                db.query(Form).filter(Form.user_id == None).update({Form.user_id: first_user.id})
                db.commit()
                print(f"- Assigned {orphans_count} orphaned form(s) to existing user '{first_user.username}'.")
                
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()
        
    print("Migration and seeding check completed successfully!")

if __name__ == "__main__":
    run_migration()
