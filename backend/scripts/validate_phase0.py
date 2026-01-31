"""
Phase 0 Validation Script - Test all installed dependencies
"""
import sys

def test_easyocr():
    """Test EasyOCR installation"""
    try:
        import easyocr
        print("✓ EasyOCR Ready")
        return True
    except Exception as e:
        print(f"✗ EasyOCR Error: {e}")
        return False

def test_spacy():
    """Test spaCy installation and model"""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy & en_core_web_sm Ready")
        return True
    except Exception as e:
        print(f"✗ spaCy Error: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing libraries"""
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image Ready (Note: Requires Poppler to be in PATH)")
        return True
    except Exception as e:
        print(f"✗ pdf2image Error: {e}")
        return False

def test_other_imports():
    """Test other required imports"""
    modules = [
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('PIL', 'Pillow'),
        ('dotenv', 'python-dotenv'),
        ('alembic', 'Alembic'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('sqlalchemy', 'SQLAlchemy')
    ]
    
    all_good = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✓ {name} Ready")
        except Exception as e:
            print(f"✗ {name} Error: {e}")
            all_good = False
    
    return all_good

def test_database():
    """Test database connection"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5433,
            user="user",
            password="password",
            database="invoiceflow"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        print("✓ PostgreSQL Connection Ready")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL Error: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis Connection Ready")
        return True
    except Exception as e:
        print(f"⚠ Redis Error: {e} (Redis not critical for basic demo)")
        return True  # Not critical

def main():
    print("=" * 60)
    print("Phase 0 Validation - Checking All Dependencies")
    print("=" * 60)
    print()
    
    tests = [
        test_easyocr,
        test_spacy,
        test_pdf_processing,
        test_other_imports,
        test_database,
        test_redis
    ]
    
    results = [test() for test in tests]
    
    print()
    print("=" * 60)
    if all(results):
        print("✓ ALL VALIDATIONS PASSED - Phase 0 Complete!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("1. For PDF support, install Poppler:")
        print("   Download: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("   Extract to: C:\\Program Files\\poppler")
        print("   Add to PATH: C:\\Program Files\\poppler\\Library\\bin")
        print()
        print("2. Start Phase 1: Core Agent Implementation")
        return 0
    else:
        print("✗ SOME VALIDATIONS FAILED - Please fix errors above")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
