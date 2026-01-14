"""
Phase 3 Testing: Database Integration
Tests database models, connection, and API endpoints
"""
import asyncio
import sys
from pathlib import Path
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, seed_vendors, SessionLocal
from database.models import Vendor, Invoice, ProcessingResult, DecisionStatus, ApprovalLevel, RiskLevel


def test_database_connection():
    """Test 1: Database connection"""
    print("\n" + "="*80)
    print("Test 1: Database Connection")
    print("="*80)
    
    try:
        db = SessionLocal()
        # Try a simple query
        count = db.query(Vendor).count()
        db.close()
        print(f"✓ Database connection successful")
        print(f"✓ Current vendor count: {count}")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_table_creation():
    """Test 2: Create all tables"""
    print("\n" + "="*80)
    print("Test 2: Table Creation")
    print("="*80)
    
    try:
        init_db()
        print(f"✓ All tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False


def test_vendor_seeding():
    """Test 3: Seed vendors"""
    print("\n" + "="*80)
    print("Test 3: Vendor Seeding")
    print("="*80)
    
    try:
        db = SessionLocal()
        seed_vendors(db)
        
        vendors = db.query(Vendor).filter(Vendor.is_approved == True).all()
        print(f"✓ Vendors seeded successfully")
        print(f"✓ Approved vendors: {len(vendors)}")
        for v in vendors:
            print(f"  - {v.name}")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Vendor seeding failed: {e}")
        return False


def test_invoice_creation():
    """Test 4: Create sample invoice and processing result"""
    print("\n" + "="*80)
    print("Test 4: Invoice & Processing Result Creation")
    print("="*80)
    
    try:
        db = SessionLocal()
        
        # Get a vendor
        vendor = db.query(Vendor).filter(Vendor.name == "Acme Corp").first()
        
        if not vendor:
            print("⚠ Vendor 'Acme Corp' not found, creating...")
            vendor = Vendor(name="Acme Corp", is_approved=True)
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
        
        # Create invoice
        invoice = Invoice(
            filename="test_invoice.pdf",
            file_path="uploads/test_invoice.pdf",
            file_size=12345,
            invoice_number="INV-TEST-001",
            invoice_date="2026-01-15",
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            total_amount=2500.00,
            currency="USD",
            tax_amount=250.00,
            po_number="PO-TEST-001",
            extraction_confidence=0.95
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        print(f"✓ Invoice created: ID={invoice.id}, Number={invoice.invoice_number}")
        
        # Create processing result
        result = ProcessingResult(
            invoice_id=invoice.id,
            fraud_risk_score=0.15,
            fraud_risk_level=RiskLevel.MINIMAL,
            is_suspicious=False,
            fraud_flags=[],
            fraud_check_results={},
            policy_compliant=True,
            policy_violations=[],
            policy_warnings=["Test warning"],
            approval_level=ApprovalLevel.AUTO_APPROVE,
            approver_required=None,
            decision=DecisionStatus.APPROVE,
            decision_reason="All checks passed - test invoice",
            decision_confidence=0.95,
            decision_recommendation="Approved for testing",
            decision_summary={"test": True},
            total_processing_time=2.5
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        print(f"✓ Processing result created: ID={result.id}, Decision={result.decision.value}")
        
        # Query back
        invoice_check = db.query(Invoice).filter(Invoice.id == invoice.id).first()
        result_check = db.query(ProcessingResult).filter(ProcessingResult.invoice_id == invoice.id).first()
        
        print(f"✓ Database read successful:")
        print(f"  Invoice: {invoice_check.invoice_number} - ${invoice_check.total_amount}")
        print(f"  Decision: {result_check.decision.value} (confidence: {result_check.decision_confidence:.0%})")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Invoice creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queries():
    """Test 5: Complex queries"""
    print("\n" + "="*80)
    print("Test 5: Complex Queries")
    print("="*80)
    
    try:
        db = SessionLocal()
        
        # Query all invoices with their processing results
        invoices = db.query(Invoice).join(ProcessingResult).all()
        print(f"✓ Found {len(invoices)} invoices with processing results")
        
        # Query by decision status
        approved = db.query(ProcessingResult).filter(ProcessingResult.decision == DecisionStatus.APPROVE).count()
        print(f"✓ Approved invoices: {approved}")
        
        # Query suspicious invoices
        suspicious = db.query(ProcessingResult).filter(ProcessingResult.is_suspicious == True).count()
        print(f"✓ Suspicious invoices: {suspicious}")
        
        # Query approved vendors
        approved_vendors = db.query(Vendor).filter(Vendor.is_approved == True).count()
        print(f"✓ Approved vendors: {approved_vendors}")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Query test failed: {e}")
        return False


def main():
    print("="*80)
    print("PHASE 3 DATABASE INTEGRATION TESTING")
    print("Testing NeonDB Connection and Database Models")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Table Creation", test_table_creation()))
    results.append(("Vendor Seeding", test_vendor_seeding()))
    results.append(("Invoice Creation", test_invoice_creation()))
    results.append(("Complex Queries", test_queries()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {test_name}")
    
    print(f"\n{passed_count}/{total_count} tests passed ({passed_count/total_count*100:.0f}%)")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Phase 3 database integration is working correctly.")
        print("✓ NeonDB connection successful")
        print("✓ All tables created")
        print("✓ Data persistence working")
        return 0
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed. Review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
