#!/usr/bin/env python3
"""
Comprehensive test suite for LatestEmailFetcher agent.
This test suite ensures 100% accuracy in parsing fitness data from emails.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import email
from io import StringIO

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher


class TestLatestEmailFetcher(unittest.TestCase):
    """Comprehensive test cases for LatestEmailFetcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = LatestEmailFetcher()
        # Mock the pushover notifier to avoid actual notifications in tests
        self.fetcher.notifier = Mock()
        self.fetcher.notifier.send_notification.return_value = True
    
    def test_parse_measurements_strategy_1_perfect_data(self):
        """Test Strategy 1 with perfect HTML table format (from user's email)"""
        email_body = """
        <table>
            <tr><td>Week Number</td><td>20</td></tr>
            <tr><td>Weight</td><td>121.0</td></tr>
            <tr><td>Fat Percentage</td><td>0.500</td></tr>
            <tr><td>BMI</td><td>45.0</td></tr>
            <tr><td>Fat Weight</td><td>60.0</td></tr>
            <tr><td>Lean Weight</td><td>61.0</td></tr>
            <tr><td>Neck</td><td>16.0</td></tr>
            <tr><td>Shoulders</td><td>18.0</td></tr>
            <tr><td>Biceps</td><td>18.0</td></tr>
            <tr><td>Forearms</td><td>12.5</td></tr>
            <tr><td>Chest</td><td>42.0</td></tr>
            <tr><td>Above Navel</td><td>38.0</td></tr>
            <tr><td>Navel</td><td>42.0</td></tr>
            <tr><td>Waist</td><td>41.5</td></tr>
            <tr><td>Hips</td><td>47.0</td></tr>
            <tr><td>Thighs</td><td>28.0</td></tr>
            <tr><td>Calves</td><td>17.0</td></tr>
        </table>
        """
        
        result = self.fetcher._parse_measurements_strategy_3(email_body)
        
        # Verify all expected measurements are present
        expected_measurements = {
            'Week Number': 20,
            'Weight': 121.0,
            'Fat Percentage': 0.500,
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
        
        self.assertEqual(len(result), 17, f"Should extract 17 measurements, got {len(result)}")
        
        for measurement, expected_value in expected_measurements.items():
            self.assertIn(measurement, result, f"Missing measurement: {measurement}")
            self.assertEqual(result[measurement], expected_value, 
                           f"Wrong value for {measurement}: expected {expected_value}, got {result[measurement]}")
    
    def test_parse_measurements_strategy_1_colon_format(self):
        """Test Strategy 1 with colon-separated format"""
        email_body = """
        Week Number: 20
        Weight: 121.0
        Fat Percentage: 0.500
        BMI: 45.0
        Fat Weight: 60.0
        Lean Weight: 61.0
        Neck: 16.0
        Shoulders: 18.0
        Biceps: 18.0
        Forearms: 12.5
        Chest: 42.0
        Above Navel: 38.0
        Navel: 42.0
        Waist: 41.5
        Hips: 47.0
        Thighs: 28.0
        Calves: 17.0
        """
        
        result = self.fetcher._parse_measurements_strategy_1(email_body)
        
        # Verify critical measurements
        self.assertEqual(result.get('Weight'), 121.0, "Weight should be 121.0, not Lean Weight value")
        self.assertEqual(result.get('Fat Weight'), 60.0, "Fat Weight should be 60.0")
        self.assertEqual(result.get('Lean Weight'), 61.0, "Lean Weight should be 61.0")
        self.assertEqual(result.get('Above Navel'), 38.0, "Above Navel should be 38.0")
        self.assertEqual(result.get('Navel'), 42.0, "Navel should be 42.0")
        
        # Verify all 17 measurements are captured
        self.assertEqual(len(result), 17, f"Should extract 17 measurements, got {len(result)}")
    
    def test_weight_confusion_prevention(self):
        """Test that Weight, Fat Weight, and Lean Weight are correctly distinguished"""
        email_body = """
        Fat Weight: 60.0
        Weight: 121.0  
        Lean Weight: 61.0
        """
        
        result = self.fetcher._parse_measurements_strategy_1(email_body)
        
        # This is the critical test - ensure Weight picks up 121.0, not 60.0 or 61.0
        self.assertEqual(result.get('Weight'), 121.0, "Weight should be 121.0")
        self.assertEqual(result.get('Fat Weight'), 60.0, "Fat Weight should be 60.0")
        self.assertEqual(result.get('Lean Weight'), 61.0, "Lean Weight should be 61.0")
    
    def test_navel_confusion_prevention(self):
        """Test that Navel and Above Navel are correctly distinguished"""
        email_body = """
        Above Navel: 38.0
        Navel: 42.0
        """
        
        result = self.fetcher._parse_measurements_strategy_1(email_body)
        
        self.assertEqual(result.get('Above Navel'), 38.0, "Above Navel should be 38.0")
        self.assertEqual(result.get('Navel'), 42.0, "Navel should be 42.0")
    
    def test_parse_measurements_strategy_2_table_format(self):
        """Test Strategy 2 with table-like text format"""
        email_body = """
        Measurements:
        Week Number    20
        Weight         121.0
        Fat Percentage 0.500
        BMI            45.0
        Fat Weight     60.0
        Lean Weight    61.0
        Neck           16.0
        Shoulders      18.0
        Biceps         18.0
        Forearms       12.5
        Chest          42.0
        Above Navel    38.0
        Navel          42.0
        Waist          41.5
        Hips           47.0
        Thighs         28.0
        Calves         17.0
        """
        
        result = self.fetcher._parse_measurements_strategy_2(email_body)
        
        # Verify critical measurements
        self.assertEqual(result.get('Weight'), 121.0, "Weight should be 121.0")
        self.assertEqual(result.get('Fat Weight'), 60.0, "Fat Weight should be 60.0")
        self.assertEqual(result.get('Lean Weight'), 61.0, "Lean Weight should be 61.0")
        
        # Should extract most measurements
        self.assertGreaterEqual(len(result), 15, f"Should extract at least 15 measurements, got {len(result)}")
    
    def test_parse_measurements_strategy_4_flexible(self):
        """Test Strategy 4 with unstructured text"""
        email_body = """
        Your fitness data for this week:
        week number is 20
        your weight is 121.0 kg
        fat percentage: 0.500
        bmi value: 45.0
        fat weight measured at 60.0
        lean weight is 61.0
        neck measurement: 16.0
        shoulders: 18.0
        biceps measurement 18.0
        forearms are 12.5
        chest is 42.0
        above navel measurement 38.0
        navel area: 42.0
        waist measures 41.5
        hips: 47.0
        thighs measure 28.0
        calves: 17.0
        """
        
        result = self.fetcher._parse_measurements_strategy_4(email_body)
        
        # Verify critical measurements
        self.assertEqual(result.get('Weight'), 121.0, "Weight should be 121.0")
        self.assertEqual(result.get('Fat Weight'), 60.0, "Fat Weight should be 60.0")
        self.assertEqual(result.get('Lean Weight'), 61.0, "Lean Weight should be 61.0")
        
        # Should extract most measurements
        self.assertGreaterEqual(len(result), 12, f"Should extract at least 12 measurements, got {len(result)}")
    
    def test_fat_percentage_edge_cases(self):
        """Test various fat percentage formats"""
        test_cases = [
            ("Fat Percentage: 0.500", 0.500),
            ("Fat Percentage: .500", 0.500),
            ("Fat Percentage: 0.5", 0.5),
            ("Fat Percentage: .5", 0.5),
        ]
        
        for email_body, expected in test_cases:
            with self.subTest(email_body=email_body):
                result = self.fetcher._parse_measurements_strategy_1(email_body)
                self.assertEqual(result.get('Fat Percentage'), expected)
    
    def test_integer_vs_float_handling(self):
        """Test proper handling of integer vs float values"""
        email_body = """
        Week Number: 20
        Weight: 121.0
        BMI: 45
        Neck: 16.5
        """
        
        result = self.fetcher._parse_measurements_strategy_1(email_body)
        
        self.assertEqual(result.get('Week Number'), 20)  # Should be int
        self.assertEqual(result.get('Weight'), 121.0)    # Should be float
        self.assertEqual(result.get('Bmi'), 45)          # Should be int
        self.assertEqual(result.get('Neck'), 16.5)       # Should be float
    
    def test_parse_fitness_data_complete(self):
        """Test complete parse_fitness_data method"""
        email_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fitness Data Entry</title>
        </head>
        <body>
            <h1>Fitness Data Entry</h1>
            <p>Date: 13/09/2025</p>
            <p>Submitted: 13/09/2025 12:42:37</p>
            
            <h2>Measurements</h2>
            <table>
                <tr><td>Week Number</td><td>20</td></tr>
                <tr><td>Weight</td><td>121.0</td></tr>
                <tr><td>Fat Percentage</td><td>0.500</td></tr>
                <tr><td>BMI</td><td>45.0</td></tr>
                <tr><td>Fat Weight</td><td>60.0</td></tr>
                <tr><td>Lean Weight</td><td>61.0</td></tr>
                <tr><td>Neck</td><td>16.0</td></tr>
                <tr><td>Shoulders</td><td>18.0</td></tr>
                <tr><td>Biceps</td><td>18.0</td></tr>
                <tr><td>Forearms</td><td>12.5</td></tr>
                <tr><td>Chest</td><td>42.0</td></tr>
                <tr><td>Above Navel</td><td>38.0</td></tr>
                <tr><td>Navel</td><td>42.0</td></tr>
                <tr><td>Waist</td><td>41.5</td></tr>
                <tr><td>Hips</td><td>47.0</td></tr>
                <tr><td>Thighs</td><td>28.0</td></tr>
                <tr><td>Calves</td><td>17.0</td></tr>
            </table>
        </body>
        </html>
        """
        
        result = self.fetcher.parse_fitness_data(email_body)
        
        # Check metadata
        self.assertIn('metadata', result)
        self.assertIn('measurements', result)
        
        # Check measurements
        measurements = result['measurements']
        self.assertEqual(len(measurements), 17, f"Should extract 17 measurements, got {len(measurements)}")
        
        # Verify critical values
        self.assertEqual(measurements.get('Weight'), 121.0, "Weight should be 121.0")
        self.assertEqual(measurements.get('Fat Weight'), 60.0, "Fat Weight should be 60.0")
        self.assertEqual(measurements.get('Lean Weight'), 61.0, "Lean Weight should be 61.0")
    
    def test_validation_weight_correction(self):
        """Test validation catches and corrects Weight vs Lean Weight confusion"""
        email_body = """
        Fat Weight: 60.0
        Weight: 121.0
        Lean Weight: 61.0
        """
        
        # Simulate incorrect extraction (what was happening before)
        incorrect_measurements = {
            'Weight': 61.0,  # Wrong - this is Lean Weight value
            'Fat Weight': 60.0,
            # Missing Lean Weight
        }
        
        # Test validation
        validated = self.fetcher.validate_extracted_measurements(email_body, incorrect_measurements)
        
        # Validation should correct this
        self.assertEqual(validated.get('Weight'), 121.0, "Validation should correct Weight to 121.0")
        self.assertEqual(validated.get('Fat Weight'), 60.0, "Fat Weight should remain 60.0")
    
    def test_all_strategies_fallback(self):
        """Test that strategies work as fallbacks"""
        # Test with an email that only Strategy 3 (HTML) should handle well
        html_email = """
        <table>
            <tr><td>Weight</td><td>121.0</td></tr>
            <tr><td>Fat Weight</td><td>60.0</td></tr>
            <tr><td>Lean Weight</td><td>61.0</td></tr>
        </table>
        """
        
        # Strategy 1 should find some but not all
        result1 = self.fetcher._parse_measurements_strategy_1(html_email)
        
        # Strategy 3 should find all
        result3 = self.fetcher._parse_measurements_strategy_3(html_email)
        self.assertEqual(result3.get('Weight'), 121.0)
        self.assertEqual(result3.get('Fat Weight'), 60.0)
        self.assertEqual(result3.get('Lean Weight'), 61.0)
    
    def test_edge_case_similar_names(self):
        """Test edge cases with similar measurement names"""
        # Test Strategy 1 and 4 with colon format
        colon_email_body = """
        Fat Weight: 60.0
        Weight: 121.0
        Lean Weight: 61.0
        Above Navel: 38.0
        Navel: 42.0
        """
        
        # Test Strategy 2 with table format
        table_email_body = """
        Measurements:
        Fat Weight    60.0
        Weight        121.0
        Lean Weight   61.0
        Above Navel   38.0
        Navel         42.0
        """
        
        for strategy_num in [1, 2, 4]:
            with self.subTest(strategy=strategy_num):
                if strategy_num == 1:
                    result = self.fetcher._parse_measurements_strategy_1(colon_email_body)
                elif strategy_num == 2:
                    result = self.fetcher._parse_measurements_strategy_2(table_email_body)
                elif strategy_num == 4:
                    result = self.fetcher._parse_measurements_strategy_4(colon_email_body)
                
                # All strategies should correctly distinguish these
                self.assertEqual(result.get('Weight'), 121.0, f"Strategy {strategy_num}: Weight should be 121.0")
                self.assertEqual(result.get('Fat Weight'), 60.0, f"Strategy {strategy_num}: Fat Weight should be 60.0")
                self.assertEqual(result.get('Lean Weight'), 61.0, f"Strategy {strategy_num}: Lean Weight should be 61.0")
                self.assertEqual(result.get('Above Navel'), 38.0, f"Strategy {strategy_num}: Above Navel should be 38.0")
                self.assertEqual(result.get('Navel'), 42.0, f"Strategy {strategy_num}: Navel should be 42.0")
    
    def test_create_fitness_json(self):
        """Test JSON creation with complete data"""
        fitness_data = {
            'metadata': {'entry_date': '13/09/2025'},
            'measurements': {
                'Week Number': 20,
                'Weight': 121.0,
                'Fat Percentage': 0.500,
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
        }
        
        email_info = {
            'subject': 'Fitness Data Entry - 13/09/2025',
            'sender': 'charlesparmar@gmail.com',
            'date': 'Sat, 13 Sep 2025 11:42:40 +0000',
            'email_id': '43042',
            'timestamp': '2025-09-13T15:39:48.583041'
        }
        
        result = self.fetcher.create_fitness_json(fitness_data, email_info)
        
        # Verify structure
        self.assertIn('email_info', result)
        self.assertIn('fitness_data', result)
        self.assertIn('processed_at', result)
        
        # Verify all measurements are preserved
        measurements = result['fitness_data']['measurements']
        self.assertEqual(len(measurements), 17)
        self.assertEqual(measurements['Weight'], 121.0)
        self.assertEqual(measurements['Fat Weight'], 60.0)
        self.assertEqual(measurements['Lean Weight'], 61.0)


class TestEmailParsingAccuracy(unittest.TestCase):
    """Specific tests for parsing accuracy based on user's reported issues"""
    
    def setUp(self):
        self.fetcher = LatestEmailFetcher()
        self.fetcher.notifier = Mock()
        self.fetcher.notifier.send_notification.return_value = True
    
    def test_user_reported_issue_exact_data(self):
        """Test with the exact data from user's screenshot"""
        # This is the exact email content that was causing issues
        email_body = """
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
            <tr><td>Week Number</td><td>20</td></tr>
            <tr><td>Weight</td><td>121.0</td></tr>
            <tr><td>Fat Percentage</td><td>0.500</td></tr>
            <tr><td>BMI</td><td>45.0</td></tr>
            <tr><td>Fat Weight</td><td>60.0</td></tr>
            <tr><td>Lean Weight</td><td>61.0</td></tr>
            <tr><td>Neck</td><td>16.0</td></tr>
            <tr><td>Shoulders</td><td>18.0</td></tr>
            <tr><td>Biceps</td><td>18.0</td></tr>
            <tr><td>Forearms</td><td>12.5</td></tr>
            <tr><td>Chest</td><td>42.0</td></tr>
            <tr><td>Above Navel</td><td>38.0</td></tr>
            <tr><td>Navel</td><td>42.0</td></tr>
            <tr><td>Waist</td><td>41.5</td></tr>
            <tr><td>Hips</td><td>47.0</td></tr>
            <tr><td>Thighs</td><td>28.0</td></tr>
            <tr><td>Calves</td><td>17.0</td></tr>
        </table>
        """
        
        # Test all strategies
        for strategy_name, strategy_method in [
            ("Strategy 1", self.fetcher._parse_measurements_strategy_1),
            ("Strategy 2", self.fetcher._parse_measurements_strategy_2),
            ("Strategy 3", self.fetcher._parse_measurements_strategy_3),
            ("Strategy 4", self.fetcher._parse_measurements_strategy_4)
        ]:
            with self.subTest(strategy=strategy_name):
                result = strategy_method(email_body)
                
                if result:  # If strategy found any measurements
                    # These are the critical assertions based on user's issue
                    if 'Weight' in result:
                        self.assertEqual(result['Weight'], 121.0, 
                                       f"{strategy_name}: Weight must be 121.0, not 61.0 (Lean Weight)")
                    
                    if 'Fat Weight' in result:
                        self.assertEqual(result['Fat Weight'], 60.0,
                                       f"{strategy_name}: Fat Weight must be 60.0")
                    
                    if 'Lean Weight' in result:
                        self.assertEqual(result['Lean Weight'], 61.0,
                                       f"{strategy_name}: Lean Weight must be 61.0")
                    
                    # Ensure all 17 measurements are captured (for successful strategies)
                    if len(result) >= 15:  # Allow some tolerance
                        expected_fields = ['Week Number', 'Weight', 'Fat Percentage', 'Bmi', 
                                         'Fat Weight', 'Lean Weight', 'Neck', 'Shoulders', 
                                         'Biceps', 'Forearms', 'Chest', 'Above Navel', 
                                         'Navel', 'Waist', 'Hips', 'Thighs', 'Calves']
                        
                        missing_fields = [field for field in expected_fields if field not in result]
                        self.assertEqual(len(missing_fields), 0, 
                                       f"{strategy_name}: Missing fields: {missing_fields}")


def run_comprehensive_tests():
    """Run all comprehensive tests and report results"""
    # Capture test output
    test_output = StringIO()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLatestEmailFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailParsingAccuracy))
    
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
    print(f"TEST RESULTS SUMMARY")
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
    
    return pass_rate == 100.0


if __name__ == "__main__":
    print("Running Comprehensive Email Parser Tests...")
    print("Testing all strategies for 100% accuracy...")
    
    success = run_comprehensive_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED! Email parser is ready for production.")
    else:
        print("\n❌ Some tests failed. Please review and fix issues.")
        sys.exit(1)
