"""
Database models for InvoiceFlow AI
Using SQLAlchemy ORM for PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class DecisionStatus(enum.Enum):
    """Enum for invoice approval decisions"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    HOLD = "HOLD"


class ApprovalLevel(enum.Enum):
    """Enum for approval levels"""
    AUTO_APPROVE = "auto_approve"
    REQUIRES_MANAGER = "requires_manager"
    REQUIRES_DIRECTOR = "requires_director"
    REQUIRES_CFO = "requires_cfo"
    REQUIRES_BOARD = "requires_board"


class RiskLevel(enum.Enum):
    """Enum for fraud risk levels"""
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Vendor(Base):
    """Vendor/Supplier information"""
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="vendor")
    
    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}', approved={self.is_approved})>"


class Invoice(Base):
    """Invoice information extracted from documents"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Extracted invoice data
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String(255), nullable=True, index=True)
    
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="USD", nullable=True)
    tax_amount = Column(Float, nullable=True)
    po_number = Column(String(100), nullable=True)
    
    # Processing metadata
    extraction_confidence = Column(Float, nullable=True)
    ocr_text = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    processing_result = relationship("ProcessingResult", back_populates="invoice", uselist=False)
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', vendor='{self.vendor_name}', amount={self.total_amount})>"


class ProcessingResult(Base):
    """Results from all agent processing"""
    __tablename__ = "processing_results"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, unique=True, index=True)
    
    # Fraud detection results
    fraud_risk_score = Column(Float, nullable=True)
    fraud_risk_level = Column(SQLEnum(RiskLevel), nullable=True)
    is_suspicious = Column(Boolean, default=False, nullable=False)
    fraud_flags = Column(JSON, nullable=True)  # List of fraud flags
    fraud_check_results = Column(JSON, nullable=True)  # Detailed check results
    
    # Policy compliance results
    policy_compliant = Column(Boolean, default=False, nullable=False)
    policy_violations = Column(JSON, nullable=True)  # List of violations
    policy_warnings = Column(JSON, nullable=True)  # List of warnings
    approval_level = Column(SQLEnum(ApprovalLevel), nullable=True)
    approver_required = Column(String(100), nullable=True)
    
    # Final decision
    decision = Column(SQLEnum(DecisionStatus), nullable=False, index=True)
    decision_reason = Column(Text, nullable=True)
    decision_confidence = Column(Float, nullable=True)
    decision_recommendation = Column(Text, nullable=True)
    decision_summary = Column(JSON, nullable=True)
    
    # Processing timeline
    vision_agent_time = Column(Float, nullable=True)  # Processing time in seconds
    nlp_agent_time = Column(Float, nullable=True)
    fraud_agent_time = Column(Float, nullable=True)
    policy_agent_time = Column(Float, nullable=True)
    decision_agent_time = Column(Float, nullable=True)
    total_processing_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="processing_result")
    
    def __repr__(self):
        return f"<ProcessingResult(id={self.id}, invoice_id={self.invoice_id}, decision={self.decision}, risk={self.fraud_risk_level})>"


class ProcessingLog(Base):
    """Detailed processing logs for debugging and auditing"""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    
    agent_name = Column(String(50), nullable=False)
    step_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # success, error, warning
    message = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Agent-specific data
    
    processing_time = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, agent='{self.agent_name}', status='{self.status}')>"
