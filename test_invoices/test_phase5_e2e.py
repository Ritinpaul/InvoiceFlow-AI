"""
Phase 5: Comprehensive End-to-End Testing
Tests all 5 scenarios with real invoice images and validates entire pipeline
"""

import asyncio
import os
import sys
import time
from pathlib import Path
import aiohttp
import json

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Test configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
TEST_INVOICES_DIR = Path(__file__).parent.parent / "test_invoices"

# Expected outcomes for each scenario
EXPECTED_OUTCOMES = {
    "scenario1_approved_low_risk.png": {
        "vendor_match": "TechSupplies",
        "amount_range": (1200, 1300),
        "fraud_risk": "LOW",
        "expected_decision": "APPROVED",
        "description": "Normal approved invoice"
    },
    "scenario2_high_risk_fraud.png": {
        "vendor_match": "Unknown",
        "amount_range": (99000, 100000),
        "fraud_risk": "HIGH",
        "expected_decision": "REJECTED",
        "description": "High fraud risk invoice"
    },
    "scenario3_policy_violation.png": {
        "vendor_match": "OfficeDepot",
        "amount_range": (15000, 16000),
        "fraud_risk": "MEDIUM",
        "expected_decision": "REJECTED",  # Exceeds $15k limit
        "description": "Policy violation - exceeds limit"
    },
    "scenario4_duplicate_invoice.png": {
        "vendor_match": "TechSupplies",
        "amount_range": (1200, 1300),
        "fraud_risk": "HIGH",  # Duplicate should be flagged
        "expected_decision": "REJECTED",
        "description": "Duplicate invoice detection"
    },
    "scenario5_requires_approval.png": {
        "vendor_match": "Amazon",
        "amount_range": (8000, 9000),
        "fraud_risk": "LOW",
        "expected_decision": "ON_HOLD",  # Requires manager approval
        "description": "Requires manager approval"
    }
}

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")

def print_test(name, status, details=""):
    """Print test result"""
    if status == "PASS":
        symbol = "✅"
        color = Colors.GREEN
    elif status == "FAIL":
        symbol = "❌"
        color = Colors.RED
    elif status == "WARN":
        symbol = "⚠️ "
        color = Colors.YELLOW
    else:
        symbol = "ℹ️ "
        color = Colors.BLUE
    
    print(f"{symbol} {color}{name}{Colors.END}")
    if details:
        print(f"   {details}")

async def test_scenario(session, scenario_file, expected):
    """Test a single invoice scenario"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📄 Testing: {scenario_file}{Colors.END}")
    print(f"   Expected: {expected['description']}")
    
    file_path = TEST_INVOICES_DIR / scenario_file
    
    if not file_path.exists():
        print_test(f"File Check", "FAIL", f"File not found: {file_path}")
        return False
    
    # Upload invoice
    try:
        with open(file_path, 'rb') as f:
            form_data = aiohttp.FormData()
            form_data.add_field('file', f, filename=scenario_file, content_type='image/png')
            
            async with session.post(f"{API_URL}/upload", data=form_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print_test("Upload", "FAIL", f"HTTP {response.status}: {error_text}")
                    return False
                
                result = await response.json()
                print_test("Upload", "PASS", "Invoice uploaded successfully")
    
    except Exception as e:
        print_test("Upload", "FAIL", str(e))
        return False
    
    # Validate results - API returns nested under "result" key
    passed_tests = 0
    total_tests = 0
    
    # Extract nested result data
    result_data = result.get("result", {})
    extraction = result_data.get("extraction", {})
    fraud = result_data.get("fraud", {})
    policy = result_data.get("policy", {})
    decision_data = result_data.get("decision", {})
    
    # Check Vision/OCR - check if text was extracted
    total_tests += 1
    ocr_text = extraction.get("raw_text", "")
    if ocr_text and len(ocr_text) > 0:
        print_test("Vision Agent", "PASS", f"Extracted {len(ocr_text)} characters")
        passed_tests += 1
    else:
        print_test("Vision Agent", "FAIL", "No text extracted")
    
    # Check NLP Agent (extraction results)
    total_tests += 1
    if extraction.get("invoice_number"):
        vendor = extraction.get("vendor", "")
        amount = extraction.get("total_amount", 0)
        print_test("NLP Agent", "PASS", 
                  f"Vendor: {vendor}, Amount: ${amount:,.2f}, Invoice: {extraction.get('invoice_number')}")
        passed_tests += 1
        
        # Validate vendor name contains expected text
        total_tests += 1
        if expected["vendor_match"].lower() in vendor.lower():
            print_test("Vendor Match", "PASS", f"'{vendor}' contains '{expected['vendor_match']}'")
            passed_tests += 1
        else:
            print_test("Vendor Match", "WARN", f"Expected '{expected['vendor_match']}' in '{vendor}'")
        
        # Validate amount is in expected range
        total_tests += 1
        min_amt, max_amt = expected["amount_range"]
        if min_amt <= amount <= max_amt:
            print_test("Amount Range", "PASS", f"${amount:,.2f} in range ${min_amt:,.2f}-${max_amt:,.2f}")
            passed_tests += 1
        else:
            print_test("Amount Range", "WARN", f"${amount:,.2f} outside range ${min_amt:,.2f}-${max_amt:,.2f}")
    else:
        print_test("NLP Agent", "FAIL", "No invoice data extracted")
    
    # Check Fraud Agent
    total_tests += 1
    if fraud.get("risk_level"):
        risk_level = fraud.get("risk_level")
        risk_score = fraud.get("risk_score", 0)
        print_test("Fraud Agent", "PASS", 
                  f"Risk: {risk_level} (Score: {risk_score:.2f})")
        passed_tests += 1
        
        # Validate risk level matches expected
        total_tests += 1
        if risk_level == expected["fraud_risk"]:
            print_test("Risk Level Match", "PASS", f"Risk level is {risk_level} as expected")
            passed_tests += 1
        else:
            print_test("Risk Level Match", "WARN", 
                      f"Expected {expected['fraud_risk']}, got {risk_level}")
    else:
        print_test("Fraud Agent", "FAIL", "No fraud analysis")
    
    # Check Policy Agent
    total_tests += 1
    if "compliant" in policy:
        compliant = policy.get("compliant")
        approval_level = policy.get("approval_level", "UNKNOWN")
        print_test("Policy Agent", "PASS", 
                  f"Compliant: {compliant}, Level: {approval_level}")
        passed_tests += 1
    else:
        print_test("Policy Agent", "FAIL", "No policy check")
    
    # Check Decision Agent
    total_tests += 1
    if decision_data.get("decision"):
        decision = decision_data.get("decision")
        confidence = decision_data.get("confidence", 0)
        reason = decision_data.get("reason", "")
        print_test("Decision Agent", "PASS", 
                  f"Decision: {decision} (Confidence: {confidence:.0%})")
        
        if reason:
            print(f"   Reason: {reason}")
        
        passed_tests += 1
        
        # Validate decision matches expected
        total_tests += 1
        if decision == expected["expected_decision"]:
            print_test("Decision Match", "PASS", f"Decision is {decision} as expected")
            passed_tests += 1
        else:
            print_test("Decision Match", "WARN", 
                      f"Expected {expected['expected_decision']}, got {decision}")
    else:
        print_test("Decision Agent", "FAIL", "No decision made")
    
    # Overall result
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n   {Colors.BOLD}Result: {passed_tests}/{total_tests} tests passed ({pass_rate:.0f}%){Colors.END}")
    
    return passed_tests == total_tests

async def test_dashboard_stats():
    """Test dashboard statistics endpoint"""
    print_header("Dashboard Statistics Test")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Get stats
            async with session.get(f"{API_URL}/stats") as response:
                if response.status != 200:
                    print_test("Stats API", "FAIL", f"HTTP {response.status}")
                    return False
                
                stats = await response.json()
                print_test("Stats API", "PASS", "Retrieved statistics")
                
                # Display stats
                print(f"\n   📊 Dashboard Statistics:")
                print(f"   Total Invoices: {stats.get('total_invoices', 0)}")
                print(f"   Approved: {stats.get('approved', 0)}")
                print(f"   Rejected: {stats.get('rejected', 0)}")
                print(f"   On Hold: {stats.get('on_hold', 0)}")
                
                # Get recent invoices
                async with session.get(f"{API_URL}/invoices") as inv_response:
                    if inv_response.status != 200:
                        print_test("Invoices API", "FAIL", f"HTTP {inv_response.status}")
                        return False
                    
                    invoices = await inv_response.json()
                    # Handle both dict and list responses
                    if isinstance(invoices, dict):
                        invoices = invoices.get('invoices', [])
                    
                    print_test("Invoices API", "PASS", f"Retrieved {len(invoices)} invoices")
                    
                    # Show recent invoices
                    print(f"\n   📋 Recent Invoices:")
                    for idx, inv in enumerate(invoices[:5], 1):
                        print(f"   {idx}. {inv.get('vendor_name', 'N/A')} - "
                              f"${inv.get('total_amount', 0):,.2f} - "
                              f"Decision: {inv.get('decision', 'N/A')}")
                    
                    return True
        
        except Exception as e:
            print_test("Dashboard Test", "FAIL", str(e))
            return False

async def main():
    """Run all Phase 5 tests"""
    print_header("InvoiceFlow AI - Phase 5 End-to-End Testing")
    
    print(f"{Colors.BOLD}Test Configuration:{Colors.END}")
    print(f"   API URL: {API_URL}")
    print(f"   Test Invoices: {TEST_INVOICES_DIR}")
    print(f"   Scenarios: {len(EXPECTED_OUTCOMES)}")
    
    # Check if server is running
    print(f"\n{Colors.BOLD}Pre-flight Checks:{Colors.END}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    print_test("Server Status", "PASS", "FastAPI server is running")
                else:
                    print_test("Server Status", "FAIL", f"HTTP {response.status}")
                    print("\n⚠️  Please start the server: uvicorn backend.main:app --reload")
                    return
    except Exception as e:
        print_test("Server Status", "FAIL", str(e))
        print("\n⚠️  Please start the server: uvicorn backend.main:app --reload")
        return
    
    # Run scenario tests
    print_header("Scenario Testing")
    
    scenario_results = []
    async with aiohttp.ClientSession() as session:
        for scenario_file, expected in EXPECTED_OUTCOMES.items():
            result = await test_scenario(session, scenario_file, expected)
            scenario_results.append((scenario_file, result))
            await asyncio.sleep(1)  # Brief pause between tests
    
    # Test dashboard
    dashboard_ok = await test_dashboard_stats()
    
    # Final summary
    print_header("Test Summary")
    
    passed_scenarios = sum(1 for _, result in scenario_results if result)
    total_scenarios = len(scenario_results)
    
    print(f"{Colors.BOLD}Scenario Results:{Colors.END}")
    for scenario_file, result in scenario_results:
        status = "PASS" if result else "FAIL"
        print_test(f"{scenario_file}", status)
    
    print(f"\n{Colors.BOLD}Statistics:{Colors.END}")
    print(f"   Scenarios Passed: {passed_scenarios}/{total_scenarios}")
    print(f"   Pass Rate: {(passed_scenarios/total_scenarios)*100:.0f}%")
    print(f"   Dashboard Tests: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    
    # Overall result
    overall_pass = passed_scenarios == total_scenarios and dashboard_ok
    
    if overall_pass:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 70}")
        print(f"{'✅ ALL TESTS PASSED - PHASE 5 COMPLETE'.center(70)}")
        print(f"{'=' * 70}{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}{'=' * 70}")
        print(f"{'⚠️  SOME TESTS FAILED - REVIEW RESULTS ABOVE'.center(70)}")
        print(f"{'=' * 70}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.END}")
    print("   1. Review test results above")
    print("   2. Check dashboard at http://localhost:3000")
    print("   3. Verify all 5 invoices appear in dashboard")
    print("   4. Ready for Phase 6: Polish & Demo Prep")

if __name__ == "__main__":
    asyncio.run(main())
