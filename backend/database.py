from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed default user if no users exist
    from backend.models import User, Form
    from backend.config import ADMIN_USERNAME, ADMIN_PASSWORD
    from backend.routes.auth import hash_password
    
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            hashed = hash_password(ADMIN_PASSWORD)
            user = User(username=ADMIN_USERNAME, hashed_password=hashed)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Associate any orphaned forms to this first user
            db.query(Form).filter(Form.user_id == None).update({Form.user_id: user.id}, synchronize_session=False)
            db.commit()
            print(f"Default admin user '{ADMIN_USERNAME}' seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed default admin: {e}")
    finally:
        db.close()
