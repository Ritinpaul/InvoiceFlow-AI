import spacy
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

class NLPAgent:
    def __init__(self):
        self.name = "NLP Agent"
        print(f"[{self.name}] Loading NLP model...")
        self.nlp = spacy.load("en_core_web_sm")
        print(f"[{self.name}] NLP Ready")
        
        # Regex patterns for common invoice fields
        self.patterns = {
            'invoice_number': [
                r'Invoice\s*#[\s:]*([A-Z0-9-]+)',
                r'Invoice\s*Number[\s:]*([A-Z0-9-]+)',
                r'INV[\s#:-]*([A-Z0-9-]+)',
                r'#[\s:]*([A-Z0-9]{3,}[-]?[A-Z0-9]*)',
            ],
            'date': [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
            ],
            'amount': r'\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'total': [
                r'Total\s+Amount\s+Due[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:Grand\s+)?Total[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'Amount\s+Due[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'Balance\s+Due[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            ],
            'po_number': [
                r'PO\s*#[\s:]*([A-Z0-9-]+)',
                r'P\.?O\.?\s*Number[\s:]*([A-Z0-9-]+)',
                r'Purchase\s+Order[\s#:]*([A-Z0-9-]+)',
            ],
            'tax': r'Tax\s*\([^)]+\)[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        }
    
    async def extract(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw text into structured invoice data.
        Extracts: invoice number, date, vendor, amounts, line items
        """
        print(f"[{self.name}] Extracting structured data...")
        
        if not raw_text or len(raw_text.strip()) == 0:
            return self._empty_result("No text to process")
        
        # Extract all fields
        invoice_number = self._extract_invoice_number(raw_text)
        date = self._extract_date(raw_text)
        vendor = self._extract_vendor(raw_text)
        total_amount = self._extract_total(raw_text)
        currency = self._detect_currency(raw_text)
        po_number = self._extract_po_number(raw_text)
        tax_amount = self._extract_tax(raw_text)
        line_items = self._extract_line_items(raw_text)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            invoice_number, date, vendor, total_amount
        )
        
        result = {
            "invoice_number": invoice_number,
            "date": date,
            "vendor": vendor,
            "total_amount": total_amount,
            "currency": currency,
            "po_number": po_number,
            "tax_amount": tax_amount,
            "line_items": line_items,
            "confidence": confidence,
            "status": "success"
        }
        
        print(f"[{self.name}] Extraction complete: {invoice_number or 'Unknown'} from {vendor or 'Unknown'}")
        return result
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number using multiple patterns"""
        for pattern in self.patterns['invoice_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract and normalize date"""
        for pattern in self.patterns['date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(0)
                # Try to normalize date format
                try:
                    # Handle different date formats
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m-%d-%Y', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            parsed = datetime.strptime(date_str.strip(), fmt)
                            return parsed.strftime('%Y-%m-%d')
                        except:
                            continue
                except:
                    pass
                # Return as-is if parsing fails
                return date_str.strip()
        return None
    
    def _extract_vendor(self, text: str) -> Optional[str]:
        """Extract vendor name using NER and heuristics"""
        # Use spaCy NER to find organizations in first few lines
        lines = text.split('\n')[:15]  # Check first 15 lines
        first_section = '\n'.join(lines)
        
        doc = self.nlp(first_section)
        
        # Look for ORG entities, prioritizing those that appear early
        orgs = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Filter out common non-vendor words
                text_lower = ent.text.lower()
                if not any(word in text_lower for word in ['invoice', 'bill', 'statement', 'receipt', 
                                                            'description', 'qty', 'price', 'total',
                                                            'customer', 'client']):
                    orgs.append(ent.text)
        
        if orgs:
            # Return the first valid organization found
            return orgs[0].strip()
        
        # Fallback: Look for company name patterns in first few lines
        for line in lines[:5]:
            line = line.strip()
            # Look for lines with 2-4 capitalized words (likely company name)
            if len(line) > 5 and line[0].isupper():
                words = line.split()
                # Check if it looks like a company name (multiple capitalized words)
                cap_words = [w for w in words if w and w[0].isupper()]
                if 2 <= len(cap_words) <= 4 and len(words) <= 5:
                    # Additional check: not a common label
                    if not any(word.lower() in ['invoice', 'bill', 'statement', 'receipt', 'from', 'to'] 
                              for word in words):
                        return line
        
        return None
    
    def _extract_total(self, text: str) -> float:
        """Extract total amount"""
        # Try specific total patterns first
        for pattern in self.patterns['total']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '').replace('$', '').strip()
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        # Fallback: find largest amount in document (likely the total)
        amounts = re.findall(self.patterns['amount'], text)
        if amounts:
            cleaned_amounts = []
            for a in amounts:
                try:
                    cleaned = float(a.replace('$', '').replace(',', '').strip())
                    if cleaned > 0:
                        cleaned_amounts.append(cleaned)
                except:
                    continue
            
            if cleaned_amounts:
                # Return the largest amount (typically the total)
                return max(cleaned_amounts)
        
        return 0.0
    
    def _extract_po_number(self, text: str) -> Optional[str]:
        """Extract purchase order number"""
        for pattern in self.patterns['po_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_tax(self, text: str) -> Optional[float]:
        """Extract tax/VAT/GST amount"""
        match = re.search(self.patterns['tax'], text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except:
                pass
        return None
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract line items (simplified version).
        In production, this would be more sophisticated.
        """
        line_items = []
        # This is a placeholder - full implementation would parse item tables
        # For demo purposes, we'll return empty list
        return line_items
    
    def _detect_currency(self, text: str) -> str:
        """Detect currency from text"""
        if '$' in text:
            # Check for USD, CAD, AUD mentions
            if 'CAD' in text or 'Canadian' in text:
                return "CAD"
            elif 'AUD' in text or 'Australian' in text:
                return "AUD"
            return "USD"
        elif '€' in text or 'EUR' in text:
            return "EUR"
        elif '£' in text or 'GBP' in text:
            return "GBP"
        elif '¥' in text or 'JPY' in text:
            return "JPY"
        elif 'INR' in text or '₹' in text:
            return "INR"
        
        return "USD"  # Default
    
    def _calculate_confidence(self, inv_num, date, vendor, amount) -> float:
        """Calculate extraction confidence score based on found fields"""
        score = 0.0
        
        # Each critical field contributes 0.25
        if inv_num:
            score += 0.25
        if date:
            score += 0.25
        if vendor:
            score += 0.25
        if amount and amount > 0:
            score += 0.25
        
        return round(score, 2)
    
    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """Return empty result structure with error"""
        return {
            "invoice_number": None,
            "date": None,
            "vendor": None,
            "total_amount": 0.0,
            "currency": "USD",
            "po_number": None,
            "tax_amount": None,
            "line_items": [],
            "confidence": 0.0,
            "status": "error",
            "error": reason
        }
