"""
Phase 2 Testing: Enhanced Fraud, Policy, and Decision Agents
Tests all the new sophisticated logic added in Phase 2
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.fraud_agent import FraudAgent
from agents.policy_agent import PolicyAgent
from agents.decision_agent import DecisionAgent

# Generate current date for testing
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
OLD_DATE = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")

# Test scenarios
SCENARIOS = [
    {
        "name": "Normal Invoice - Should APPROVE",
        "data": {
            "invoice_number": "INV-2025-001",
            "date": CURRENT_DATE,
            "vendor": "Acme Corporation",
            "total_amount": 2345.67,  # Not round to avoid flags
            "currency": "USD",
            "po_number": "PO-12345",
            "tax_amount": 234.56,
            "confidence": 0.95
        },
        "expected": "APPROVE"
    },
    {
        "name": "High Amount Invoice - Should HOLD (CFO approval)",
        "data": {
            "invoice_number": "INV-2025-002",
            "date": CURRENT_DATE,
            "vendor": "Tech Solutions Inc",
            "total_amount": 75123.45,  # High but not round
            "currency": "USD",
            "po_number": "PO-67890",
            "tax_amount": 7512.34,
            "confidence": 0.92
        },
        "expected": "HOLD"
    },
    {
        "name": "Unapproved Vendor - Should REJECT",
        "data": {
            "invoice_number": "INV-2025-003",
            "date": CURRENT_DATE,
            "vendor": "Shady Business LLC",
            "total_amount": 1523.45,
            "currency": "USD",
            "po_number": "PO-11111",
            "tax_amount": 152.34,
            "confidence": 0.88
        },
        "expected": "REJECT"
    },
    {
        "name": "Missing PO Number - Should REJECT",
        "data": {
            "invoice_number": "INV-2025-004",
            "date": CURRENT_DATE,
            "vendor": "Acme Corporation",
            "total_amount": 3234.56,
            "currency": "USD",
            "po_number": "",
            "tax_amount": 323.45,
            "confidence": 0.90
        },
        "expected": "REJECT"
    },
    {
        "name": "Duplicate Invoice - Should REJECT",
        "data": {
            "invoice_number": "INV-2025-001",  # Same as first
            "date": CURRENT_DATE,
            "vendor": "Acme Corporation",
            "total_amount": 2345.67,
            "currency": "USD",
            "po_number": "PO-12345",
            "tax_amount": 234.56,
            "confidence": 0.95
        },
        "expected": "REJECT"
    },
    {
        "name": "Suspicious Round Amount - Should APPROVE (pending manager review)",
        "data": {
            "invoice_number": "INV-2025-005",
            "date": CURRENT_DATE,
            "vendor": "Office Supplies Co",
            "total_amount": 10000.00,  # Exactly $10k - suspicious but requires manager
            "currency": "USD",
            "po_number": "PO-22222",
            "tax_amount": 1000.00,
            "confidence": 0.85
        },
        "expected": "APPROVE"  # Approved pending manager, not HOLD
    },
    {
        "name": "Old Invoice Date - Should REJECT",
        "data": {
            "invoice_number": "INV-2024-099",
            "date": OLD_DATE,  # >90 days old
            "vendor": "Tech Solutions Inc",
            "total_amount": 1234.56,
            "currency": "USD",
            "po_number": "PO-33333",
            "tax_amount": 123.45,
            "confidence": 0.88
        },
        "expected": "REJECT"
    },
    {
        "name": "Small Amount - Should APPROVE (auto-approve)",
        "data": {
            "invoice_number": "INV-2025-006",
            "date": CURRENT_DATE,
            "vendor": "Acme Corporation",
            "total_amount": 456.78,
            "currency": "USD",
            "po_number": "",  # No PO needed for small amounts
            "tax_amount": 45.67,
            "confidence": 0.92
        },
        "expected": "APPROVE"
    }
]


async def test_scenario(fraud_agent, policy_agent, decision_agent, scenario):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"Testing: {scenario['name']}")
    print(f"{'='*80}")
    
    data = scenario['data']
    expected = scenario['expected']
    
    # Test fraud detection
    fraud_result = await fraud_agent.detect(data)
    print(f"\n[Fraud] Risk Score: {fraud_result['risk_score']:.2f} | Level: {fraud_result['risk_level']}")
    if fraud_result.get('flags'):
        print(f"[Fraud] Flags: {', '.join(fraud_result['flags'])}")
    
    # Test policy compliance
    policy_result = await policy_agent.check_compliance(data)
    print(f"\n[Policy] Compliant: {policy_result['compliant']} | Approval: {policy_result['approval_level']}")
    if policy_result.get('violations'):
        print(f"[Policy] Violations: {', '.join(policy_result['violations'])}")
    if policy_result.get('warnings'):
        print(f"[Policy] Warnings: {', '.join(policy_result['warnings'])}")
    
    # Test final decision
    decision_result = await decision_agent.decide(data, fraud_result, policy_result)
    print(f"\n[Decision] {decision_result['decision']} - {decision_result['reason']}")
    print(f"[Decision] Confidence: {decision_result['confidence']:.0%}")
    print(f"[Decision] Recommendation: {decision_result['recommendation']}")
    
    # Verify against expected
    actual = decision_result['decision']
    status = "✓ PASS" if actual == expected else f"✗ FAIL (expected {expected})"
    print(f"\n{status}")
    
    return actual == expected


async def main():
    print("="*80)
    print("PHASE 2 COMPREHENSIVE TESTING")
    print("Testing Enhanced Fraud, Policy, and Decision Agents")
    print("="*80)
    
    # Initialize agents
    fraud_agent = FraudAgent()
    policy_agent = PolicyAgent()
    decision_agent = DecisionAgent()
    
    # Run all scenarios
    results = []
    for scenario in SCENARIOS:
        passed = await test_scenario(fraud_agent, policy_agent, decision_agent, scenario)
        results.append({
            "name": scenario['name'],
            "passed": passed,
            "expected": scenario['expected']
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    for result in results:
        status = "✓" if result['passed'] else "✗"
        print(f"{status} {result['name']}")
    
    print(f"\n{passed_count}/{total_count} tests passed ({passed_count/total_count*100:.0f}%)")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Phase 2 implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed. Review the logic.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
