#!/usr/bin/env python3
"""
Debug test for email parsing to understand why measurements are empty
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher

def test_email_parsing_with_actual_format():
    """Test with the actual email format from the image"""
    print("🧪 Testing Email Parsing with Actual Format...")
    
    # This is the actual format from the email image you showed
    actual_email_body = """
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
    result = fetcher.parse_fitness_data(actual_email_body)
    
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

def test_email_parsing_with_html_format():
    """Test with HTML format that might be in the actual email"""
    print("\n🧪 Testing Email Parsing with HTML Format...")
    
    # Simulate HTML email format
    html_email_body = """
<html>
<body>
<p>Fitness Data Entry Date: 21/08/2025</p>
<p>Submitted: 21/08/2025 09:40:34</p>
<p>Measurements:</p>
<p>Week Number: 9</p>
<p>Weight: 124.4</p>
<p>Fat Percentage: .514</p>
<p>Bmi: 45.7</p>
<p>Fat Weight: 64</p>
<p>Lean Weight: 60.4</p>
<p>Neck: 16</p>
<p>Shoulders: 18</p>
<p>Biceps: 18</p>
<p>Forearms: 12.5</p>
<p>Chest: 43</p>
<p>Above Navel: 39</p>
<p>Navel: 43</p>
<p>Waist: 42</p>
<p>Hips: 48</p>
<p>Thighs: 29</p>
<p>Calves: 17</p>
</body>
</html>
    """
    
    fetcher = LatestEmailFetcher()
    result = fetcher.parse_fitness_data(html_email_body)
    
    print(f"📊 Parsed measurements:")
    for key, value in result['measurements'].items():
        print(f"  {key}: {value}")
    
    return len(result['measurements']) > 0

def test_email_parsing_with_table_format():
    """Test with table format that might be in the actual email"""
    print("\n🧪 Testing Email Parsing with Table Format...")
    
    # Simulate table format
    table_email_body = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34

Measurements:
Measurement	Value
Week Number	9
Weight	124.4
Fat Percentage	.514
Bmi	45.7
Fat Weight	64
Lean Weight	60.4
Neck	16
Shoulders	18
Biceps	18
Forearms	12.5
Chest	43
Above Navel	39
Navel	43
Waist	42
Hips	48
Thighs	29
Calves	17
    """
    
    fetcher = LatestEmailFetcher()
    result = fetcher.parse_fitness_data(table_email_body)
    
    print(f"📊 Parsed measurements:")
    for key, value in result['measurements'].items():
        print(f"  {key}: {value}")
    
    return len(result['measurements']) > 0

def main():
    """Run all debug tests"""
    print("🚀 Starting Email Parsing Debug Tests")
    print("=" * 50)
    
    tests = [
        ("Actual Format", test_email_parsing_with_actual_format),
        ("HTML Format", test_email_parsing_with_html_format),
        ("Table Format", test_email_parsing_with_table_format)
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
        print("🎉 All tests passed! The email parsing should work correctly.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
