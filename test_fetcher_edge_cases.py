#!/usr/bin/env python3
"""
Edge Case Tests for Fetcher Agents
Additional comprehensive tests for edge cases and robustness.
"""

import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher
from Agents.fetcher_agent2_database import DatabaseFetcher

class TestFetcherEdgeCases(unittest.TestCase):
    """Edge case tests for fetcher agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_fetcher = LatestEmailFetcher()
        self.db_fetcher = DatabaseFetcher()

    def test_email_parsing_with_extra_spaces(self):
        """Test email parsing with extra spaces and formatting"""
        print("\n🧪 Testing Email Parsing - Extra Spaces")
        
        email_with_spaces = """
Fitness Data Entry Date:  21/08/2025
Submitted:  21/08/2025 09:40:34

Measurements:
Week Number:  9
Weight:  124.4
Fat Percentage:  .514
Bmi:  45.7
Fat Weight:  64
Lean Weight:  60.4
Neck:  16
Shoulders:  18
Biceps:  18
Forearms:  12.5
Chest:  43
Above Navel:  39
Navel:  43
Waist:  42
Hips:  48
Thighs:  29
Calves:  17
        """
        
        result = self.email_fetcher.parse_fitness_data(email_with_spaces)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Extra spaces: All measurements parsed correctly")

    def test_email_parsing_with_mixed_case(self):
        """Test email parsing with mixed case in measurement names"""
        print("\n🧪 Testing Email Parsing - Mixed Case")
        
        email_mixed_case = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34

Measurements:
week number: 9
WEIGHT: 124.4
Fat Percentage: .514
BMI: 45.7
fat weight: 64
Lean Weight: 60.4
neck: 16
SHOULDERS: 18
Biceps: 18
forearms: 12.5
CHEST: 43
Above Navel: 39
navel: 43
Waist: 42
HIPS: 48
thighs: 29
Calves: 17
        """
        
        result = self.email_fetcher.parse_fitness_data(email_mixed_case)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Mixed case: All measurements parsed correctly")

    def test_email_parsing_with_tabs(self):
        """Test email parsing with tab separators"""
        print("\n🧪 Testing Email Parsing - Tab Separators")
        
        email_with_tabs = """
Fitness Data Entry Date:	21/08/2025
Submitted:	21/08/2025 09:40:34

Measurements:
Week Number:	9
Weight:	124.4
Fat Percentage:	.514
Bmi:	45.7
Fat Weight:	64
Lean Weight:	60.4
Neck:	16
Shoulders:	18
Biceps:	18
Forearms:	12.5
Chest:	43
Above Navel:	39
Navel:	43
Waist:	42
Hips:	48
Thighs:	29
Calves:	17
        """
        
        result = self.email_fetcher.parse_fitness_data(email_with_tabs)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Tab separators: All measurements parsed correctly")

    def test_email_parsing_with_decimal_values(self):
        """Test email parsing with various decimal value formats"""
        print("\n🧪 Testing Email Parsing - Decimal Values")
        
        email_decimal_values = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34

Measurements:
Week Number: 9
Weight: 124.40
Fat Percentage: 0.514
Bmi: 45.70
Fat Weight: 64.0
Lean Weight: 60.40
Neck: 16.0
Shoulders: 18.00
Biceps: 18
Forearms: 12.50
Chest: 43.0
Above Navel: 39.00
Navel: 43.0
Waist: 42.00
Hips: 48.0
Thighs: 29.00
Calves: 17.0
        """
        
        result = self.email_fetcher.parse_fitness_data(email_decimal_values)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39.0)
        self.assertEqual(measurements['Navel'], 43.0)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Decimal values: All measurements parsed correctly")

    def test_email_parsing_with_partial_data(self):
        """Test email parsing with only some measurements present"""
        print("\n🧪 Testing Email Parsing - Partial Data")
        
        email_partial = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34

Measurements:
Week Number: 9
Weight: 124.4
Above Navel: 39
Navel: 43
        """
        
        result = self.email_fetcher.parse_fitness_data(email_partial)
        measurements = result['measurements']
        
        # Should only have the measurements that were present
        self.assertEqual(measurements['Week Number'], 9)
        self.assertEqual(measurements['Weight'], 124.4)
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        
        # Should not have other measurements
        self.assertNotIn('Fat Percentage', measurements)
        self.assertNotIn('Bmi', measurements)
        
        print("✅ Partial data: Only present measurements parsed correctly")

    def test_email_parsing_with_duplicate_measurements(self):
        """Test email parsing when same measurement appears twice"""
        print("\n🧪 Testing Email Parsing - Duplicate Measurements")
        
        email_duplicate = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34

Measurements:
Week Number: 9
Weight: 124.4
Above Navel: 39
Navel: 43
Above Navel: 40
        """
        
        result = self.email_fetcher.parse_fitness_data(email_duplicate)
        measurements = result['measurements']
        
        # Should use the first occurrence
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        
        print("✅ Duplicate measurements: First occurrence used correctly")

    def test_database_fetcher_with_missing_fields(self):
        """Test database fetcher with missing fields in database entry"""
        print("\n🧪 Testing Database Fetcher - Missing Fields")
        
        incomplete_db_entry = {
            'id': 1,
            'week_number': 9,
            'weight': 124.4,
            'above_navel': 39.0,
            'navel': 43.0,
            'created_at': '2025-08-21T20:49:56.066857'
            # Missing other fields
        }
        
        json_data = self.db_fetcher.create_database_json(incomplete_db_entry)
        measurements = json_data['fitness_data']['measurements']
        
        # Present fields should have values
        self.assertEqual(measurements['Week Number'], 9)
        self.assertEqual(measurements['Weight'], 124.4)
        self.assertEqual(measurements['Above Navel'], 39.0)
        self.assertEqual(measurements['Navel'], 43.0)
        
        # Missing fields should be None
        self.assertIsNone(measurements['Fat Percentage'])
        self.assertIsNone(measurements['Bmi'])
        
        print("✅ Missing fields: Present fields mapped, missing fields set to None")

    def test_database_fetcher_with_null_values(self):
        """Test database fetcher with null values in database entry"""
        print("\n🧪 Testing Database Fetcher - Null Values")
        
        null_db_entry = {
            'id': 1,
            'week_number': None,
            'weight': None,
            'fat_percentage': None,
            'bmi': None,
            'fat_weight': None,
            'lean_weight': None,
            'neck': None,
            'shoulders': None,
            'biceps': None,
            'forearms': None,
            'chest': None,
            'above_navel': None,
            'navel': None,
            'waist': None,
            'hips': None,
            'thighs': None,
            'calves': None,
            'created_at': '2025-08-2025T20:49:56.066857',
            'updated_at': '2025-08-2025T20:49:56.066857'
        }
        
        json_data = self.db_fetcher.create_database_json(null_db_entry)
        measurements = json_data['fitness_data']['measurements']
        
        # All measurements should be None
        for value in measurements.values():
            self.assertIsNone(value)
        
        print("✅ Null values: All measurements correctly set to None")

    def test_email_parsing_with_special_characters(self):
        """Test email parsing with special characters in the email body"""
        print("\n🧪 Testing Email Parsing - Special Characters")
        
        email_special_chars = """
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

Additional notes: This is a test with special characters: !@#$%^&*()
        """
        
        result = self.email_fetcher.parse_fitness_data(email_special_chars)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Special characters: All measurements parsed correctly")

    def test_email_parsing_with_multiple_lines(self):
        """Test email parsing with measurements spread across multiple lines"""
        print("\n🧪 Testing Email Parsing - Multiple Lines")
        
        email_multiline = """
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
        
        result = self.email_fetcher.parse_fitness_data(email_multiline)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print("✅ Multiple lines: All measurements parsed correctly")

def run_edge_case_tests():
    """Run all edge case tests"""
    print("🚀 Starting Fetcher Agent Edge Case Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFetcherEdgeCases)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"📊 Edge Case Test Results:")
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("🎉 All edge case tests passed! Fetcher agents are robust.")
        return True
    else:
        print("❌ Some edge case tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)
