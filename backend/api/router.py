from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.orchestrator.orchestrator import Orchestrator
from backend.database import get_db, Invoice, Vendor, ProcessingResult, ProcessingLog
from backend.database.models import DecisionStatus, ApprovalLevel, RiskLevel
from backend.api.websocket import manager, ProgressTracker
import shutil
import os
import uuid
from datetime import datetime
from typing import List, Optional

router = APIRouter()
orchestrator = Orchestrator()

# Temporary storage for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time progress updates
    """
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)


@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    session_id: Optional[str] = None
):
    """
    Upload and process an invoice
    Stores results in database
    Supports real-time progress updates via WebSocket if session_id provided
    """
    # Validate file type
    allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 10MB, your file: {file_size / 1024 / 1024:.2f}MB"
        )
    
    # Save file locally
    try:
        file_id = str(uuid.uuid4())
        file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create progress tracker if session_id provided
    progress_tracker = None
    if session_id:
        progress_tracker = ProgressTracker(session_id)
    
    # Run processing pipeline with progress tracking
    try:
        start_time = datetime.utcnow()
        result = await orchestrator.run_pipeline(file_path, progress_tracker=progress_tracker)
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
    except Exception as e:
        # Clean up file on processing error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Invoice processing failed: {str(e)}"
        )
    
    # Extract results
    extraction = result.get("extraction", {})
    fraud = result.get("fraud", {})
    policy = result.get("policy", {})
    decision = result.get("decision", {})
    
    # Get or create vendor
    vendor_name = extraction.get("vendor", "Unknown")
    vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()
    
    if not vendor:
        # Create new vendor (not approved by default)
        vendor = Vendor(name=vendor_name, is_approved=False)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
    
    # Create invoice record
    invoice = Invoice(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
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
    processing_result = ProcessingResult(
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
    db.add(processing_result)
    db.commit()
    db.refresh(processing_result)
    
    # Return response with OCR text included
    return {
        "status": "processed",
        "invoice_id": invoice.id,
        "file_id": file_id,
        "filename": file.filename,
        "decision": decision_status.value,
        "result": {
            "extraction": {
                **extraction,
                "raw_text": result.get("ocr_text", "")  # Include OCR text
            },
            "fraud": fraud,
            "policy": policy,
            "decision": decision,
            "processing_time": processing_time
        }
    }


@router.get("/invoices")
def list_invoices(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    decision: Optional[str] = Query(None, description="Filter by decision: APPROVE, REJECT, HOLD")
):
    """
    List all invoices with pagination and filtering
    """
    query = db.query(Invoice).order_by(Invoice.uploaded_at.desc())
    
    # Filter by decision if provided
    if decision:
        try:
            decision_status = DecisionStatus[decision.upper()]
            query = query.join(ProcessingResult).filter(ProcessingResult.decision == decision_status)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid decision status: {decision}")
    
    total = query.count()
    invoices = query.offset(offset).limit(limit).all()
    
    # Build response with decision status from processing results
    invoice_list = []
    for inv in invoices:
        # Get processing result for this invoice
        proc_result = db.query(ProcessingResult).filter(ProcessingResult.invoice_id == inv.id).first()
        
        invoice_list.append({
            "id": inv.id,
            "filename": inv.filename,
            "invoice_number": inv.invoice_number,
            "vendor_name": inv.vendor_name,
            "total_amount": inv.total_amount,
            "currency": inv.currency,
            "uploaded_at": inv.uploaded_at.isoformat() if inv.uploaded_at else None,
            "processed_at": inv.processed_at.isoformat() if inv.processed_at else None,
            "decision": proc_result.decision.value if proc_result and proc_result.decision else None
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "invoices": invoice_list
    }


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Get detailed invoice information including processing results
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    
    # Get processing result
    result = db.query(ProcessingResult).filter(ProcessingResult.invoice_id == invoice_id).first()
    
    return {
        "invoice": {
            "id": invoice.id,
            "filename": invoice.filename,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "vendor_name": invoice.vendor_name,
            "vendor_id": invoice.vendor_id,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "tax_amount": invoice.tax_amount,
            "po_number": invoice.po_number,
            "extraction_confidence": invoice.extraction_confidence,
            "uploaded_at": invoice.uploaded_at.isoformat() if invoice.uploaded_at else None,
            "processed_at": invoice.processed_at.isoformat() if invoice.processed_at else None,
        },
        "processing": {
            "decision": result.decision.value if result else None,
            "decision_reason": result.decision_reason if result else None,
            "decision_confidence": result.decision_confidence if result else None,
            "decision_recommendation": result.decision_recommendation if result else None,
            "fraud_risk_score": result.fraud_risk_score if result else None,
            "fraud_risk_level": result.fraud_risk_level.value if result and result.fraud_risk_level else None,
            "is_suspicious": result.is_suspicious if result else False,
            "fraud_flags": result.fraud_flags if result else [],
            "policy_compliant": result.policy_compliant if result else False,
            "policy_violations": result.policy_violations if result else [],
            "policy_warnings": result.policy_warnings if result else [],
            "approval_level": result.approval_level.value if result and result.approval_level else None,
            "approver_required": result.approver_required if result else None,
            "total_processing_time": result.total_processing_time if result else None,
        } if result else None
    }


@router.get("/vendors")
def list_vendors(db: Session = Depends(get_db), approved_only: bool = Query(False)):
    """
    List all vendors
    """
    query = db.query(Vendor)
    
    if approved_only:
        query = query.filter(Vendor.is_approved == True)
    
    vendors = query.order_by(Vendor.name).all()
    
    return {
        "total": len(vendors),
        "vendors": [
            {
                "id": v.id,
                "name": v.name,
                "is_approved": v.is_approved,
                "email": v.email,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in vendors
        ]
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics
    """
    total_invoices = db.query(Invoice).count()
    
    # Count by decision
    approved = db.query(ProcessingResult).filter(ProcessingResult.decision == DecisionStatus.APPROVE).count()
    rejected = db.query(ProcessingResult).filter(ProcessingResult.decision == DecisionStatus.REJECT).count()
    on_hold = db.query(ProcessingResult).filter(ProcessingResult.decision == DecisionStatus.HOLD).count()
    
    # Count suspicious invoices
    suspicious = db.query(ProcessingResult).filter(ProcessingResult.is_suspicious == True).count()
    
    # Count by approval level
    auto_approve = db.query(ProcessingResult).filter(ProcessingResult.approval_level == ApprovalLevel.AUTO_APPROVE).count()
    
    return {
        "total_invoices": total_invoices,
        "decisions": {
            "approved": approved,
            "rejected": rejected,
            "on_hold": on_hold
        },
        "fraud": {
            "suspicious": suspicious,
            "clean": total_invoices - suspicious
        },
        "approval_levels": {
            "auto_approve": auto_approve,
            "requires_review": total_invoices - auto_approve
        }
    }

