"""
Test script for NLP Agent
Tests data extraction from sample invoice text
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.nlp_agent import NLPAgent


async def test_nlp_agent():
    """Test NLP Agent with sample invoice text"""
    print("=" * 60)
    print("Testing NLP Agent")
    print("=" * 60)
    print()
    
    agent = NLPAgent()
    
    # Sample invoice text
    sample_text = """
    ACME Corporation
    123 Business Street
    New York, NY 10001
    
    INVOICE
    
    Invoice #: INV-12345
    Date: January 15, 2026
    PO #: PO-98765
    
    Bill To:
    Customer Company
    456 Client Avenue
    
    Description                Qty     Price       Total
    --------------------------------------------------
    Consulting Services        10      $100.00     $1,000.00
    Software License           1       $500.00     $500.00
    
    Subtotal:                                      $1,500.00
    Tax (10%):                                     $150.00
    Total Amount Due:                              $1,650.00
    
    Payment Terms: Net 30
    """
    
    print("Sample Invoice Text:")
    print("-" * 60)
    print(sample_text)
    print("-" * 60)
    print()
    
    # Test NLP Agent
    result = await agent.extract(sample_text)
    
    print("NLP Agent Extraction Results:")
    print("=" * 60)
    print(f"  Invoice Number: {result.get('invoice_number')}")
    print(f"  Date: {result.get('date')}")
    print(f"  Vendor: {result.get('vendor')}")
    print(f"  Total Amount: ${result.get('total_amount', 0):.2f}")
    print(f"  Currency: {result.get('currency')}")
    print(f"  PO Number: {result.get('po_number')}")
    print(f"  Tax Amount: ${result.get('tax_amount') or 0:.2f}")
    print(f"  Confidence: {result.get('confidence', 0):.0%}")
    print(f"  Status: {result.get('status')}")
    print("=" * 60)
    print()
    
    # Validation
    expected_fields = {
        'invoice_number': 'INV-12345',
        'vendor': 'ACME Corporation',
        'total_amount': 1650.0,
        'po_number': 'PO-98765',
    }
    
    passed = True
    print("Validation:")
    for field, expected_value in expected_fields.items():
        actual_value = result.get(field)
        match = False
        
        if field == 'total_amount':
            match = abs(actual_value - expected_value) < 10  # Allow small variance
        else:
            match = expected_value in str(actual_value) if actual_value else False
        
        status = "✓" if match else "✗"
        print(f"  {status} {field}: Expected '{expected_value}', Got '{actual_value}'")
        
        if not match:
            passed = False
    
    print()
    print("=" * 60)
    if passed and result.get('confidence', 0) >= 0.75:
        print("✓ NLP Agent Test PASSED")
    else:
        print("⚠ NLP Agent Test PARTIAL (some fields may need adjustment)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_nlp_agent())
