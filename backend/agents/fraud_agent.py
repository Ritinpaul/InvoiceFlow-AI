from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

class FraudAgent:
    def __init__(self):
        self.name = "Fraud Agent"
        # In-memory cache for recent invoices (in production, use database)
        self.processed_invoices = []
        
        # Fraud detection thresholds
        self.thresholds = {
            'high_amount': 10000,
            'very_high_amount': 50000,
            'suspicious_frequency_same_day': 3,  # Same vendor, same day
            'suspicious_frequency_same_hour': 2,  # Same vendor, within 1 hour
            'round_amount_min': 1000,  # Round amounts above this are flagged
            'duplicate_check_days': 90,  # Check for duplicates in last 90 days
        }
    
    async def detect(self, extraction_data: dict) -> dict:
        """
        Analyze extracted data for fraud indicators with detailed flagging.
        
        Checks performed:
        1. Duplicate invoice detection
        2. Amount-based anomalies (high amounts, round amounts)
        3. Vendor frequency analysis
        4. Missing critical data
        5. Suspicious patterns (sequential invoices, etc.)
        """
        print(f"[{self.name}] Running comprehensive fraud detection...")
        
        flags = []
        risk_score = 0.0
        
        # Extract relevant fields
        invoice_number = extraction_data.get("invoice_number")
        vendor = extraction_data.get("vendor")
        amount = extraction_data.get("total_amount", 0)
        date = extraction_data.get("date")
        currency = extraction_data.get("currency", "USD")
        
        # Check 1: Duplicate invoice detection
        duplicate_check = self._check_duplicate(invoice_number, vendor)
        if duplicate_check['is_duplicate']:
            flags.append(f"Duplicate invoice: {duplicate_check['message']}")
            risk_score += 0.5  # High risk for duplicates
        
        # Check 2: Very high amount (potential fraud)
        if amount >= self.thresholds['very_high_amount']:
            flags.append(f"Very high amount: {currency} {amount:,.2f} (≥{self.thresholds['very_high_amount']:,})")
            risk_score += 0.3
        elif amount >= self.thresholds['high_amount']:
            flags.append(f"High amount: {currency} {amount:,.2f} (≥{self.thresholds['high_amount']:,})")
            risk_score += 0.2
        
        # Check 3: Suspicious round amounts
        if self._is_suspicious_round_amount(amount):
            flags.append(f"Suspicious round amount: {currency} {amount:,.2f}")
            risk_score += 0.15
        
        # Check 4: Vendor frequency analysis
        frequency_check = self._check_vendor_frequency(vendor, date)
        if frequency_check['suspicious']:
            flags.append(frequency_check['message'])
            risk_score += 0.25
        
        # Check 5: Missing critical data (potential incomplete/fraudulent invoice)
        missing_fields = self._check_missing_fields(extraction_data)
        if missing_fields:
            flags.append(f"Missing critical fields: {', '.join(missing_fields)}")
            risk_score += 0.2
        
        # Check 6: Invoice number pattern analysis
        pattern_check = self._check_invoice_pattern(invoice_number)
        if pattern_check['suspicious']:
            flags.append(pattern_check['message'])
            risk_score += 0.1
        
        # Check 7: Amount consistency (tax calculation check)
        if not self._check_amount_consistency(extraction_data):
            flags.append("Tax calculation appears inconsistent")
            risk_score += 0.1
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine if suspicious (threshold: 0.3)
        is_suspicious = risk_score >= 0.3
        
        # Store this invoice for future checks
        self._store_invoice(invoice_number, vendor, amount, date)
        
        result = {
            "is_suspicious": is_suspicious,
            "risk_score": round(risk_score, 2),
            "risk_level": self._get_risk_level(risk_score),
            "flags": flags if flags else ["No fraud indicators detected"],
            "checks_performed": 7,
            "details": {
                "duplicate_check": duplicate_check,
                "frequency_check": frequency_check,
                "pattern_check": pattern_check,
            }
        }
        
        risk_emoji = "🚨" if is_suspicious else "✓"
        print(f"[{self.name}] {risk_emoji} Risk Score: {risk_score:.2f} ({result['risk_level']}) | Flags: {len(flags)}")
        
        return result
    
    def _check_duplicate(self, invoice_number: str, vendor: str) -> dict:
        """Check if invoice number already exists for this vendor"""
        if not invoice_number:
            return {"is_duplicate": False, "message": "No invoice number to check"}
        
        # Check in recent invoices
        for inv in self.processed_invoices:
            if inv['invoice_number'] == invoice_number:
                if inv['vendor'] == vendor:
                    return {
                        "is_duplicate": True,
                        "message": f"Invoice #{invoice_number} already processed for {vendor}"
                    }
                else:
                    # Same invoice number, different vendor (suspicious but possible)
                    return {
                        "is_duplicate": False,
                        "message": f"Invoice #{invoice_number} exists for different vendor"
                    }
        
        return {"is_duplicate": False, "message": "No duplicate found"}
    
    def _is_suspicious_round_amount(self, amount: float) -> bool:
        """Check if amount is suspiciously round (e.g., exactly $5000.00)"""
        if amount < self.thresholds['round_amount_min']:
            return False
        
        # Check if amount is a perfect round number
        if amount % 100 == 0 and amount >= 1000:
            # Very round amounts like 5000, 10000 can be suspicious
            return True
        
        return False
    
    def _check_vendor_frequency(self, vendor: str, date: str) -> dict:
        """Check if too many invoices from same vendor in short time"""
        if not vendor:
            return {"suspicious": False, "message": "No vendor to check"}
        
        now = datetime.now()
        today_count = 0
        recent_count = 0
        
        for inv in self.processed_invoices:
            if inv['vendor'] == vendor:
                # Check if processed today
                time_diff = (now - inv['timestamp']).total_seconds()
                
                if time_diff < 86400:  # Within 24 hours
                    today_count += 1
                
                if time_diff < 3600:  # Within 1 hour
                    recent_count += 1
        
        # High frequency in short time is suspicious
        if recent_count >= self.thresholds['suspicious_frequency_same_hour']:
            return {
                "suspicious": True,
                "message": f"Multiple invoices from {vendor} within 1 hour ({recent_count + 1} total)"
            }
        
        if today_count >= self.thresholds['suspicious_frequency_same_day']:
            return {
                "suspicious": True,
                "message": f"Multiple invoices from {vendor} today ({today_count + 1} total)"
            }
        
        return {"suspicious": False, "message": "Normal frequency"}
    
    def _check_missing_fields(self, data: dict) -> List[str]:
        """Check for missing critical fields"""
        critical_fields = ['invoice_number', 'vendor', 'date', 'total_amount']
        missing = []
        
        for field in critical_fields:
            value = data.get(field)
            if not value or (isinstance(value, (int, float)) and value <= 0):
                missing.append(field)
        
        return missing
    
    def _check_invoice_pattern(self, invoice_number: str) -> dict:
        """Analyze invoice number for suspicious patterns"""
        if not invoice_number:
            return {"suspicious": False, "message": "No invoice number"}
        
        # Check for sequential numbers that might indicate fabrication
        # This is a simplified check - production would be more sophisticated
        
        # Check if invoice number is suspiciously simple (e.g., "123", "001")
        if invoice_number.isdigit() and len(invoice_number) <= 3:
            return {
                "suspicious": True,
                "message": f"Suspiciously simple invoice number: {invoice_number}"
            }
        
        # Check for all zeros or ones
        if re.match(r'^[0]+$', invoice_number) or re.match(r'^[1]+$', invoice_number):
            return {
                "suspicious": True,
                "message": f"Invalid invoice number pattern: {invoice_number}"
            }
        
        return {"suspicious": False, "message": "Normal pattern"}
    
    def _check_amount_consistency(self, data: dict) -> bool:
        """Check if tax calculation is consistent with total"""
        total = data.get("total_amount", 0)
        tax = data.get("tax_amount")
        
        if not tax or tax <= 0:
            # No tax info to validate
            return True
        
        # Estimate if tax percentage is reasonable (5-20%)
        if total > 0:
            tax_percentage = (tax / total) * 100
            
            # Tax should typically be between 5% and 20%
            if tax_percentage < 3 or tax_percentage > 25:
                return False  # Suspicious tax calculation
        
        return True
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _store_invoice(self, invoice_number: str, vendor: str, amount: float, date: str):
        """Store invoice in cache for future fraud checks"""
        self.processed_invoices.append({
            'invoice_number': invoice_number,
            'vendor': vendor,
            'amount': amount,
            'date': date,
            'timestamp': datetime.now()
        })
        
        # Keep only last 100 invoices in memory (in production, use database)
        if len(self.processed_invoices) > 100:
            self.processed_invoices = self.processed_invoices[-100:]
