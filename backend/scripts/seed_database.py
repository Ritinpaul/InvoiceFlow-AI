"""
Database seeding script for demo/production use
Seeds the database with approved vendors and test data
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import SessionLocal, Vendor
from sqlalchemy import text

def seed_approved_vendors():
    """Add approved vendors to the database"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding Approved Vendors...\n")
        
        # Approved vendors for demo
        approved_vendors = [
            {
                "name": "TechSupplies Inc",
                "email": "billing@techsupplies.com",
                "phone": "+1-555-0100",
                "tax_id": "12-3456789",
                "address": "123 Tech Street, San Francisco, CA 94105",
                "is_approved": True
            },
            {
                "name": "OfficeDepot",
                "email": "corporate@officedepot.com",
                "phone": "+1-555-0200",
                "tax_id": "98-7654321",
                "address": "456 Office Ave, New York, NY 10001",
                "is_approved": True
            },
            {
                "name": "Amazon Business",
                "email": "business@amazon.com",
                "phone": "+1-555-0300",
                "tax_id": "11-2233445",
                "address": "789 Commerce Blvd, Seattle, WA 98101",
                "is_approved": True
            },
            {
                "name": "Staples Business Advantage",
                "email": "advantage@staples.com",
                "phone": "+1-555-0400",
                "tax_id": "55-6677889",
                "address": "321 Supply Lane, Boston, MA 02101",
                "is_approved": True
            },
            {
                "name": "Dell Technologies",
                "email": "enterprise@dell.com",
                "phone": "+1-555-0500",
                "tax_id": "22-3344556",
                "address": "555 Dell Way, Austin, TX 78701",
                "is_approved": True
            }
        ]
        
        vendors_added = 0
        vendors_updated = 0
        
        for vendor_data in approved_vendors:
            # Check if vendor already exists
            existing = db.query(Vendor).filter(Vendor.name == vendor_data["name"]).first()
            
            if existing:
                # Update to approved status
                if not existing.is_approved:
                    existing.is_approved = True
                    existing.email = vendor_data.get("email")
                    existing.phone = vendor_data.get("phone")
                    existing.tax_id = vendor_data.get("tax_id")
                    existing.address = vendor_data.get("address")
                    vendors_updated += 1
                    print(f"  ✅ Updated: {vendor_data['name']} (now approved)")
                else:
                    print(f"  ℹ️  Already approved: {vendor_data['name']}")
            else:
                # Create new vendor
                vendor = Vendor(**vendor_data)
                db.add(vendor)
                vendors_added += 1
                print(f"  ✅ Added: {vendor_data['name']}")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Seeding Complete!")
        print(f"   New Vendors: {vendors_added}")
        print(f"   Updated: {vendors_updated}")
        
        # Show all approved vendors
        approved = db.query(Vendor).filter(Vendor.is_approved == True).all()
        print(f"   Total Approved Vendors: {len(approved)}")
        print(f"{'='*60}\n")
        
        print("📋 Approved Vendors List:")
        for v in approved:
            print(f"   • {v.name} (ID: {v.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding vendors: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def reset_database():
    """Reset database - DANGER: Deletes all data"""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    confirmation = input("Type 'RESET' to confirm: ")
    
    if confirmation != "RESET":
        print("Cancelled.")
        return False
    
    db = SessionLocal()
    try:
        print("\n🗑️  Resetting database...")
        
        # Delete all data (in correct order due to foreign keys)
        db.execute(text("DELETE FROM processing_logs"))
        db.execute(text("DELETE FROM processing_results"))
        db.execute(text("DELETE FROM invoices"))
        db.execute(text("DELETE FROM vendors"))
        
        # Reset sequences
        db.execute(text("ALTER SEQUENCE vendors_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE invoices_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE processing_results_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE processing_logs_id_seq RESTART WITH 1"))
        
        db.commit()
        print("✅ Database reset complete!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main seeding function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database seeding utilities")
    parser.add_argument("--reset", action="store_true", help="Reset database (delete all data)")
    parser.add_argument("--vendors", action="store_true", help="Seed approved vendors")
    parser.add_argument("--all", action="store_true", help="Run all seeding operations")
    
    args = parser.parse_args()
    
    if args.reset:
        if reset_database():
            print("Database reset. You can now run seeding operations.")
    
    if args.vendors or args.all:
        seed_approved_vendors()
    
    if not (args.reset or args.vendors or args.all):
        # Default: just seed vendors
        print("Running default seeding: Approved Vendors\n")
        print("Use --help to see all options\n")
        seed_approved_vendors()

if __name__ == "__main__":
    main()
