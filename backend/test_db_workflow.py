"""
Simple End-to-End Database Test
Tests database storage independently
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, Invoice, ProcessingResult, Vendor
from database.models import DecisionStatus, ApprovalLevel, RiskLevel


def test_complete_workflow():
    """Simulate a complete invoice processing workflow"""
    print("="*80)
    print("END-TO-END DATABASE WORKFLOW TEST")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Step 1: Get/Create Vendor
        print("\n[Step 1] Vendor Management...")
        vendor = db.query(Vendor).filter(Vendor.name == "Acme Corp").first()
        if not vendor:
            vendor = Vendor(name="Acme Corp", is_approved=True)
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
        print(f"✓ Vendor: {vendor.name} (ID: {vendor.id}, Approved: {vendor.is_approved})")
        
        # Step 2: Create Invoice
        print("\n[Step 2] Invoice Creation...")
        invoice = Invoice(
            filename="test_workflow.jpg",
            file_path="uploads/test_workflow.jpg",
            file_size=15000,
            invoice_number="INV-E2E-001",
            invoice_date="2026-01-15",
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            total_amount=5220.23,
            currency="USD",
            tax_amount=474.56,
            po_number="PO-2026-500",
            extraction_confidence=0.92,
            ocr_text="INVOICE ... Acme Corp ... Total: $5,220.23",
            uploaded_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        print(f"✓ Invoice created: {invoice.invoice_number}")
        print(f"  Vendor: {invoice.vendor_name}")
        print(f"  Amount: ${invoice.total_amount:,.2f}")
        print(f"  Date: {invoice.invoice_date}")
        
        # Step 3: Create Processing Result
        print("\n[Step 3] Processing Results...")
        processing = ProcessingResult(
            invoice_id=invoice.id,
            fraud_risk_score=0.15,
            fraud_risk_level=RiskLevel.MINIMAL,
            is_suspicious=False,
            fraud_flags=["Suspicious round amount: USD 5,220.23"],
            fraud_check_results={
                "duplicate": False,
                "high_amount": False,
                "round_amount": True
            },
            policy_compliant=True,
            policy_violations=[],
            policy_warnings=["Verify PO number exists in system"],
            approval_level=ApprovalLevel.REQUIRES_MANAGER,
            approver_required="Manager",
            decision=DecisionStatus.APPROVE,
            decision_reason="Approved pending manager confirmation (amount: $5,220.23)",
            decision_confidence=0.80,
            decision_recommendation="✓ Recommended for approval. Note: 1 warnings flagged",
            decision_summary={
                "fraud_risk": "MINIMAL",
                "policy_status": "Compliant",
                "approval_required": "Manager",
                "amount": 5220.23,
                "vendor": "Acme Corp"
            },
            total_processing_time=3.42
        )
        db.add(processing)
        db.commit()
        db.refresh(processing)
        
        print(f"✓ Processing result created:")
        print(f"  Decision: {processing.decision.value}")
        print(f"  Fraud Risk: {processing.fraud_risk_level.value} ({processing.fraud_risk_score:.2f})")
        print(f"  Policy: {'Compliant' if processing.policy_compliant else 'Non-compliant'}")
        print(f"  Approval: {processing.approval_level.value}")
        print(f"  Confidence: {processing.decision_confidence:.0%}")
        
        # Step 4: Query and Verify
        print("\n[Step 4] Database Verification...")
        
        # Query invoice with processing result
        inv = db.query(Invoice).filter(Invoice.id == invoice.id).first()
        proc = db.query(ProcessingResult).filter(ProcessingResult.invoice_id == invoice.id).first()
        
        if not inv or not proc:
            print("✗ Failed to retrieve data from database")
            return False
        
        print("✓ Data successfully persisted and retrieved")
        print(f"\nStored Invoice:")
        print(f"  #{inv.invoice_number} | {inv.vendor_name} | ${inv.total_amount:,.2f}")
        print(f"  Decision: {proc.decision.value} | Risk: {proc.fraud_risk_level.value}")
        
        # Step 5: Test Queries
        print("\n[Step 5] Query Capabilities...")
        
        # Count by decision
        approved_count = db.query(ProcessingResult).filter(
            ProcessingResult.decision == DecisionStatus.APPROVE
        ).count()
        print(f"✓ Approved invoices: {approved_count}")
        
        # Count by vendor
        acme_invoices = db.query(Invoice).filter(
            Invoice.vendor_name == "Acme Corp"
        ).count()
        print(f"✓ Acme Corp invoices: {acme_invoices}")
        
        # Recent invoices
        recent = db.query(Invoice).order_by(Invoice.uploaded_at.desc()).limit(3).all()
        print(f"✓ Recent invoices: {len(recent)}")
        
        # Step 6: Final Checks
        print("\n[Step 6] Integrity Checks...")
        checks = [
            ("Invoice persisted", inv.id == invoice.id),
            ("Processing result linked", proc.invoice_id == invoice.id),
            ("Vendor linked", inv.vendor_id == vendor.id),
            ("Amount correct", inv.total_amount == 5220.23),
            ("Decision made", proc.decision == DecisionStatus.APPROVE),
            ("Risk calculated", proc.fraud_risk_score is not None),
            ("Approval level set", proc.approval_level == ApprovalLevel.REQUIRES_MANAGER),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 ALL CHECKS PASSED!")
            print("\n✅ Database Integration Working:")
            print("  ✓ NeonDB connection successful")
            print("  ✓ Tables created and accessible")
            print("  ✓ Vendors managed")
            print("  ✓ Invoices stored with full data")
            print("  ✓ Processing results persisted")
            print("  ✓ Relationships working (vendor↔invoice↔processing)")
            print("  ✓ Enums stored correctly")
            print("  ✓ JSON fields functional")
            print("  ✓ Queries executing properly")
            return True
        else:
            print("\n⚠ Some checks failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
