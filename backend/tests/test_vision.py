"""
Test script for Vision Agent
Tests OCR functionality with sample images
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.vision_agent import VisionAgent


async def test_vision_agent():
    """Test Vision Agent with a simple text image"""
    print("=" * 60)
    print("Testing Vision Agent")
    print("=" * 60)
    print()
    
    agent = VisionAgent()
    
    # Test with a sample file
    # For now, we'll create a simple test image
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple invoice image for testing
    test_image_path = "test_invoice.png"
    
    # Create test image
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    text = """
    ACME Corporation
    Invoice #: INV-12345
    Date: 01/15/2026
    
    Total: $1,250.00
    """
    
    y_pos = 50
    for line in text.strip().split('\n'):
        draw.text((50, y_pos), line.strip(), fill='black')
        y_pos += 40
    
    img.save(test_image_path)
    print(f"Created test image: {test_image_path}")
    print()
    
    # Test Vision Agent
    result = await agent.process(test_image_path)
    
    print("Vision Agent Result:")
    print(f"  Status: {result.get('status')}")
    print(f"  Characters extracted: {result.get('char_count')}")
    print(f"  Raw text preview:")
    print("  " + "-" * 50)
    text_preview = result.get('raw_text', '')[:200]
    print(f"  {text_preview}")
    if len(result.get('raw_text', '')) > 200:
        print("  ...")
    print("  " + "-" * 50)
    print()
    
    # Cleanup
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"Cleaned up test image")
    
    print()
    print("=" * 60)
    if result.get('status') == 'success' and result.get('char_count', 0) > 0:
        print("✓ Vision Agent Test PASSED")
    else:
        print("✗ Vision Agent Test FAILED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_vision_agent())
