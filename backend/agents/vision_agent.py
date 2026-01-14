import easyocr
from pdf2image import convert_from_path
from PIL import Image
import os

class VisionAgent:
    def __init__(self):
        self.name = "Vision Agent"
        print(f"[{self.name}] Initializing OCR...")
        # Initialize EasyOCR with English language, GPU disabled for compatibility
        self.reader = easyocr.Reader(['en'], gpu=False)
        print(f"[{self.name}] OCR Ready")
    
    async def process(self, file_path: str):
        """
        Extract text from PDF or image file.
        Supports: PDF, JPG, JPEG, PNG
        """
        print(f"[{self.name}] Processing {file_path}")
        
        try:
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = await self._process_pdf(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                text = await self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            print(f"[{self.name}] Extracted {len(text)} characters")
            return {
                "raw_text": text, 
                "char_count": len(text),
                "status": "success"
            }
            
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            return {
                "raw_text": "", 
                "char_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def _process_pdf(self, file_path: str):
        """
        Convert PDF to images and extract text.
        Note: Requires Poppler to be installed and in PATH
        """
        try:
            # Convert first page of PDF to image
            images = convert_from_path(file_path, first_page=1, last_page=1)
            all_text = []
            
            for img in images:
                # EasyOCR expects numpy array or PIL Image
                result = self.reader.readtext(img, detail=0, paragraph=False)
                all_text.extend(result)
            
            return "\n".join(all_text)
        except Exception as e:
            # If Poppler is not installed, provide helpful error
            if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
                raise Exception("Poppler not installed. Please install Poppler for PDF support or use image files (JPG/PNG)")
            raise e
    
    async def _process_image(self, file_path: str):
        """
        Extract text from image file (JPG, PNG).
        """
        # Read text from image
        result = self.reader.readtext(file_path, detail=0, paragraph=False)
        return "\n".join(result)
