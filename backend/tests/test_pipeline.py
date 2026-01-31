"""
End-to-End Pipeline Test
Tests the complete invoice processing flow through all agents
"""
import asyncio
import sys
import os

# Add parent directory to path
# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.orchestrator import Orchestrator
from PIL import Image, ImageDraw, ImageFont


async def test_full_pipeline():
    """Test complete pipeline from file upload to final decision"""
    print("=" * 70)
    print("END-TO-END PIPELINE TEST")
    print("=" * 70)
    print()
    
    # Create a test invoice image
    test_file = "test_full_invoice.png"
    create_test_invoice(test_file)
    print(f"✓ Created test invoice: {test_file}")
    print()
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    print("✓ Orchestrator initialized")
    print()
    
    # Run the full pipeline
    print("Running complete pipeline...")
    print("-" * 70)
    result = await orchestrator.run_pipeline(test_file)
    print("-" * 70)
    print()
    
    # Display results
    print("PIPELINE RESULTS")
    print("=" * 70)
    
    print("\n1. EXTRACTION (NLP Agent):")
    extraction = result.get('extraction', {})
    print(f"   Invoice #: {extraction.get('invoice_number')}")
    print(f"   Vendor: {extraction.get('vendor')}")
    print(f"   Date: {extraction.get('date')}")
    print(f"   Amount: ${extraction.get('total_amount', 0):.2f} {extraction.get('currency')}")
    print(f"   Confidence: {extraction.get('confidence', 0):.0%}")
    
    print("\n2. FRAUD CHECK:")
    fraud = result.get('fraud_check', {})
    print(f"   Suspicious: {fraud.get('is_suspicious')}")
    print(f"   Risk Score: {fraud.get('risk_score', 0):.2f}")
    print(f"   Flags: {', '.join(fraud.get('flags', []))}")
    
    print("\n3. POLICY CHECK:")
    policy = result.get('policy_check', {})
    print(f"   Compliant: {policy.get('compliant')}")
    print(f"   Violations: {', '.join(policy.get('violations', [])) or 'None'}")
    
    print("\n4. FINAL DECISION:")
    decision = result.get('final_decision', {})
    print(f"   Decision: {decision.get('decision')}")
    print(f"   Reason: {decision.get('reason')}")
    print(f"   Confidence: {decision.get('confidence', 0):.0%}")
    
    print()
    print("=" * 70)
    
    # Validation
    success = (
        extraction.get('confidence', 0) > 0 and
        'decision' in decision and
        decision.get('decision') in ['APPROVE', 'REJECT', 'HOLD']
    )
    
    if success:
        print("✓ END-TO-END TEST PASSED")
        print()
        print("All agents executed successfully!")
        print("The multi-agent pipeline is working correctly.")
    else:
        print("✗ END-TO-END TEST FAILED")
        print("Some agents did not execute properly.")
    
    print("=" * 70)
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n✓ Cleaned up test file")
    
    return success


def create_test_invoice(filename: str):
    """Create a sample invoice image for testing"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    invoice_text = [
        "",
        "    ACME Corporation",
        "    123 Business Street",
        "    New York, NY 10001",
        "",
        "    INVOICE",
        "",
        "    Invoice Number: INV-12345",
        "    Date: 01/15/2026",
        "    PO Number: PO-98765",
        "",
        "    Bill To:",
        "    Customer Company Inc",
        "",
        "    Description              Amount",
        "    Consulting Services      $800.00",
        "    Software License         $450.00",
        "",
        "    Subtotal:              $1,250.00",
        "    Tax (10%):              $125.00",
        "    Total Amount:          $1,375.00",
        "",
        "    Payment Terms: Net 30",
    ]
    
    y_pos = 30
    for line in invoice_text:
        draw.text((40, y_pos), line, fill='black')
        y_pos += 25
    
    img.save(filename)


if __name__ == "__main__":
    result = asyncio.run(test_full_pipeline())
    sys.exit(0 if result else 1)
