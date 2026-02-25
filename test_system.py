"""
System Validation Script
========================
Run this to check if all components are working correctly.

Usage:
    python test_system.py
"""

import sys
import os

print("=" * 60)
print("Face Detection Attendance System - Validation")
print("=" * 60)
print()

# Test 1: Python Version
print("Test 1: Python Version")
print("-" * 40)
version = sys.version_info
print(f"Python {version.major}.{version.minor}.{version.micro}")
if version.major >= 3 and version.minor >= 8:
    print("✅ PASS - Python version is compatible")
else:
    print("❌ FAIL - Python 3.8+ required")
    sys.exit(1)
print()

# Test 2: Required Modules
print("Test 2: Required Python Modules")
print("-" * 40)
required_modules = {
    'cv2': 'opencv-python',
    'mysql.connector': 'mysql-connector-python',
    'PIL': 'Pillow',
    'pandas': 'pandas',
    'openpyxl': 'openpyxl',
    'numpy': 'numpy',
}

all_modules_ok = True
for module, package in required_modules.items():
    try:
        __import__(module)
        print(f"✅ {package:30s} - OK")
    except ImportError:
        print(f"❌ {package:30s} - MISSING")
        print(f"   Install: pip install {package}")
        all_modules_ok = False

if not all_modules_ok:
    print("\n⚠️  Some modules are missing. Install them first:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
print()

# Test 3: OpenCV Camera Access
print("Test 3: Camera Access")
print("-" * 40)
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"✅ Camera opened successfully")
            print(f"   Resolution: {w}x{h}")
        else:
            print("⚠️  Camera opened but cannot read frames")
        cap.release()
    else:
        print("❌ Cannot open camera (index 0)")
        print("   Try: Close other apps using camera")
        print("   Or: Camera might be at index 1")
except Exception as e:
    print(f"❌ Camera test failed: {e}")
print()

# Test 4: Face Detection Engine
print("Test 4: Face Detection Engine")
print("-" * 40)
try:
    from face_engine import detect_faces, encode_face, compare_faces
    import numpy as np
    
    # Test with dummy data
    dummy_gray = np.zeros((480, 640), dtype=np.uint8)
    faces = detect_faces(dummy_gray)
    print(f"✅ Face detection engine loaded")
    print(f"   Detected {len(faces)} faces in test image (expected: 0)")
    
    # Test encoding
    dummy_face = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    enc = encode_face(dummy_face)
    if enc is not None and len(enc) > 0:
        print(f"✅ Face encoding works")
        print(f"   Encoding size: {len(enc)} features")
    else:
        print("❌ Face encoding failed")
        
except Exception as e:
    print(f"❌ Face engine test failed: {e}")
print()

# Test 5: Database Connection
print("Test 5: Database Connection")
print("-" * 40)
try:
    from database import DatabaseManager, DB_CONFIG
    
    print(f"Database config:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Database: {DB_CONFIG['database']}")
    
    db = DatabaseManager()
    conn = db.get_connection()
    
    if conn:
        print("✅ Database connection successful")
        
        # Test table creation
        try:
            db.initialize_database()
            print("✅ Database tables initialized")
            
            # Test admin account
            admin = db.verify_admin('admin', 'admin123')
            if admin:
                print("✅ Default admin account exists")
                print(f"   Username: {admin['username']}")
            else:
                print("⚠️  Default admin account not found")
                print("   Will be created on first run")
                
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")
        
        conn.close()
    else:
        print("❌ Cannot connect to database")
        print("   Check MySQL is running")
        print("   Verify password in database.py")
        
except Exception as e:
    print(f"❌ Database test failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure MySQL Server is running")
    print("2. Check password in database.py")
    print("3. Verify MySQL user has permissions")
print()

# Test 6: File Structure
print("Test 6: Project File Structure")
print("-" * 40)
required_files = [
    'main.py',
    'database.py',
    'login.py',
    'dashboard.py',
    'attendance_module.py',
    'students_module.py',
    'reports_module.py',
    'settings_module.py',
    'face_engine.py',
    'requirements.txt',
    'README.md',
]

all_files_ok = True
for filename in required_files:
    if os.path.exists(filename):
        print(f"✅ {filename:30s} - Found")
    else:
        print(f"❌ {filename:30s} - Missing")
        all_files_ok = False

if not all_files_ok:
    print("\n⚠️  Some files are missing!")
print()

# Test 7: Directories
print("Test 7: Required Directories")
print("-" * 40)
required_dirs = ['student_photos', 'attendance_csv']
for dirname in required_dirs:
    if os.path.exists(dirname):
        print(f"✅ {dirname:30s} - Exists")
    else:
        print(f"⚠️  {dirname:30s} - Will be created automatically")
print()

# Final Summary
print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

if all_modules_ok and all_files_ok:
    print("✅ System is ready to run!")
    print()
    print("Next steps:")
    print("1. Run: python main.py")
    print("2. Login with: admin / admin123")
    print("3. Change default password in Settings")
    print("4. Add students with face capture")
    print("5. Start taking attendance!")
else:
    print("⚠️  System has some issues. Please fix them first.")
    print()
    print("Common fixes:")
    print("- Install missing modules: pip install -r requirements.txt")
    print("- Start MySQL Server")
    print("- Check database password in database.py")
    print("- Ensure all project files are present")

print()
print("For detailed setup instructions, see SETUP_GUIDE.md")
print("=" * 60)
