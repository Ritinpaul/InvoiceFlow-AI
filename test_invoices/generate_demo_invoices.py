"""
Generate compliant demo invoices that will be APPROVED
These invoices have all required fields and use approved vendors
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import random

# Demo scenarios - these should all APPROVE
DEMO_SCENARIOS = [
    {
        "filename": "demo1_approved_small.png",
        "vendor": "TechSupplies Inc",
        "invoice_num": "TS-2026-100",
        "amount": 850.00,
        "tax": 68.00,
        "po_number": "PO-2026-001",
        "date": "2026-01-10",
        "description": "Small approved invoice - auto-approve tier",
        "items": [
            {"desc": "Wireless Mouse x2", "price": 50.00},
            {"desc": "USB-C Cables x5", "price": 75.00},
            {"desc": "Laptop Stand", "price": 125.00},
            {"desc": "Monitor Riser", "price": 80.00},
            {"desc": "Cable Management Kit", "price": 45.00},
            {"desc": "Desk Mat", "price": 35.00},
            {"desc": "Webcam Cover x10", "price": 20.00},
            {"desc": "Screen Cleaner Kit", "price": 25.00},
            {"desc": "Phone Holder", "price": 30.00},
            {"desc": "Ergonomic Wrist Rest", "price": 65.00},
            {"desc": "Subtotal", "price": 550.00},
            {"desc": "Shipping & Handling", "price": 150.00},
            {"desc": "Rush Processing Fee", "price": 150.00}
        ]
    },
    {
        "filename": "demo2_approved_medium.png",
        "vendor": "Dell Technologies",
        "invoice_num": "DELL-INV-2026-5532",
        "amount": 4500.00,
        "tax": 360.00,
        "po_number": "PO-2026-002",
        "date": "2026-01-12",
        "description": "Medium invoice - manager approval tier",
        "items": [
            {"desc": "Dell Latitude 5540 Laptop", "price": 1800.00},
            {"desc": "Dell UltraSharp Monitor 27\"", "price": 650.00},
            {"desc": "Dell Wireless Keyboard/Mouse", "price": 120.00},
            {"desc": "Dell Docking Station USB-C", "price": 280.00},
            {"desc": "Dell Laptop Bag Professional", "price": 85.00},
            {"desc": "3-Year ProSupport Warranty", "price": 450.00},
            {"desc": "Dell Webcam WB7022", "price": 180.00},
            {"desc": "Dell Active Pen PN7320", "price": 95.00},
            {"desc": "Installation & Setup Service", "price": 200.00},
            {"desc": "Data Migration Service", "price": 150.00},
            {"desc": "Extended Memory 32GB Upgrade", "price": 490.00}
        ]
    },
    {
        "filename": "demo3_approved_large.png",
        "vendor": "Amazon Business",
        "invoice_num": "AMZ-B2B-2026-8821",
        "amount": 12500.00,
        "tax": 1000.00,
        "po_number": "PO-2026-003",
        "date": "2026-01-14",
        "description": "Large invoice - director approval tier",
        "items": [
            {"desc": "Conference Room Monitors 65\" x3", "price": 4500.00},
            {"desc": "Video Conference System", "price": 2800.00},
            {"desc": "Professional Audio System", "price": 1200.00},
            {"desc": "Conference Table 12-Person", "price": 1500.00},
            {"desc": "Executive Chairs x12", "price": 1800.00},
            {"desc": "Whiteboard Interactive 75\"", "price": 650.00}
        ]
    }
]

def create_compliant_invoice(scenario):
    """Create a compliant invoice image with all required fields"""
    
    # Image dimensions
    width, height = 800, 1100
    
    # Create white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        heading_font = ImageFont.truetype("arial.ttf", 24)
        normal_font = ImageFont.truetype("arial.ttf", 18)
        small_font = ImageFont.truetype("arial.ttf", 14)
        bold_font = ImageFont.truetype("arialbd.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    y_position = 50
    
    # Company header
    draw.text((50, y_position), scenario["vendor"], fill='black', font=title_font)
    y_position += 50
    
    draw.text((50, y_position), "Authorized Vendor", fill='green', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Tax ID: 12-3456789", fill='gray', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Phone: (555) 123-4567", fill='gray', font=small_font)
    y_position += 50
    
    # Invoice title
    draw.text((50, y_position), "INVOICE", fill='black', font=heading_font)
    y_position += 50
    
    # Invoice details (left column)
    draw.text((50, y_position), f"Invoice Number: {scenario['invoice_num']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Date: {scenario['date']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"PO Number: {scenario['po_number']}", fill='black', font=bold_font)
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
        draw.text((50, y_position), item["desc"], fill='black', font=small_font)
        draw.text((600, y_position), f"${item['price']:,.2f}", fill='black', font=small_font)
        y_position += 22
    
    y_position += 20
    draw.line([(50, y_position), (750, y_position)], fill='black', width=1)
    y_position += 20
    
    # Subtotal
    draw.text((400, y_position), "Subtotal:", fill='black', font=normal_font)
    draw.text((600, y_position), f"${scenario['amount']:,.2f}", fill='black', font=normal_font)
    y_position += 30
    
    # Tax (REQUIRED FIELD)
    draw.text((400, y_position), "Tax (8%):", fill='black', font=normal_font)
    draw.text((600, y_position), f"${scenario['tax']:,.2f}", fill='black', font=normal_font)
    y_position += 30
    
    # Total
    draw.line([(400, y_position), (750, y_position)], fill='black', width=2)
    y_position += 10
    total = scenario['amount'] + scenario['tax']
    draw.text((400, y_position), "TOTAL:", fill='black', font=heading_font)
    draw.text((600, y_position), f"${total:,.2f}", fill='black', font=heading_font)
    y_position += 50
    
    # Payment terms
    draw.text((50, y_position), "Payment Terms: Net 30", fill='gray', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Please make payment to: Bank Account #1234567890", fill='gray', font=small_font)
    
    # Footer
    y_position = height - 100
    draw.line([(50, y_position), (750, y_position)], fill='lightgray', width=1)
    y_position += 10
    draw.text((50, y_position), "✅ Approved Vendor | All Required Fields Present", fill='green', font=small_font)
    y_position += 20
    draw.text((50, y_position), f"PO: {scenario['po_number']} | Tax Included | Compliant Invoice", fill='green', font=small_font)
    y_position += 25
    draw.text((50, y_position), "Thank you for your business!", fill='gray', font=small_font)
    
    return img

def main():
    """Generate all compliant demo invoices"""
    print("🎨 Generating Compliant Demo Invoice Images\n")
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_invoices")
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, scenario in enumerate(DEMO_SCENARIOS, 1):
        print(f"\n📄 Demo {idx}: {scenario['description']}")
        print(f"   Vendor: {scenario['vendor']} ✅ APPROVED")
        print(f"   Invoice #: {scenario['invoice_num']}")
        print(f"   PO Number: {scenario['po_number']} ✅ PRESENT")
        print(f"   Amount: ${scenario['amount']:,.2f}")
        print(f"   Tax: ${scenario['tax']:,.2f} ✅ INCLUDED")
        print(f"   Total: ${scenario['amount'] + scenario['tax']:,.2f}")
        print(f"   Expected: ✅ APPROVED")
        
        # Create invoice image
        img = create_compliant_invoice(scenario)
        
        # Save image
        output_path = os.path.join(output_dir, scenario['filename'])
        img.save(output_path)
        print(f"   💾 Saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully generated {len(DEMO_SCENARIOS)} compliant demo invoices")
    print(f"📁 Location: {output_dir}")
    print("\n📋 Demo Scenarios Summary:")
    print("   1. ✅ Small Invoice ($850) - Auto-approve tier")
    print("   2. ✅ Medium Invoice ($4,500) - Manager approval")
    print("   3. ✅ Large Invoice ($12,500) - Director approval")
    print("\n🎯 All invoices should be APPROVED (have all required fields)")
    print("   • Approved vendors ✅")
    print("   • PO numbers present ✅")
    print("   • Tax amounts included ✅")
    print("\nReady for demo presentation!")

if __name__ == "__main__":
    main()
