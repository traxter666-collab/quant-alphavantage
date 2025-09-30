#!/usr/bin/env python3
"""
Comprehensive Error Handling Test Suite
Tests all failure scenarios and error recovery mechanisms
"""

import os
import subprocess
import time
import json
from datetime import datetime

def test_api_failures():
    """Test API failure scenarios"""
    print(" TESTING API FAILURE SCENARIOS")
    print("=" * 40)

    # Test 1: Invalid API key
    print("1. Testing invalid API key...")
    original_key = os.getenv('ALPHAVANTAGE_API_KEY')

    try:
        os.environ['ALPHAVANTAGE_API_KEY'] = 'INVALID_KEY_123'
        result = subprocess.run(['python', 'validate_api_key.py'],
                               capture_output=True, text=True, timeout=30)

        if "API key" in result.stdout and ("fail" in result.stdout.lower() or "error" in result.stdout.lower()):
            print("   SUCCESS Invalid API key properly detected")
        else:
            print("   WARNING Invalid API key not properly handled")
            print(f"   Output: {result.stdout[:100]}...")

    except Exception as e:
        print(f"   ERROR API key test failed: {e}")
    finally:
        if original_key:
            os.environ['ALPHAVANTAGE_API_KEY'] = original_key

    # Test 2: Network timeout
    print("2. Testing network resilience...")
    try:
        result = subprocess.run(['python', 'spx_command_router.py', 'spx api status'],
                               capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("   SUCCESS Network connectivity test passed")
        else:
            print("   WARNING Network test showed issues")

    except subprocess.TimeoutExpired:
        print("   WARNING Network test timed out (expected in some cases)")
    except Exception as e:
        print(f"   ERROR Network test failed: {e}")

def test_file_system_errors():
    """Test file system error handling"""
    print("\n TESTING FILE SYSTEM ERROR SCENARIOS")
    print("=" * 40)

    # Test 1: Missing .spx directory
    print("1. Testing missing session directory...")
    spx_backup = None

    try:
        if os.path.exists('.spx'):
            os.rename('.spx', '.spx_backup_test')
            spx_backup = True

        result = subprocess.run(['python', 'spx_command_router.py', 'spx now'],
                               capture_output=True, text=True, timeout=60)

        if os.path.exists('.spx'):
            print("   SUCCESS Session directory auto-created")
        else:
            print("   WARNING Session directory not created")

    except Exception as e:
        print(f"   ERROR Session directory test failed: {e}")
    finally:
        if spx_backup and os.path.exists('.spx_backup_test'):
            if os.path.exists('.spx'):
                import shutil
                shutil.rmtree('.spx')
            os.rename('.spx_backup_test', '.spx')

    # Test 2: Read-only files
    print("2. Testing file permission handling...")
    test_file = '.spx/permission_test.json'

    try:
        os.makedirs('.spx', exist_ok=True)
        with open(test_file, 'w') as f:
            json.dump({"test": "data"}, f)

        # Make file read-only (Windows compatible)
        import stat
        os.chmod(test_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        # Try to write to read-only file
        try:
            with open(test_file, 'w') as f:
                json.dump({"new": "data"}, f)
            print("   WARNING Read-only file was writable (unexpected)")
        except PermissionError:
            print("   SUCCESS Read-only file properly protected")

        # Restore permissions and cleanup
        os.chmod(test_file, stat.S_IWRITE | stat.S_IREAD)
        os.remove(test_file)

    except Exception as e:
        print(f"   ERROR Permission test failed: {e}")

def test_command_errors():
    """Test command error handling"""
    print("\nFAST TESTING COMMAND ERROR SCENARIOS")
    print("=" * 40)

    # Test 1: Unknown command
    print("1. Testing unknown command handling...")
    result = subprocess.run(['python', 'spx_command_router.py', 'spx totally_fake_command'],
                           capture_output=True, text=True, timeout=30)

    if "Unknown command" in result.stderr and "suggestions" in result.stderr.lower():
        print("   SUCCESS Unknown command handled with suggestions")
    elif "Error" in result.stderr:
        print("   SUCCESS Unknown command handled with error")
    else:
        print("   WARNING Unknown command not properly handled")
        print(f"   Output: {result.stderr[:100]}...")

    # Test 2: Malformed command
    print("2. Testing malformed command...")
    result = subprocess.run(['python', 'spx_command_router.py', ''],
                           capture_output=True, text=True, timeout=30)

    if result.returncode != 0 or "Usage" in result.stdout:
        print("   SUCCESS Empty command handled properly")
    else:
        print("   WARNING Empty command not handled")

    # Test 3: Script not found
    print("3. Testing missing script handling...")

    # Temporarily move a script
    script_to_test = 'spx_auto.py'
    backup_name = 'spx_auto.py.temp_backup'

    try:
        if os.path.exists(script_to_test):
            os.rename(script_to_test, backup_name)

        result = subprocess.run(['python', 'spx_command_router.py', 'spx now'],
                               capture_output=True, text=True, timeout=30)

        if "not found" in result.stderr.lower() or "Script not found" in result.stderr:
            print("   SUCCESS Missing script properly detected")
        else:
            print("   WARNING Missing script not detected")
            print(f"   Error output: {result.stderr[:100]}...")

    except Exception as e:
        print(f"   ERROR Missing script test failed: {e}")
    finally:
        if os.path.exists(backup_name):
            if os.path.exists(script_to_test):
                os.remove(script_to_test)
            os.rename(backup_name, script_to_test)

def test_discord_errors():
    """Test Discord integration error handling"""
    print("\nPHONE TESTING DISCORD ERROR SCENARIOS")
    print("=" * 40)

    # Test 1: Discord webhook failure
    print("1. Testing Discord webhook resilience...")

    # Test with potentially invalid webhook (the command should still work for analysis)
    result = subprocess.run(['python', 'spx_command_router.py', 'spx quick discord'],
                           capture_output=True, text=True, timeout=60)

    if "discord" in result.stdout.lower() or result.returncode == 0:
        print("   SUCCESS Discord integration handled gracefully")
    else:
        print("   WARNING Discord error not handled gracefully")
        print(f"   Error: {result.stderr[:100]}...")

def test_timeout_scenarios():
    """Test timeout handling"""
    print("\n TESTING TIMEOUT SCENARIOS")
    print("=" * 40)

    print("1. Testing command timeout handling...")

    # The router has a 5-minute timeout
    start_time = time.time()

    try:
        result = subprocess.run(['python', 'spx_command_router.py', 'spx dealer positioning'],
                               capture_output=True, text=True, timeout=10)  # 10-second test timeout

        elapsed = time.time() - start_time
        if elapsed < 10 and result.returncode == 0:
            print("   SUCCESS Command completed within timeout")
        else:
            print(f"   WARNING Command took {elapsed:.1f}s")

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"   WARNING Command timed out after {elapsed:.1f}s (may be expected for complex analysis)")

def test_recovery_mechanisms():
    """Test system recovery capabilities"""
    print("\n TESTING RECOVERY MECHANISMS")
    print("=" * 40)

    # Test 1: Session recovery
    print("1. Testing session recovery...")

    try:
        # Create a corrupt session file
        corrupt_session = '.spx/test_corrupt.json'
        with open(corrupt_session, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON

        result = subprocess.run(['python', 'spx_command_router.py', 'spx now'],
                               capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("   SUCCESS System recovered from corrupt session data")
        else:
            print("   WARNING System struggled with corrupt session data")

        # Cleanup
        if os.path.exists(corrupt_session):
            os.remove(corrupt_session)

    except Exception as e:
        print(f"   ERROR Recovery test failed: {e}")

def main():
    """Run comprehensive error handling tests"""
    print(" COMPREHENSIVE ERROR HANDLING TEST SUITE")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run all tests
    test_api_failures()
    test_file_system_errors()
    test_command_errors()
    test_discord_errors()
    test_timeout_scenarios()
    test_recovery_mechanisms()

    print("\n" + "=" * 50)
    print(" ERROR HANDLING TEST COMPLETE")
    print()
    print(" SUMMARY:")
    print("SUCCESS = Proper error handling detected")
    print("WARNING = Warning or unexpected behavior")
    print("ERROR = Test failed or error not handled")
    print()
    print("IDEA RECOMMENDATION:")
    print("Review any WARNING or ERROR items for production readiness")

if __name__ == "__main__":
    main()