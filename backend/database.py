from sqlalchemy import create_engine, text
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
    
    # Ensure slug column exists on existing tables
    with engine.begin() as conn:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [c["name"] for c in inspector.get_columns("forms")]
        if "slug" not in columns:
            conn.execute(text("ALTER TABLE forms ADD COLUMN slug VARCHAR(255) NULL"))
            conn.execute(text("CREATE INDEX ix_forms_slug ON forms(slug)"))
    
    # Backfill slugs for existing forms
    from backend.models import User, Form
    from backend.config import ADMIN_USERNAME, ADMIN_PASSWORD
    from backend.routes.auth import hash_password
    
    db = SessionLocal()
    try:
        slugless = db.query(Form).filter(Form.slug == None).all()
        for form in slugless:
            form.slug = _generate_slug(db, form.title, form.id)
        if slugless:
            db.commit()
        
        if db.query(User).count() == 0:
            hashed = hash_password(ADMIN_PASSWORD)
            user = User(username=ADMIN_USERNAME, hashed_password=hashed)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            db.query(Form).filter(Form.user_id == None).update({Form.user_id: user.id}, synchronize_session=False)
            db.commit()
            print(f"Default admin user '{ADMIN_USERNAME}' seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed default admin: {e}")
    finally:
        db.close()


def _generate_slug(db: Session, title: str, exclude_id: int | None = None) -> str:
    import re
    text = title.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    base_slug = text.strip('-') or "untitled"
    slug = base_slug
    counter = 1
    from backend.models import Form
    while True:
        query = db.query(Form).filter(Form.slug == slug)
        if exclude_id is not None:
            query = query.filter(Form.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1
