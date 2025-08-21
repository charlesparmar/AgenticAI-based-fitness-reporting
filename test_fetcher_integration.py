#!/usr/bin/env python3
"""
Comprehensive Integration Test for Fetcher Agents
Tests both fetcher_agent1_latestemail.py and fetcher_agent2_database.py
with real-world scenarios and edge cases.
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher
from Agents.fetcher_agent2_database import DatabaseFetcher

class TestFetcherAgentIntegration(unittest.TestCase):
    """Comprehensive integration tests for fetcher agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_fetcher = LatestEmailFetcher()
        self.db_fetcher = DatabaseFetcher()
        
        # Sample email data for testing
        self.sample_email_body = """
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
        
        # Sample database entry for testing
        self.sample_db_entry = {
            'id': 1,
            'week_number': 9,
            'weight': 124.4,
            'fat_percentage': 0.514,
            'bmi': 45.7,
            'fat_weight': 64.0,
            'lean_weight': 60.4,
            'neck': 16.0,
            'shoulders': 18.0,
            'biceps': 18.0,
            'forearms': 12.5,
            'chest': 43.0,
            'above_navel': 39.0,
            'navel': 43.0,
            'waist': 42.0,
            'hips': 48.0,
            'thighs': 29.0,
            'calves': 17.0,
            'created_at': '2025-08-21T20:49:56.066857',
            'updated_at': '2025-08-21T20:49:56.066857'
        }

    def test_email_parsing_standard_format(self):
        """Test email parsing with standard format"""
        print("\n🧪 Testing Email Parsing - Standard Format")
        
        result = self.email_fetcher.parse_fitness_data(self.sample_email_body)
        
        # Check that all measurements are parsed
        self.assertIn('measurements', result)
        measurements = result['measurements']
        
        # Verify all expected measurements are present
        expected_measurements = [
            'Week Number', 'Weight', 'Fat Percentage', 'Bmi', 'Fat Weight', 
            'Lean Weight', 'Neck', 'Shoulders', 'Biceps', 'Forearms', 
            'Chest', 'Above Navel', 'Navel', 'Waist', 'Hips', 'Thighs', 'Calves'
        ]
        
        for measurement in expected_measurements:
            self.assertIn(measurement, measurements, f"Missing measurement: {measurement}")
        
        # Verify critical measurements have correct values
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Standard format: {len(measurements)} measurements parsed correctly")

    def test_email_parsing_html_format(self):
        """Test email parsing with HTML format"""
        print("\n🧪 Testing Email Parsing - HTML Format")
        
        html_email_body = f"""
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
        
        result = self.email_fetcher.parse_fitness_data(html_email_body)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ HTML format: {len(measurements)} measurements parsed correctly")

    def test_email_parsing_edge_cases(self):
        """Test email parsing with edge cases"""
        print("\n🧪 Testing Email Parsing - Edge Cases")
        
        # Test case 1: Same values for Above Navel and Navel (valid case)
        edge_case_1 = """
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
        
        result = self.email_fetcher.parse_fitness_data(edge_case_1)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 43)
        self.assertEqual(measurements['Navel'], 43)
        
        # Test case 2: Missing some measurements
        edge_case_2 = """
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34
Measurements:
Week Number: 9
Weight: 124.4
Above Navel: 39
Navel: 43
        """
        
        result = self.email_fetcher.parse_fitness_data(edge_case_2)
        measurements = result['measurements']
        
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Week Number'], 9)
        self.assertEqual(measurements['Weight'], 124.4)
        
        print("✅ Edge cases: All edge cases handled correctly")

    def test_email_parsing_data_types(self):
        """Test that data types are correctly converted"""
        print("\n🧪 Testing Email Parsing - Data Types")
        
        result = self.email_fetcher.parse_fitness_data(self.sample_email_body)
        measurements = result['measurements']
        
        # Test integer values
        self.assertIsInstance(measurements['Week Number'], int)
        self.assertIsInstance(measurements['Neck'], int)
        
        # Test float values
        self.assertIsInstance(measurements['Weight'], float)
        self.assertIsInstance(measurements['Fat Percentage'], float)
        self.assertIsInstance(measurements['Forearms'], float)
        
        print("✅ Data types: All values correctly converted to appropriate types")

    def test_database_fetcher_json_creation(self):
        """Test database fetcher JSON creation"""
        print("\n🧪 Testing Database Fetcher - JSON Creation")
        
        json_data = self.db_fetcher.create_database_json(self.sample_db_entry)
        
        # Verify structure
        self.assertIn('database_info', json_data)
        self.assertIn('email_info', json_data)
        self.assertIn('fitness_data', json_data)
        
        # Verify measurements
        measurements = json_data['fitness_data']['measurements']
        self.assertEqual(measurements['Above Navel'], 39.0)
        self.assertEqual(measurements['Navel'], 43.0)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Database JSON: {len(measurements)} measurements mapped correctly")

    def test_database_fetcher_empty_data(self):
        """Test database fetcher with no existing data"""
        print("\n🧪 Testing Database Fetcher - Empty Data")
        
        json_data = self.db_fetcher.create_database_json(None)
        
        # Verify structure exists
        self.assertIn('database_info', json_data)
        self.assertIn('email_info', json_data)
        self.assertIn('fitness_data', json_data)
        
        # Verify all measurements are None
        measurements = json_data['fitness_data']['measurements']
        for value in measurements.values():
            self.assertIsNone(value)
        
        print("✅ Empty data: JSON structure created correctly with None values")

    def test_critical_measurement_validation(self):
        """Test that Above Navel and Navel are never incorrectly copied"""
        print("\n🧪 Testing Critical Measurement Validation")
        
        # Test multiple scenarios to ensure no copying occurs
        test_cases = [
            ("Different values", 39, 43),
            ("Same values", 43, 43),
            ("Zero values", 0, 0),
            ("Decimal values", 39.5, 43.2)
        ]
        
        for case_name, above_navel_val, navel_val in test_cases:
            test_body = f"""
Fitness Data Entry Date: 21/08/2025
Submitted: 21/08/2025 09:40:34
Measurements:
Week Number: 9
Above Navel: {above_navel_val}
Navel: {navel_val}
            """
            
            result = self.email_fetcher.parse_fitness_data(test_body)
            measurements = result['measurements']
            
            self.assertEqual(measurements['Above Navel'], above_navel_val)
            self.assertEqual(measurements['Navel'], navel_val)
            
            print(f"✅ {case_name}: Above Navel={measurements['Above Navel']}, Navel={measurements['Navel']}")

    def test_json_structure_consistency(self):
        """Test that both agents produce consistent JSON structures"""
        print("\n🧪 Testing JSON Structure Consistency")
        
        # Test email fetcher JSON structure
        email_result = self.email_fetcher.parse_fitness_data(self.sample_email_body)
        email_json = self.email_fetcher.create_fitness_json(email_result, {
            'subject': 'Test',
            'sender': 'test@example.com',
            'date': '2025-08-21',
            'email_id': '123',
            'timestamp': '2025-08-21T20:49:56.066857'
        })
        
        # Test database fetcher JSON structure
        db_json = self.db_fetcher.create_database_json(self.sample_db_entry)
        
        # Verify both have the same top-level structure
        self.assertIn('email_info', email_json)
        self.assertIn('fitness_data', email_json)
        self.assertIn('processed_at', email_json)
        
        self.assertIn('database_info', db_json)
        self.assertIn('email_info', db_json)
        self.assertIn('fitness_data', db_json)
        self.assertIn('processed_at', db_json)
        
        print("✅ JSON structure: Both agents produce consistent structures")

    def test_error_handling(self):
        """Test error handling in both agents"""
        print("\n🧪 Testing Error Handling")
        
        # Test email parsing with malformed data
        malformed_email = """
Invalid format
No measurements here
Random text
        """
        
        result = self.email_fetcher.parse_fitness_data(malformed_email)
        self.assertIn('measurements', result)
        self.assertEqual(len(result['measurements']), 0)
        
        # Test database fetcher with None data
        json_data = self.db_fetcher.create_database_json(None)
        self.assertIsNotNone(json_data)
        self.assertIn('fitness_data', json_data)
        
        print("✅ Error handling: Both agents handle errors gracefully")

    def test_comprehensive_measurement_validation(self):
        """Comprehensive test of all measurement parsing"""
        print("\n🧪 Testing Comprehensive Measurement Validation")
        
        result = self.email_fetcher.parse_fitness_data(self.sample_email_body)
        measurements = result['measurements']
        
        # Define expected values
        expected_values = {
            'Week Number': 9,
            'Weight': 124.4,
            'Fat Percentage': 0.514,
            'Bmi': 45.7,
            'Fat Weight': 64,
            'Lean Weight': 60.4,
            'Neck': 16,
            'Shoulders': 18,
            'Biceps': 18,
            'Forearms': 12.5,
            'Chest': 43,
            'Above Navel': 39,
            'Navel': 43,
            'Waist': 42,
            'Hips': 48,
            'Thighs': 29,
            'Calves': 17
        }
        
        # Verify all expected values
        for measurement, expected_value in expected_values.items():
            self.assertIn(measurement, measurements)
            self.assertEqual(measurements[measurement], expected_value)
        
        print(f"✅ Comprehensive validation: All {len(expected_values)} measurements parsed correctly")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Comprehensive Fetcher Agent Integration Tests")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFetcherAgentIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"📊 Integration Test Results:")
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("🎉 All integration tests passed! Fetcher agents are working correctly.")
        return True
    else:
        print("❌ Some integration tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
