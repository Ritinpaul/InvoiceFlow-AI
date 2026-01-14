"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from pathlib import Path
from dotenv import load_dotenv
from .models import Base

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print(f"Warning: DATABASE_URL not found. Checked: {env_path}")
    raise ValueError("DATABASE_URL not found in environment variables")

# Create engine with proper configuration for NeonDB
# NullPool prevents connection pooling issues with serverless databases
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Better for serverless databases like NeonDB
    echo=False,  # Set to True for SQL query logging (debugging)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def get_db():
    """
    Dependency for FastAPI routes
    Provides a database session and ensures cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_vendors(db: Session):
    """
    Seed initial approved vendors
    Called during database initialization
    """
    from .models import Vendor
    
    # Check if vendors already exist
    existing_count = db.query(Vendor).count()
    if existing_count > 0:
        print(f"✓ Database already has {existing_count} vendors")
        return
    
    # Approved vendor list (same as in PolicyAgent)
    approved_vendors = [
        {"name": "Acme Corp", "is_approved": True},
        {"name": "Tech Solutions Inc", "is_approved": True},
        {"name": "Office Supplies Co", "is_approved": True},
        {"name": "Cloud Services Ltd", "is_approved": True},
        {"name": "Legal Advisors LLC", "is_approved": True},
    ]
    
    print("Seeding approved vendors...")
    for vendor_data in approved_vendors:
        vendor = Vendor(**vendor_data)
        db.add(vendor)
    
    db.commit()
    print(f"✓ Seeded {len(approved_vendors)} approved vendors")


if __name__ == "__main__":
    # Run this script to initialize the database
    print("Initializing database...")
    init_db()
    
    # Seed vendors
    db = SessionLocal()
    try:
        seed_vendors(db)
    finally:
        db.close()
    
    print("✓ Database initialization complete")
