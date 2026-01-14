from typing import Dict, List, Optional
import re

class PolicyAgent:
    def __init__(self):
        self.name = "Policy Agent"
        
        # Company policies (in production, load from database/config)
        self.approved_vendors = [
            "Acme Corp", "ACME Corporation", "ACMECorporation",
            "TechSolutions Inc", "Tech Solutions Inc",
            "OfficeSupplies Co", "Office Supplies Co",
            "GlobalServices Ltd", "Global Services Ltd",
            "DataSystems Inc", "Data Systems Inc",
            "CloudTech Solutions", "Cloud Tech Solutions",
            "Microsoft", "Google", "Amazon", "Adobe"
        ]
        
        # Spending limits by approval level
        self.spending_limits = {
            'auto_approve': 5000,      # Can auto-approve up to $5k
            'requires_manager': 10000,  # $5k-$10k needs manager
            'requires_director': 25000, # $10k-$25k needs director
            'requires_cfo': 50000,      # $25k-$50k needs CFO
            'requires_board': float('inf')  # Over $50k needs board approval
        }
        
        # Required fields for different invoice types
        self.required_fields = {
            'basic': ['invoice_number', 'vendor', 'date', 'total_amount'],
            'standard': ['invoice_number', 'vendor', 'date', 'total_amount', 'currency'],
            'international': ['invoice_number', 'vendor', 'date', 'total_amount', 'currency', 'tax_amount']
        }
        
        # Business rules
        self.rules = {
            'max_invoice_age_days': 90,  # Invoice shouldn't be older than 90 days
            'min_amount': 0.01,  # Minimum invoice amount
            'max_amount': 100000,  # Maximum single invoice amount
            'require_po_above': 1000,  # PO number required for invoices above $1000
        }
    
    async def check_compliance(self, extraction_data: dict) -> dict:
        """
        Verify compliance with all company policies.
        
        Checks performed:
        1. Required fields validation
        2. Approved vendor verification
        3. Spending limits and approval levels
        4. Amount validation (min/max)
        5. PO number requirements
        6. Invoice date validation
        7. Currency validation
        """
        print(f"[{self.name}] Running comprehensive policy compliance checks...")
        
        violations = []
        warnings = []
        
        # Extract relevant fields
        vendor = extraction_data.get("vendor", "")
        amount = extraction_data.get("total_amount", 0)
        invoice_number = extraction_data.get("invoice_number")
        date = extraction_data.get("date")
        po_number = extraction_data.get("po_number")
        currency = extraction_data.get("currency", "USD")
        
        # Check 1: Required fields validation
        missing_fields = self._check_required_fields(extraction_data)
        if missing_fields:
            violations.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check 2: Approved vendor verification
        vendor_check = self._check_vendor_approval(vendor)
        if not vendor_check['approved']:
            violations.append(vendor_check['message'])
        elif vendor_check.get('warning'):
            warnings.append(vendor_check['warning'])
        
        # Check 3: Spending limits and approval requirements
        approval_check = self._check_spending_limit(amount)
        if approval_check['level'] == 'auto_approve':
            # No special approval needed
            pass
        else:
            warnings.append(f"Amount ${amount:,.2f} requires {approval_check['approver']} approval")
        
        # Check 4: Amount validation
        amount_check = self._validate_amount(amount)
        if not amount_check['valid']:
            violations.append(amount_check['message'])
        
        # Check 5: PO number requirements
        po_check = self._check_po_requirement(amount, po_number)
        if not po_check['compliant']:
            violations.append(po_check['message'])
        
        # Check 6: Invoice number format validation
        invoice_check = self._validate_invoice_format(invoice_number)
        if not invoice_check['valid']:
            warnings.append(invoice_check['message'])
        
        # Check 7: Invoice date validation
        date_check = self._validate_invoice_date(date)
        if not date_check['valid']:
            violations.append(date_check['message'])
        elif date_check.get('warning'):
            warnings.append(date_check['warning'])
        
        # Check 8: Currency validation
        if currency not in ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'INR']:
            warnings.append(f"Unusual currency: {currency} - may need additional review")
        
        # Determine overall compliance
        compliant = len(violations) == 0
        
        result = {
            "compliant": compliant,
            "violations": violations if violations else [],
            "warnings": warnings if warnings else [],
            "approval_level": approval_check['level'],
            "approver_required": approval_check['approver'],
            "checks_performed": 8,
            "details": {
                "vendor_check": vendor_check,
                "approval_check": approval_check,
                "amount_check": amount_check,
                "po_check": po_check,
                "date_check": date_check,
            }
        }
        
        status_emoji = "✓" if compliant else "✗"
        print(f"[{self.name}] {status_emoji} Compliant: {compliant} | Violations: {len(violations)} | Warnings: {len(warnings)}")
        
        return result
    
    def _check_required_fields(self, data: dict) -> List[str]:
        """Check if all required fields are present"""
        # Determine which field set to use based on amount
        amount = data.get("total_amount", 0)
        
        if amount > 10000:
            required = self.required_fields['international']
        elif amount > 1000:
            required = self.required_fields['standard']
        else:
            required = self.required_fields['basic']
        
        missing = []
        for field in required:
            value = data.get(field)
            if not value or (isinstance(value, (int, float)) and value <= 0):
                missing.append(field)
        
        return missing
    
    def _check_vendor_approval(self, vendor: str) -> dict:
        """Check if vendor is in approved list"""
        if not vendor:
            return {
                "approved": False,
                "message": "No vendor name provided"
            }
        
        vendor_lower = vendor.lower().strip()
        
        # Check exact matches first
        for approved in self.approved_vendors:
            if vendor.strip() == approved:
                return {
                    "approved": True,
                    "message": f"Vendor '{vendor}' is approved",
                    "match_type": "exact"
                }
        
        # Check fuzzy matches (contains or is contained)
        for approved in self.approved_vendors:
            approved_lower = approved.lower()
            if approved_lower in vendor_lower or vendor_lower in approved_lower:
                return {
                    "approved": True,
                    "message": f"Vendor '{vendor}' matched approved vendor '{approved}'",
                    "match_type": "fuzzy",
                    "warning": f"Vendor name '{vendor}' is similar to '{approved}' - verify exact match"
                }
        
        # Not found in approved list
        return {
            "approved": False,
            "message": f"Vendor '{vendor}' is not in approved vendor list",
            "suggestion": "Add vendor to approved list or request manual approval"
        }
    
    def _check_spending_limit(self, amount: float) -> dict:
        """Determine approval level based on amount"""
        if amount <= self.spending_limits['auto_approve']:
            return {
                "level": "auto_approve",
                "approver": "System",
                "message": "Within auto-approval limit"
            }
        elif amount <= self.spending_limits['requires_manager']:
            return {
                "level": "requires_manager",
                "approver": "Manager",
                "message": f"Amount ${amount:,.2f} requires manager approval"
            }
        elif amount <= self.spending_limits['requires_director']:
            return {
                "level": "requires_director",
                "approver": "Director",
                "message": f"Amount ${amount:,.2f} requires director approval"
            }
        elif amount <= self.spending_limits['requires_cfo']:
            return {
                "level": "requires_cfo",
                "approver": "CFO",
                "message": f"Amount ${amount:,.2f} requires CFO approval"
            }
        else:
            return {
                "level": "requires_board",
                "approver": "Board of Directors",
                "message": f"Amount ${amount:,.2f} requires board approval"
            }
    
    def _validate_amount(self, amount: float) -> dict:
        """Validate invoice amount is within acceptable range"""
        if amount < self.rules['min_amount']:
            return {
                "valid": False,
                "message": f"Amount ${amount:.2f} is below minimum (${self.rules['min_amount']})"
            }
        
        if amount > self.rules['max_amount']:
            return {
                "valid": False,
                "message": f"Amount ${amount:,.2f} exceeds maximum allowed (${self.rules['max_amount']:,})"
            }
        
        return {
            "valid": True,
            "message": "Amount is within acceptable range"
        }
    
    def _check_po_requirement(self, amount: float, po_number: Optional[str]) -> dict:
        """Check if PO number is required and present"""
        if amount >= self.rules['require_po_above']:
            if not po_number:
                return {
                    "compliant": False,
                    "message": f"PO number required for invoices ≥${self.rules['require_po_above']:,} (amount: ${amount:,.2f})"
                }
        
        return {
            "compliant": True,
            "message": "PO requirements met"
        }
    
    def _validate_invoice_format(self, invoice_number: str) -> dict:
        """Validate invoice number format"""
        if not invoice_number:
            return {
                "valid": False,
                "message": "Invoice number is missing"
            }
        
        # Check minimum length
        if len(invoice_number) < 3:
            return {
                "valid": False,
                "message": f"Invoice number '{invoice_number}' is too short (minimum 3 characters)"
            }
        
        # Check for valid characters (alphanumeric, dash, hash)
        if not re.match(r'^[A-Z0-9#-]+$', invoice_number, re.IGNORECASE):
            return {
                "valid": True,  # Valid but warning
                "message": f"Invoice number '{invoice_number}' contains unusual characters"
            }
        
        return {
            "valid": True,
            "message": "Invoice number format is valid"
        }
    
    def _validate_invoice_date(self, date: str) -> dict:
        """Validate invoice date is not too old or in the future"""
        if not date:
            return {
                "valid": False,
                "message": "Invoice date is missing"
            }
        
        # Try to parse date
        from datetime import datetime, timedelta
        
        try:
            # Handle different date formats
            invoice_date = None
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    invoice_date = datetime.strptime(date, fmt)
                    break
                except:
                    continue
            
            if not invoice_date:
                return {
                    "valid": True,  # Can't validate, but don't block
                    "warning": f"Invoice date '{date}' format could not be validated"
                }
            
            today = datetime.now()
            age_days = (today - invoice_date).days
            
            # Check if invoice is too old
            if age_days > self.rules['max_invoice_age_days']:
                return {
                    "valid": False,
                    "message": f"Invoice date {date} is {age_days} days old (max: {self.rules['max_invoice_age_days']} days)"
                }
            
            # Check if invoice is in the future
            if age_days < -1:  # Allow 1 day grace period
                return {
                    "valid": False,
                    "message": f"Invoice date {date} is in the future"
                }
            
            # Warn if invoice is getting old
            if age_days > 30:
                return {
                    "valid": True,
                    "warning": f"Invoice is {age_days} days old - verify it hasn't been paid already"
                }
            
            return {
                "valid": True,
                "message": f"Invoice date is valid ({age_days} days old)"
            }
            
        except Exception as e:
            return {
                "valid": True,  # Don't block on parse errors
                "warning": f"Could not validate invoice date: {str(e)}"
            }
