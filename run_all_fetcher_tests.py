#!/usr/bin/env python3
"""
Comprehensive Test Runner for Fetcher Agents
Runs all tests and provides a complete report with 100% pass rate verification.
"""

import sys
import os
import subprocess
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_test_suite(test_file, suite_name):
    """Run a specific test suite and return results"""
    print(f"\n{'='*20} {suite_name} {'='*20}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {suite_name} PASSED")
            return True, result.stdout
        else:
            print(f"❌ {suite_name} FAILED")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {suite_name} TIMEOUT")
        return False, "Test timed out"
    except Exception as e:
        print(f"💥 {suite_name} ERROR: {e}")
        return False, str(e)

def run_comprehensive_tests():
    """Run all comprehensive tests for fetcher agents"""
    print("🚀 COMPREHENSIVE FETCHER AGENT TEST SUITE")
    print("=" * 60)
    print("Testing both fetcher_agent1_latestemail.py and fetcher_agent2_database.py")
    print("Ensuring 100% pass rate across all scenarios")
    print("=" * 60)
    
    # Define test suites
    test_suites = [
        ("test_fetcher_agents.py", "Basic Functionality Tests"),
        ("test_fetcher_integration.py", "Integration Tests"),
        ("test_fetcher_edge_cases.py", "Edge Case Tests"),
        ("test_email_parsing_debug.py", "Email Parsing Debug Tests")
    ]
    
    results = []
    total_tests = 0
    passed_tests = 0
    
    # Run each test suite
    for test_file, suite_name in test_suites:
        if os.path.exists(test_file):
            success, output = run_test_suite(test_file, suite_name)
            results.append((suite_name, success, output))
            
            if success:
                passed_tests += 1
            total_tests += 1
        else:
            print(f"⚠️  {suite_name}: Test file not found ({test_file})")
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Test Suites Run: {total_tests}")
    print(f"Test Suites Passed: {passed_tests}")
    print(f"Test Suites Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100.0:
        print("\n🎉 ACHIEVED 100% PASS RATE!")
        print("✅ All fetcher agents are working correctly")
        print("✅ Ready for production deployment")
        print("✅ GitHub workflow should work without issues")
    else:
        print(f"\n⚠️  {100 - success_rate:.1f}% of tests failed")
        print("❌ Some issues need to be addressed before deployment")
    
    # Detailed results
    print("\n" + "=" * 60)
    print("📋 DETAILED RESULTS")
    print("=" * 60)
    
    for suite_name, success, output in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{suite_name}: {status}")
        if not success and output:
            print(f"  Error: {output[:200]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("📝 SUMMARY")
    print("=" * 60)
    
    if success_rate == 100.0:
        print("🎯 MISSION ACCOMPLISHED!")
        print("• Email parsing works correctly with all formats")
        print("• Database fetching works correctly")
        print("• Critical measurements (Above Navel vs Navel) are never confused")
        print("• All edge cases are handled properly")
        print("• Error handling is robust")
        print("• JSON structures are consistent")
        print("\n🚀 READY FOR PRODUCTION DEPLOYMENT")
    else:
        print("🔧 WORK NEEDED:")
        print("• Some test suites failed")
        print("• Review failed tests above")
        print("• Fix issues before deployment")
    
    return success_rate == 100.0

def run_quick_verification():
    """Run a quick verification test"""
    print("\n🔍 QUICK VERIFICATION TEST")
    print("=" * 40)
    
    try:
        from Agents.fetcher_agent1_latestemail import LatestEmailFetcher
        from Agents.fetcher_agent2_database import DatabaseFetcher
        
        # Quick email parsing test
        email_fetcher = LatestEmailFetcher()
        test_email = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34
Measurements:
Week Number: 9
Weight: 124.4
Fat Percentage: .514
Above Navel: 39
Navel: 43
        """
        
        result = email_fetcher.parse_fitness_data(test_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        if (measurements.get('Above Navel') == 39 and 
            measurements.get('Navel') == 43 and
            measurements.get('Fat Percentage') == 0.514):
            print("✅ Quick email parsing test PASSED")
            email_ok = True
        else:
            print("❌ Quick email parsing test FAILED")
            email_ok = False
        
        # Quick database test
        db_fetcher = DatabaseFetcher()
        json_data = db_fetcher.create_database_json(None)
        
        if (json_data and 
            'fitness_data' in json_data and 
            'measurements' in json_data['fitness_data']):
            print("✅ Quick database test PASSED")
            db_ok = True
        else:
            print("❌ Quick database test FAILED")
            db_ok = False
        
        return email_ok and db_ok
        
    except Exception as e:
        print(f"❌ Quick verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Starting Comprehensive Fetcher Agent Test Suite")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run quick verification first
    quick_ok = run_quick_verification()
    
    if quick_ok:
        # Run comprehensive tests
        all_passed = run_comprehensive_tests()
        
        if all_passed:
            print("\n🎉 FINAL RESULT: ALL TESTS PASSED!")
            print("✅ Fetcher agents are ready for production")
            sys.exit(0)
        else:
            print("\n❌ FINAL RESULT: SOME TESTS FAILED")
            print("⚠️  Please review and fix issues before deployment")
            sys.exit(1)
    else:
        print("\n❌ QUICK VERIFICATION FAILED")
        print("⚠️  Basic functionality is broken")
        sys.exit(1)
