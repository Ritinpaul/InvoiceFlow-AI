"""
Generate sample invoice images for Phase 5 testing
Creates 5 realistic invoice images with different scenarios
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import random

# Invoice scenarios for testing different paths through the system
SCENARIOS = [
    {
        "filename": "scenario1_approved_low_risk.png",
        "vendor": "TechSupplies Inc",
        "invoice_num": "INV-2026-001",
        "amount": 1250.00,
        "date": "2026-01-10",
        "description": "Normal approved invoice - known vendor, reasonable amount",
        "items": [
            "Dell Laptop x1 - $800.00",
            "Wireless Mouse x2 - $50.00", 
            "USB-C Hub - $150.00",
            "Laptop Bag - $80.00",
            "Extended Warranty - $170.00"
        ]
    },
    {
        "filename": "scenario2_high_risk_fraud.png",
        "vendor": "Unknown Vendor LLC",
        "invoice_num": "FAKE-999",
        "amount": 99999.99,
        "date": "2026-01-15",
        "description": "High fraud risk - unknown vendor, suspicious amount",
        "items": [
            "Consulting Services - $99,999.99"
        ]
    },
    {
        "filename": "scenario3_policy_violation.png",
        "vendor": "OfficeDepot",
        "invoice_num": "INV-OD-5532",
        "amount": 15750.00,
        "date": "2026-01-12",
        "description": "Policy violation - amount exceeds $15k limit",
        "items": [
            "Office Furniture Set - $12,000.00",
            "Desk Chairs x5 - $2,500.00",
            "Filing Cabinets - $1,250.00"
        ]
    },
    {
        "filename": "scenario4_duplicate_invoice.png",
        "vendor": "TechSupplies Inc",
        "invoice_num": "INV-2026-001",
        "amount": 1250.00,
        "date": "2026-01-10",
        "description": "Duplicate detection - same invoice number as scenario 1",
        "items": [
            "Dell Laptop x1 - $800.00",
            "Wireless Mouse x2 - $50.00",
            "USB-C Hub - $150.00"
        ]
    },
    {
        "filename": "scenario5_requires_approval.png",
        "vendor": "Amazon Business",
        "invoice_num": "AMZ-2026-AB123",
        "amount": 8500.00,
        "date": "2026-01-14",
        "description": "Requires manager approval - medium amount, known vendor",
        "items": [
            "Conference Room Monitor 65\" - $4,500.00",
            "Webcam System - $1,200.00",
            "Audio System - $2,800.00"
        ]
    }
]

def create_invoice_image(scenario):
    """Create a realistic invoice image"""
    
    # Image dimensions
    width, height = 800, 1000
    
    # Create white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        heading_font = ImageFont.truetype("arial.ttf", 24)
        normal_font = ImageFont.truetype("arial.ttf", 18)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    y_position = 50
    
    # Company header
    draw.text((50, y_position), scenario["vendor"], fill='black', font=title_font)
    y_position += 50
    
    draw.text((50, y_position), "123 Business Street", fill='gray', font=small_font)
    y_position += 25
    draw.text((50, y_position), "New York, NY 10001", fill='gray', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Phone: (555) 123-4567", fill='gray', font=small_font)
    y_position += 50
    
    # Invoice title
    draw.text((50, y_position), "INVOICE", fill='black', font=heading_font)
    y_position += 50
    
    # Invoice details
    draw.text((50, y_position), f"Invoice Number: {scenario['invoice_num']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Date: {scenario['date']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Due Date: {scenario['date']}", fill='black', font=normal_font)
    y_position += 50
    
    # Bill to
    draw.text((50, y_position), "BILL TO:", fill='black', font=heading_font)
    y_position += 35
    draw.text((50, y_position), "InvoiceFlow AI Company", fill='black', font=normal_font)
    y_position += 25
    draw.text((50, y_position), "456 Tech Avenue", fill='black', font=small_font)
    y_position += 25
    draw.text((50, y_position), "San Francisco, CA 94105", fill='black', font=small_font)
    y_position += 50
    
    # Items header
    draw.line([(50, y_position), (750, y_position)], fill='black', width=2)
    y_position += 10
    draw.text((50, y_position), "DESCRIPTION", fill='black', font=normal_font)
    draw.text((600, y_position), "AMOUNT", fill='black', font=normal_font)
    y_position += 30
    draw.line([(50, y_position), (750, y_position)], fill='black', width=1)
    y_position += 20
    
    # Line items
    for item in scenario["items"]:
        draw.text((50, y_position), item, fill='black', font=small_font)
        y_position += 25
    
    y_position += 20
    draw.line([(50, y_position), (750, y_position)], fill='black', width=1)
    y_position += 20
    
    # Total
    draw.text((50, y_position), "TOTAL:", fill='black', font=heading_font)
    draw.text((600, y_position), f"${scenario['amount']:,.2f}", fill='black', font=heading_font)
    y_position += 50
    
    # Payment terms
    draw.text((50, y_position), "Payment Terms: Net 30", fill='gray', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Please make payment to: Bank Account #1234567890", fill='gray', font=small_font)
    
    # Footer
    y_position = height - 50
    draw.text((50, y_position), "Thank you for your business!", fill='gray', font=small_font)
    
    return img

def main():
    """Generate all sample invoices"""
    print("🎨 Generating Sample Invoice Images for Phase 5 Testing\n")
    print("=" * 60)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    for idx, scenario in enumerate(SCENARIOS, 1):
        print(f"\n📄 Scenario {idx}: {scenario['description']}")
        print(f"   Vendor: {scenario['vendor']}")
        print(f"   Invoice #: {scenario['invoice_num']}")
        print(f"   Amount: ${scenario['amount']:,.2f}")
        print(f"   Expected Path: {scenario['description'].split('-')[0].strip()}")
        
        # Create invoice image
        img = create_invoice_image(scenario)
        
        # Save image
        output_path = os.path.join(output_dir, scenario['filename'])
        img.save(output_path)
        print(f"   ✅ Saved to: {scenario['filename']}")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully generated {len(SCENARIOS)} test invoice images")
    print(f"📁 Location: {output_dir}")
    print("\n📋 Test Scenarios Summary:")
    print("   1. ✅ Approved - Low risk, known vendor, normal amount")
    print("   2. 🚨 Fraud - Unknown vendor, suspicious amount")
    print("   3. ⚠️  Policy - Exceeds approval limit ($15k)")
    print("   4. 🔄 Duplicate - Same invoice number as #1")
    print("   5. 👤 Approval - Requires manager review (medium amount)")
    print("\nReady for Phase 5 testing!")

if __name__ == "__main__":
    main()
