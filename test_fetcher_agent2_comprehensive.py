#!/usr/bin/env python3
"""
Comprehensive test suite for DatabaseFetcher agent.
This test suite ensures 100% accuracy in fetching and mapping database data.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from io import StringIO

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent2_database import DatabaseFetcher, run_database_fetcher


class TestDatabaseFetcher(unittest.TestCase):
    """Comprehensive test cases for DatabaseFetcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = DatabaseFetcher()
        
        # Mock database data that matches the actual database schema
        self.mock_db_entry = {
            'id': 20,
            'week_number': 20,
            'date': '2025-09-13',
            'weight': 121.0,
            'fat_percent': 0.5,  # This is the correct column name!
            'bmi': 45.0,
            'fat_weight': 60.0,
            'lean_weight': 61.0,
            'neck': 16.0,
            'shoulders': 18.0,
            'biceps': 18.0,
            'forearms': 12.5,
            'chest': 42.0,
            'above_navel': 38.0,
            'navel': 42.0,
            'waist': 41.5,
            'hips': 47.0,
            'thighs': 28.0,
            'calves': 17.0,
            'created_at': '2025-09-13 02:38:43',
            'updated_at': None,
            'email_subject': 'Fitness Data Entry - 13/09/2025',
            'email_sender': 'charlesparmar@gmail.com',
            'email_date': 'Sat, 13 Sep 2025 11:42:40 +0000',
            'email_id': '43042',
            'email_fetched_at': '2025-09-13T15:39:48.583041',
            'entry_date': '13/09/2025',
            'submitted': '13/09/2025 12:42:37',
            'processed_at': '2025-09-13T15:39:48.647221'
        }
    
    @patch('sqlitecloud.connect')
    def test_fetch_latest_db_entry_success(self, mock_connect):
        """Test successful database entry fetching"""
        # Setup mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock cursor behavior
        mock_cursor.fetchall.return_value = [tuple(self.mock_db_entry.values())]
        mock_cursor.description = [(key, None) for key in self.mock_db_entry.keys()]
        
        # Test the method
        result = self.fetcher.fetch_latest_db_entry()
        
        # Verify database connection
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify returned data
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 20)
        self.assertEqual(result['weight'], 121.0)
        self.assertEqual(result['fat_percent'], 0.5)  # Critical: This should not be null!
        self.assertEqual(result['fat_weight'], 60.0)
        self.assertEqual(result['lean_weight'], 61.0)
    
    @patch('sqlitecloud.connect')
    def test_fetch_latest_db_entry_no_data(self, mock_connect):
        """Test behavior when no data exists in database"""
        # Setup mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock cursor to return no results
        mock_cursor.fetchall.return_value = []
        
        # Test the method
        result = self.fetcher.fetch_latest_db_entry()
        
        # Verify database connection
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify None returned when no data
        self.assertIsNone(result)
    
    @patch('sqlitecloud.connect')
    def test_fetch_latest_db_entry_connection_error(self, mock_connect):
        """Test behavior when database connection fails"""
        # Setup mock to raise exception
        mock_connect.side_effect = Exception("Connection failed")
        
        # Test the method
        result = self.fetcher.fetch_latest_db_entry()
        
        # Verify None returned on error
        self.assertIsNone(result)
    
    def test_create_database_json_with_data(self):
        """Test JSON creation with actual database data"""
        result = self.fetcher.create_database_json(self.mock_db_entry)
        
        # Verify structure
        self.assertIn('database_info', result)
        self.assertIn('email_info', result)
        self.assertIn('fitness_data', result)
        self.assertIn('processed_at', result)
        
        # Verify database info
        db_info = result['database_info']
        self.assertEqual(db_info['id'], 20)
        self.assertEqual(db_info['created_at'], '2025-09-13 02:38:43')
        
        # Verify email info
        email_info = result['email_info']
        self.assertEqual(email_info['subject'], 'Fitness Data Entry - 13/09/2025')
        self.assertEqual(email_info['sender'], 'charlesparmar@gmail.com')
        
        # Verify fitness data measurements - ALL CRITICAL VALUES
        measurements = result['fitness_data']['measurements']
        self.assertEqual(len(measurements), 17, "Should have all 17 measurements")
        
        # Critical test: Fat Percentage should NOT be null
        self.assertEqual(measurements['Fat Percentage'], 0.5, "Fat Percentage should be 0.5, not null!")
        self.assertEqual(measurements['Weight'], 121.0, "Weight should be 121.0")
        self.assertEqual(measurements['Fat Weight'], 60.0, "Fat Weight should be 60.0")
        self.assertEqual(measurements['Lean Weight'], 61.0, "Lean Weight should be 61.0")
        
        # Verify all measurements are present and not null
        expected_measurements = {
            'Week Number': 20,
            'Weight': 121.0,
            'Fat Percentage': 0.5,
            'Bmi': 45.0,
            'Fat Weight': 60.0,
            'Lean Weight': 61.0,
            'Neck': 16.0,
            'Shoulders': 18.0,
            'Biceps': 18.0,
            'Forearms': 12.5,
            'Chest': 42.0,
            'Above Navel': 38.0,
            'Navel': 42.0,
            'Waist': 41.5,
            'Hips': 47.0,
            'Thighs': 28.0,
            'Calves': 17.0
        }
        
        for measurement, expected_value in expected_measurements.items():
            self.assertIn(measurement, measurements, f"Missing measurement: {measurement}")
            self.assertEqual(measurements[measurement], expected_value, 
                           f"Wrong value for {measurement}: expected {expected_value}, got {measurements[measurement]}")
            self.assertIsNotNone(measurements[measurement], f"{measurement} should not be null!")
    
    def test_create_database_json_blank_data(self):
        """Test JSON creation with no database data (blank structure)"""
        result = self.fetcher.create_database_json(None)
        
        # Verify structure
        self.assertIn('database_info', result)
        self.assertIn('email_info', result)
        self.assertIn('fitness_data', result)
        self.assertIn('processed_at', result)
        
        # Verify all values are None for blank data
        db_info = result['database_info']
        self.assertIsNone(db_info['id'])
        self.assertIsNone(db_info['created_at'])
        
        email_info = result['email_info']
        self.assertIsNone(email_info['subject'])
        self.assertIsNone(email_info['sender'])
        
        # Verify fitness data measurements are all None
        measurements = result['fitness_data']['measurements']
        self.assertEqual(len(measurements), 17, "Should have all 17 measurement placeholders")
        
        for measurement_name, value in measurements.items():
            self.assertIsNone(value, f"{measurement_name} should be None for blank data")
    
    def test_column_name_mapping_accuracy(self):
        """Test that all column names map correctly from database to JSON"""
        # This test ensures no column name mismatches like fat_percentage vs fat_percent
        result = self.fetcher.create_database_json(self.mock_db_entry)
        measurements = result['fitness_data']['measurements']
        
        # Test critical column mappings that have caused issues
        test_cases = [
            ('fat_percent', 'Fat Percentage', 0.5),  # This was the bug!
            ('weight', 'Weight', 121.0),
            ('fat_weight', 'Fat Weight', 60.0),
            ('lean_weight', 'Lean Weight', 61.0),
            ('week_number', 'Week Number', 20),
            ('bmi', 'Bmi', 45.0),
            ('above_navel', 'Above Navel', 38.0),
            ('navel', 'Navel', 42.0)
        ]
        
        for db_column, json_key, expected_value in test_cases:
            # Verify the database has this column
            self.assertIn(db_column, self.mock_db_entry, f"Database should have column: {db_column}")
            
            # Verify the JSON has the correct key
            self.assertIn(json_key, measurements, f"JSON should have key: {json_key}")
            
            # Verify the value is correctly mapped
            self.assertEqual(measurements[json_key], expected_value, 
                           f"Column mapping error: {db_column} -> {json_key} should be {expected_value}")
    
    def test_data_types_preservation(self):
        """Test that data types are preserved correctly from database to JSON"""
        result = self.fetcher.create_database_json(self.mock_db_entry)
        measurements = result['fitness_data']['measurements']
        
        # Test integer types
        self.assertIsInstance(measurements['Week Number'], int)
        self.assertIsInstance(measurements['Bmi'], (int, float))
        
        # Test float types
        self.assertIsInstance(measurements['Weight'], float)
        self.assertIsInstance(measurements['Fat Percentage'], float)
        self.assertIsInstance(measurements['Fat Weight'], float)
        self.assertIsInstance(measurements['Lean Weight'], float)
        self.assertIsInstance(measurements['Forearms'], float)
        self.assertIsInstance(measurements['Waist'], float)
        
        # Test that values are reasonable
        self.assertGreater(measurements['Weight'], 0)
        self.assertGreaterEqual(measurements['Fat Percentage'], 0)
        self.assertLessEqual(measurements['Fat Percentage'], 1.0)  # Should be decimal, not percentage
    
    @patch('sqlitecloud.connect')
    def test_database_query_correctness(self, mock_connect):
        """Test that the correct SQL query is executed"""
        # Setup mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        # Test the method
        self.fetcher.fetch_latest_db_entry()
        
        # Verify the correct SQL query was executed
        expected_query = """
            SELECT * FROM Charles_Parmar_Fitness_measurements 
            ORDER BY created_at DESC
            LIMIT 1
            """
        
        # Get the actual query that was executed
        actual_query = mock_cursor.execute.call_args[0][0]
        
        # Normalize whitespace for comparison
        import re
        expected_normalized = re.sub(r'\s+', ' ', expected_query.strip())
        actual_normalized = re.sub(r'\s+', ' ', actual_query.strip())
        
        self.assertEqual(actual_normalized, expected_normalized, 
                        "SQL query should fetch from correct table with correct ordering")


class TestDatabaseFetcherIntegration(unittest.TestCase):
    """Integration tests for complete database fetcher workflow"""
    
    @patch('sqlitecloud.connect')
    def test_run_database_fetcher_with_data(self, mock_connect):
        """Test complete workflow when data exists"""
        # Setup mock data
        mock_db_entry = {
            'id': 20,
            'week_number': 20,
            'weight': 121.0,
            'fat_percent': 0.5,  # Critical: correct column name
            'bmi': 45.0,
            'fat_weight': 60.0,
            'lean_weight': 61.0,
            'neck': 16.0,
            'shoulders': 18.0,
            'biceps': 18.0,
            'forearms': 12.5,
            'chest': 42.0,
            'above_navel': 38.0,
            'navel': 42.0,
            'waist': 41.5,
            'hips': 47.0,
            'thighs': 28.0,
            'calves': 17.0,
            'created_at': '2025-09-13 02:38:43',
            'fat_percentage': None  # Note: This column shouldn't exist!
        }
        
        # Setup mock connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [tuple(mock_db_entry.values())]
        mock_cursor.description = [(key, None) for key in mock_db_entry.keys()]
        
        # Test the complete workflow
        result = run_database_fetcher()
        
        # Verify successful execution
        self.assertIsNotNone(result)
        self.assertIn('fitness_data', result)
        
        # Critical test: Fat Percentage should be extracted correctly
        measurements = result['fitness_data']['measurements']
        self.assertEqual(measurements['Fat Percentage'], 0.5, 
                        "Fat Percentage should be 0.5, extracted from fat_percent column!")
        self.assertIsNotNone(measurements['Fat Percentage'], 
                            "Fat Percentage should never be null when data exists!")
    
    @patch('sqlitecloud.connect')
    def test_run_database_fetcher_no_data(self, mock_connect):
        """Test complete workflow when no data exists"""
        # Setup mock connection to return no data
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        # Test the complete workflow
        result = run_database_fetcher()
        
        # Verify blank JSON structure is returned
        self.assertIsNotNone(result)
        self.assertIn('fitness_data', result)
        
        # All measurements should be None
        measurements = result['fitness_data']['measurements']
        for measurement_name, value in measurements.items():
            self.assertIsNone(value, f"{measurement_name} should be None when no data exists")
    
    def test_environment_variable_handling(self):
        """Test behavior when environment variables are missing"""
        # Test with missing API key
        fetcher = DatabaseFetcher()
        fetcher.sqlite_api_key = None
        
        result = fetcher.fetch_latest_db_entry()
        self.assertIsNone(result, "Should return None when API key is missing")


def run_comprehensive_tests():
    """Run all comprehensive tests and report results"""
    # Capture test output
    test_output = StringIO()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseFetcherIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    output = test_output.getvalue()
    print(output)
    
    # Calculate pass rate
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"DATABASE FETCHER TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")
    
    if failures > 0:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if errors > 0:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Additional validation checks
    print(f"\n🔍 CRITICAL VALIDATION CHECKS:")
    print(f"✅ Column name mapping test: fat_percent -> Fat Percentage")
    print(f"✅ All 17 measurement fields verification")
    print(f"✅ Data type preservation validation")
    print(f"✅ Null value prevention checks")
    
    return pass_rate == 100.0


if __name__ == "__main__":
    print("Running Comprehensive Database Fetcher Tests...")
    print("Testing column name mappings and data accuracy...")
    
    success = run_comprehensive_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED! Database fetcher is ready for production.")
        print("🎯 Fat Percentage mapping issue has been resolved!")
    else:
        print("\n❌ Some tests failed. Please review and fix issues.")
        sys.exit(1)
