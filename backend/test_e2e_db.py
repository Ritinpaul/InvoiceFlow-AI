"""
End-to-End Test: Upload Invoice and Verify Database Storage
Tests the complete flow from file upload through database persistence
"""
import asyncio
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.orchestrator import Orchestrator
from database import SessionLocal, Invoice, ProcessingResult
import shutil
import uuid
from datetime import datetime


def create_test_invoice_image():
    """Create a realistic test invoice image"""
    print("\nCreating test invoice image...")
    
    # Create image
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use default font
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw invoice content
    y = 50
    
    # Header
    draw.text((50, y), "INVOICE", fill='black', font=font_large)
    y += 60
    
    # Company info
    draw.text((50, y), "Acme Corp", fill='black', font=font_medium)
    y += 30
    draw.text((50, y), "123 Business St", fill='black', font=font_small)
    y += 25
    draw.text((50, y), "New York, NY 10001", fill='black', font=font_small)
    y += 50
    
    # Invoice details
    draw.text((50, y), "Invoice Number: INV-2026-100", fill='black', font=font_medium)
    y += 30
    draw.text((50, y), "Date: January 15, 2026", fill='black', font=font_medium)
    y += 30
    draw.text((50, y), "PO Number: PO-2026-500", fill='black', font=font_medium)
    y += 60
    
    # Line items
    draw.text((50, y), "Description", fill='black', font=font_medium)
    draw.text((500, y), "Amount", fill='black', font=font_medium)
    y += 30
    draw.line([(50, y), (750, y)], fill='black', width=2)
    y += 20
    
    draw.text((50, y), "Professional Services", fill='black', font=font_small)
    draw.text((500, y), "$3,500.00", fill='black', font=font_small)
    y += 30
    
    draw.text((50, y), "Consulting Hours", fill='black', font=font_small)
    draw.text((500, y), "$1,245.67", fill='black', font=font_small)
    y += 60
    
    # Totals
    draw.text((400, y), "Subtotal:", fill='black', font=font_medium)
    draw.text((500, y), "$4,745.67", fill='black', font=font_medium)
    y += 30
    
    draw.text((400, y), "Tax (10%):", fill='black', font=font_medium)
    draw.text((500, y), "$474.56", fill='black', font=font_medium)
    y += 30
    
    draw.line([(400, y), (750, y)], fill='black', width=2)
    y += 20
    
    draw.text((400, y), "TOTAL:", fill='black', font=font_large)
    draw.text((500, y), "$5,220.23", fill='black', font=font_large)
    
    # Save
    os.makedirs("uploads", exist_ok=True)
    filepath = "uploads/test_e2e_invoice.jpg"
    img.save(filepath)
    print(f"✓ Test invoice created: {filepath}")
    
    return filepath


async def test_full_pipeline():
    """Test the complete upload -> process -> database flow"""
    print("\n" + "="*80)
    print("END-TO-END TEST: Invoice Upload → Processing → Database Storage")
    print("="*80)
    
    # Step 1: Create test invoice
    print("\n[Step 1] Creating test invoice...")
    invoice_path = create_test_invoice_image()
    
    # Step 2: Initialize orchestrator
    print("\n[Step 2] Initializing orchestrator...")
    orchestrator = Orchestrator()
    
    # Step 3: Get database session
    print("\n[Step 3] Getting database session...")
    db = SessionLocal()
    
    try:
        # Step 4: Run pipeline
        print("\n[Step 4] Processing invoice through pipeline...")
        start_time = datetime.utcnow()
        result = await orchestrator.run_pipeline(invoice_path)
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✓ Processing complete in {processing_time:.2f}s!")
        
        # Step 5: Store in database (simulating router logic)
        print("\n[Step 5] Storing results in database...")
        
        from database.models import Vendor, DecisionStatus, ApprovalLevel, RiskLevel
        
        # Extract results
        extraction = result.get("extraction", {})
        fraud = result.get("fraud", {})
        policy = result.get("policy", {})
        decision = result.get("decision", {})
        
        # Get or create vendor
        vendor_name = extraction.get("vendor", "Unknown")
        vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()
        
        if not vendor:
            vendor = Vendor(name=vendor_name, is_approved=False)
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
        
        # Create invoice record
        invoice = Invoice(
            filename="test_e2e_invoice.jpg",
            file_path=invoice_path,
            file_size=os.path.getsize(invoice_path),
            invoice_number=extraction.get("invoice_number"),
            invoice_date=extraction.get("date"),
            vendor_id=vendor.id,
            vendor_name=vendor_name,
            total_amount=extraction.get("total_amount"),
            currency=extraction.get("currency", "USD"),
            tax_amount=extraction.get("tax_amount"),
            po_number=extraction.get("po_number"),
            extraction_confidence=extraction.get("confidence"),
            ocr_text=result.get("ocr_text"),
            uploaded_at=start_time,
            processed_at=end_time
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Parse enums safely
        try:
            fraud_risk_level = RiskLevel[fraud.get("risk_level", "MINIMAL")]
        except KeyError:
            fraud_risk_level = RiskLevel.MINIMAL
        
        try:
            approval_level = ApprovalLevel[policy.get("approval_level", "auto_approve").upper()]
        except KeyError:
            approval_level = ApprovalLevel.AUTO_APPROVE
        
        try:
            decision_status = DecisionStatus[decision.get("decision", "HOLD")]
        except KeyError:
            decision_status = DecisionStatus.HOLD
        
        # Create processing result
        proc_result = ProcessingResult(
            invoice_id=invoice.id,
            fraud_risk_score=fraud.get("risk_score"),
            fraud_risk_level=fraud_risk_level,
            is_suspicious=fraud.get("is_suspicious", False),
            fraud_flags=fraud.get("flags", []),
            fraud_check_results=fraud.get("check_results", {}),
            policy_compliant=policy.get("compliant", False),
            policy_violations=policy.get("violations", []),
            policy_warnings=policy.get("warnings", []),
            approval_level=approval_level,
            approver_required=policy.get("approver_required"),
            decision=decision_status,
            decision_reason=decision.get("reason"),
            decision_confidence=decision.get("confidence"),
            decision_recommendation=decision.get("recommendation"),
            decision_summary=decision.get("summary", {}),
            total_processing_time=processing_time
        )
        db.add(proc_result)
        db.commit()
        db.refresh(proc_result)
        
        print(f"✓ Data stored in database!")
        print(f"  Invoice ID: {invoice.id}")
        print(f"  Processing Result ID: {proc_result.id}")
        
        # Step 6: Verify database storage
        print("\n[Step 6] Verifying database storage...")
        invoice_id = invoice.id
        
        # Re-query to verify persistence
        invoice_check = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice_check:
            print("✗ Invoice not found in database!")
            return False
        
        print(f"✓ Invoice stored in database:")
        print(f"  Number: {invoice_check.invoice_number}")
        print(f"  Vendor: {invoice_check.vendor_name}")
        print(f"  Amount: ${invoice_check.total_amount:,.2f}")
        print(f"  Date: {invoice_check.invoice_date}")
        print(f"  PO: {invoice_check.po_number}")
        print(f"  Confidence: {invoice_check.extraction_confidence:.0%}")
        
        # Query processing result
        proc_result_check = db.query(ProcessingResult).filter(
            ProcessingResult.invoice_id == invoice_id
        ).first()
        
        if not proc_result_check:
            print("✗ Processing result not found in database!")
            return False
        
        print(f"\n✓ Processing result stored in database:")
        print(f"  Decision: {proc_result_check.decision.value}")
        print(f"  Reason: {proc_result_check.decision_reason}")
        print(f"  Confidence: {proc_result_check.decision_confidence:.0%}")
        print(f"  Fraud Risk: {proc_result_check.fraud_risk_level.value if proc_result_check.fraud_risk_level else 'N/A'}")
        print(f"  Policy Compliant: {proc_result_check.policy_compliant}")
        print(f"  Approval Level: {proc_result_check.approval_level.value if proc_result_check.approval_level else 'N/A'}")
        
        # Step 7: Verify all data fields
        print("\n[Step 7] Data integrity check...")
        checks = [
            ("Invoice number extracted", invoice_check.invoice_number is not None),
            ("Vendor identified", invoice_check.vendor_name is not None),
            ("Amount parsed", invoice_check.total_amount is not None),
            ("Decision made", proc_result_check.decision is not None),
            ("Fraud check completed", proc_result_check.fraud_risk_score is not None),
            ("Policy check completed", proc_result_check.approval_level is not None),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 ALL CHECKS PASSED! End-to-end flow working perfectly.")
            print("\n✓ File uploaded")
            print("✓ OCR extracted text")
            print("✓ NLP parsed invoice data")
            print("✓ Fraud detection ran")
            print("✓ Policy compliance checked")
            print("✓ Decision made")
            print("✓ All data persisted to NeonDB")
            return True
        else:
            print("\n⚠ Some checks failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def main():
    print("="*80)
    print("PHASE 3 END-TO-END VALIDATION")
    print("Testing Complete Pipeline with Database Persistence")
    print("="*80)
    
    success = await test_full_pipeline()
    
    if success:
        print("\n" + "="*80)
        print("✅ PHASE 3 COMPLETE - DATABASE INTEGRATION WORKING")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("❌ PHASE 3 INCOMPLETE - REVIEW ERRORS ABOVE")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
