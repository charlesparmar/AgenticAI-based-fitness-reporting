#!/usr/bin/env python3
"""
Test script to verify that fetcher agents are working correctly
and not copying values between different measurement fields.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher
from Agents.fetcher_agent2_database import DatabaseFetcher

def test_email_parsing():
    """Test the email parsing functionality with sample data"""
    print("🧪 Testing Email Parsing...")
    
    # Sample email body that matches the format from the image
    sample_email_body = """
    Fitness Data Entry Date: 21/08/2025
    Submitted: 21/08/2025 09:40:34
    
    Measurements:
    Week Number: 9
    Weight: 124.4
    Fat Percentage: .514
    Bmi: 45.7
    Fat Weight: 64
    Lean Weight: 60.4
    Neck: 16
    Shoulders: 18
    Biceps: 18
    Forearms: 12.5
    Chest: 43
    Above Navel: 39
    Navel: 43
    Waist: 42
    Hips: 48
    Thighs: 29
    Calves: 17
    """
    
    fetcher = LatestEmailFetcher()
    result = fetcher.parse_fitness_data(sample_email_body)
    
    print(f"📊 Parsed measurements:")
    for key, value in result['measurements'].items():
        print(f"  {key}: {value}")
    
    # Check for the specific issue
    above_navel = result['measurements'].get('Above Navel')
    navel = result['measurements'].get('Navel')
    
    print(f"\n🔍 Critical check:")
    print(f"  Above Navel: {above_navel}")
    print(f"  Navel: {navel}")
    
    if above_navel == navel:
        print("❌ ERROR: Above Navel and Navel have the same value!")
        return False
    else:
        print("✅ SUCCESS: Above Navel and Navel have different values!")
        return True

def test_database_fetcher():
    """Test the database fetcher functionality"""
    print("\n🧪 Testing Database Fetcher...")
    
    try:
        fetcher = DatabaseFetcher()
        db_entry = fetcher.fetch_latest_db_entry()
        
        if db_entry:
            print(f"📊 Database entry found:")
            print(f"  Week Number: {db_entry.get('week_number')}")
            print(f"  Weight: {db_entry.get('weight')}")
            
            # Check for the specific issue
            above_navel = db_entry.get('above_navel')
            navel = db_entry.get('navel')
            
            print(f"\n🔍 Critical check:")
            print(f"  Above Navel: {above_navel}")
            print(f"  Navel: {navel}")
            
            if above_navel == navel and above_navel is not None:
                print("❌ ERROR: Database shows Above Navel and Navel have the same value!")
                return False
            else:
                print("✅ SUCCESS: Database shows Above Navel and Navel have different values!")
                return True
        else:
            print("ℹ️  No database entry found - this is normal if no data exists")
            return True
            
    except Exception as e:
        print(f"❌ Error testing database fetcher: {e}")
        return False

def test_edge_cases():
    """Test edge cases that might cause parsing issues"""
    print("\n🧪 Testing Edge Cases...")
    
    # Test case where values are the same but should be parsed correctly
    edge_case_email = """
    Fitness Data Entry Date: 21/08/2025
    Submitted: 21/08/2025 09:40:34
    
    Measurements:
    Week Number: 9
    Weight: 124.4
    Chest: 43
    Above Navel: 43
    Navel: 43
    Waist: 42
    """
    
    fetcher = LatestEmailFetcher()
    result = fetcher.parse_fitness_data(edge_case_email)
    
    above_navel = result['measurements'].get('Above Navel')
    navel = result['measurements'].get('Navel')
    
    print(f"🔍 Edge case - same values:")
    print(f"  Above Navel: {above_navel}")
    print(f"  Navel: {navel}")
    
    if above_navel == navel and above_navel == 43:
        print("✅ SUCCESS: Correctly parsed same values (this is valid)")
        return True
    else:
        print("❌ ERROR: Failed to parse edge case correctly")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Fetcher Agents Test Suite")
    print("=" * 50)
    
    tests = [
        ("Email Parsing", test_email_parsing),
        ("Database Fetcher", test_database_fetcher),
        ("Edge Cases", test_edge_cases)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fetcher agents are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
