"""Test script to verify all login fixes are working"""
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("\n" + "="*60)
print("LOGIN FIXES VERIFICATION TEST")
print("="*60)

# Test 1: Database connection
print("\n[TEST 1] Database Connection")
print("-" * 60)
try:
    from src.db.db_utils import get_db_connection
    conn = get_db_connection()
    print("✅ Database connection successful")
    conn.close()
    test1_pass = True
except Exception as e:
    print(f"❌ Connection failed: {e}")
    test1_pass = False

# Test 2: Verify database tables exist
print("\n[TEST 2] Database Tables")
print("-" * 60)
try:
    from src.db.db_utils import initialize_database
    initialize_database()
    print("✅ Database tables initialized")
    test2_pass = True
except Exception as e:
    print(f"❌ Table initialization failed: {e}")
    test2_pass = False

# Test 3: Registration with SHORT password (should REJECT)
print("\n[TEST 3] Registration with Short Password (Should REJECT)")
print("-" * 60)
try:
    from src.db.db_utils import add_user
    result = add_user("shorttest_pwd", "Short1")  # Only 6 characters
    if result:
        print("❌ BUG: Short password (6 chars) was accepted!")
        test3_pass = False
    else:
        print("✅ Short password (6 chars) correctly rejected")
        test3_pass = True
except Exception as e:
    print(f"❌ Error: {e}")
    test3_pass = False

# Test 4: Registration with VALID password (should ACCEPT)
print("\n[TEST 4] Registration with Valid Password (Should ACCEPT)")
print("-" * 60)
try:
    from src.db.db_utils import add_user
    result = add_user("validtest_pwd", "ValidPass123")  # 11 characters
    if result:
        print("✅ Valid password (11 chars) accepted")
        test4_pass = True
    else:
        print("❌ Valid password (11 chars) rejected")
        test4_pass = False
except Exception as e:
    print(f"❌ Error: {e}")
    test4_pass = False

# Test 5: Login with CORRECT credentials
print("\n[TEST 5] Login with Correct Credentials (Should SUCCEED)")
print("-" * 60)
try:
    from src.db.db_utils import verify_user
    result = verify_user("validtest_pwd", "ValidPass123")
    if result:
        print(f"✅ Login successful: {result}")
        test5_pass = True
    else:
        print("❌ Login failed with correct credentials")
        test5_pass = False
except Exception as e:
    print(f"❌ Error: {e}")
    test5_pass = False

# Test 6: Login with WRONG password
print("\n[TEST 6] Login with Wrong Password (Should FAIL)")
print("-" * 60)
try:
    from src.db.db_utils import verify_user
    result = verify_user("validtest_pwd", "WrongPassword123")
    if result:
        print("❌ BUG: Wrong password was accepted!")
        test6_pass = False
    else:
        print("✅ Wrong password correctly rejected")
        test6_pass = True
except Exception as e:
    print(f"❌ Error: {e}")
    test6_pass = False

# Test 7: Registration with short username (should REJECT)
print("\n[TEST 7] Registration with Short Username (Should REJECT)")
print("-" * 60)
try:
    from src.db.db_utils import add_user
    result = add_user("ab", "ValidPass123")  # Only 2 characters
    if result:
        print("❌ BUG: Short username (2 chars) was accepted!")
        test7_pass = False
    else:
        print("✅ Short username (2 chars) correctly rejected")
        test7_pass = True
except Exception as e:
    print(f"❌ Error: {e}")
    test7_pass = False

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

tests = [
    ("Database Connection", test1_pass),
    ("Database Tables", test2_pass),
    ("Short Password Rejection", test3_pass),
    ("Valid Password Acceptance", test4_pass),
    ("Correct Credentials Login", test5_pass),
    ("Wrong Password Rejection", test6_pass),
    ("Short Username Rejection", test7_pass),
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for test_name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

print("="*60)
print(f"RESULT: {passed}/{total} tests passed")
print("="*60)

if passed == total:
    print("\n🎉 All login fixes are working correctly!")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
    sys.exit(1)
