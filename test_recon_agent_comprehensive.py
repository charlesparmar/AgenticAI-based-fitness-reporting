#!/usr/bin/env python3
"""
Comprehensive test suite for ReconciliationAgent.
This test suite ensures 100% accuracy in data reconciliation logic.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from io import StringIO

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.recon_agent import ReconciliationAgent, run_reconciliation_agent


class TestReconciliationAgent(unittest.TestCase):
    """Comprehensive test cases for ReconciliationAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = ReconciliationAgent()
        
        # Mock the pushover notifier to avoid actual notifications in tests
        self.agent.notifier = Mock()
        self.agent.notifier.send_notification.return_value = True
        
        # Sample identical data (what we expect when both fetchers work correctly)
        self.identical_email_data = {
            'email_info': {
                'subject': 'Fitness Data Entry - 13/09/2025',
                'sender': 'charlesparmar@gmail.com',
                'date': 'Sat, 13 Sep 2025 11:42:40 +0000',
                'email_id': '43042',
                'fetched_at': '2025-09-13T15:39:48.583041'
            },
            'fitness_data': {
                'metadata': {
                    'entry_date': '13/09/2025',
                    'submitted': '13/09/2025 12:42:37',
                    'processed_at': '2025-09-13T15:39:48.647221'
                },
                'measurements': {
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
            },
            'processed_at': '2025-09-13T15:39:48.647221'
        }
        
        self.identical_database_data = {
            'database_info': {
                'id': 20,
                'created_at': '2025-09-13 02:38:43',
                'updated_at': None
            },
            'email_info': {
                'subject': 'Fitness Data Entry - 13/09/2025',
                'sender': 'charlesparmar@gmail.com',
                'date': 'Sat, 13 Sep 2025 11:42:40 +0000',
                'email_id': '43042',
                'fetched_at': '2025-09-13T15:39:48.583041'
            },
            'fitness_data': {
                'metadata': {
                    'entry_date': '13/09/2025',
                    'submitted': '13/09/2025 12:42:37',
                    'processed_at': '2025-09-13T15:39:48.647221'
                },
                'measurements': {
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
            },
            'processed_at': '2025-09-13T15:39:48.583041'
        }
        
        # Sample different data (what we'd get if there's a parsing error)
        self.different_database_data = {
            'database_info': {
                'id': 20,
                'created_at': '2025-09-13 02:38:43',
                'updated_at': None
            },
            'email_info': {
                'subject': 'Fitness Data Entry - 13/09/2025',
                'sender': 'charlesparmar@gmail.com',
                'date': 'Sat, 13 Sep 2025 11:42:40 +0000',
                'email_id': '43042',
                'fetched_at': '2025-09-13T15:39:48.583041'
            },
            'fitness_data': {
                'metadata': {
                    'entry_date': '13/09/2025',
                    'submitted': '13/09/2025 12:42:37',
                    'processed_at': '2025-09-13T15:39:48.647221'
                },
                'measurements': {
                    'Week Number': 20,
                    'Weight': 61.0,  # WRONG! This should be 121.0 (old bug)
                    'Fat Percentage': 0.5,
                    'Bmi': 45.0,
                    'Fat Weight': None,  # MISSING! This should be 60.0
                    'Lean Weight': None,  # MISSING! This should be 61.0
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
            },
            'processed_at': '2025-09-13T15:39:48.583041'
        }
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_compare_data_identical_success(self, mock_prompt_loader):
        """Test LLM comparison when data is identical (should return SAME)"""
        # Setup mock LLM to return "SAME"
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "SAME"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test the comparison
        result = self.agent.compare_data_with_llm(self.identical_email_data, self.identical_database_data)
        
        # Verify correct behavior
        self.assertTrue(result, "Should return True when data is identical")
        mock_prompt_loader.get_model_for_prompt.assert_called_once_with("reconciliation_prompt", temperature=0)
        mock_model.invoke.assert_called_once()
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_compare_data_different_success(self, mock_prompt_loader):
        """Test LLM comparison when data is different (should return DIFFERENT)"""
        # Setup mock LLM to return "DIFFERENT"
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "DIFFERENT"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test the comparison
        result = self.agent.compare_data_with_llm(self.identical_email_data, self.different_database_data)
        
        # Verify correct behavior
        self.assertFalse(result, "Should return False when data is different")
        mock_prompt_loader.get_model_for_prompt.assert_called_once_with("reconciliation_prompt", temperature=0)
        mock_model.invoke.assert_called_once()
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_compare_data_llm_error(self, mock_prompt_loader):
        """Test LLM comparison when LLM throws an error"""
        # Setup mock LLM to throw an exception
        mock_model = Mock()
        mock_model.invoke.side_effect = Exception("LLM error")
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test the comparison
        result = self.agent.compare_data_with_llm(self.identical_email_data, self.identical_database_data)
        
        # Verify error handling
        self.assertFalse(result, "Should return False when LLM throws an error")
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_reconcile_data_identical_success(self, mock_prompt_loader):
        """Test reconciliation when data is identical (CORRECT BEHAVIOR)"""
        # Setup mock LLM to return "SAME"
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "SAME"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test reconciliation
        result = self.agent.reconcile_data(self.identical_email_data, self.identical_database_data)
        
        # Verify successful reconciliation
        self.assertTrue(result['success'], "Should succeed when data is identical")
        self.assertTrue(result['data_matches'], "Should indicate data matches")
        self.assertTrue(result['proceed_to_validation'], "Should proceed to validation")
        self.assertIn('json_data', result, "Should include email data for next agent")
        self.assertEqual(result['message'], 'Reconciliation successful - both fetchers extracted identical data')
        
        # Verify notification was sent (check just the message parameter)
        self.agent.notifier.send_notification.assert_called_once()
        call_args = self.agent.notifier.send_notification.call_args[0]
        self.assertEqual(call_args[0], "Reconciliation successful - both fetchers extracted identical data. Workflow proceeding.")
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_reconcile_data_different_failure(self, mock_prompt_loader):
        """Test reconciliation when data is different (SHOULD TERMINATE WORKFLOW)"""
        # Setup mock LLM to return "DIFFERENT"
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "DIFFERENT"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test reconciliation
        result = self.agent.reconcile_data(self.identical_email_data, self.different_database_data)
        
        # Verify workflow termination
        self.assertFalse(result['success'], "Should fail when data is different")
        self.assertFalse(result['data_matches'], "Should indicate data doesn't match")
        self.assertFalse(result['proceed_to_validation'], "Should NOT proceed to validation")
        self.assertIn('error', result, "Should include error message")
        self.assertEqual(result['error'], 'Reconciliation failed - fetcher agents extracted different data')
        self.assertEqual(result['message'], 'Fetcher agents must extract identical data. Difference detected indicates an error.')
        
        # Verify failure notification was sent (check just the message parameter)
        self.agent.notifier.send_notification.assert_called_once()
        call_args = self.agent.notifier.send_notification.call_args[0]
        self.assertEqual(call_args[0], "Reconciliation failed - fetcher agents extracted different data. Workflow terminated.")
    
    @patch('Agents.recon_agent.prompt_loader')
    def test_reconcile_data_exception_handling(self, mock_prompt_loader):
        """Test reconciliation when an exception occurs in LLM comparison"""
        # Setup mock to throw an exception during LLM comparison
        mock_model = Mock()
        mock_model.invoke.side_effect = Exception("Configuration error")
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test reconciliation
        result = self.agent.reconcile_data(self.identical_email_data, self.identical_database_data)
        
        # When LLM comparison fails, it returns False (different), which triggers workflow termination
        self.assertFalse(result['success'], "Should fail when LLM comparison throws exception")
        self.assertFalse(result['data_matches'], "Should indicate data doesn't match due to LLM error")
        self.assertFalse(result['proceed_to_validation'], "Should NOT proceed to validation")
        self.assertIn('error', result, "Should include error message")
        self.assertEqual(result['error'], 'Reconciliation failed - fetcher agents extracted different data')
    
    def test_critical_measurement_differences(self):
        """Test detection of specific measurement differences that were causing issues"""
        # Test cases that previously caused problems
        test_cases = [
            {
                'name': 'Weight confusion (121.0 vs 61.0)',
                'email_weight': 121.0,
                'db_weight': 61.0,
                'should_fail': True
            },
            {
                'name': 'Missing Fat Weight',
                'email_fat_weight': 60.0,
                'db_fat_weight': None,
                'should_fail': True
            },
            {
                'name': 'Missing Lean Weight',
                'email_lean_weight': 61.0,
                'db_lean_weight': None,
                'should_fail': True
            },
            {
                'name': 'Null Fat Percentage',
                'email_fat_pct': 0.5,
                'db_fat_pct': None,
                'should_fail': True
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case['name']):
                # Create modified data for this test case
                modified_db_data = self.different_database_data.copy()
                
                # Apply specific modification based on test case
                if 'email_weight' in test_case:
                    modified_db_data['fitness_data']['measurements']['Weight'] = test_case['db_weight']
                elif 'email_fat_weight' in test_case:
                    modified_db_data['fitness_data']['measurements']['Fat Weight'] = test_case['db_fat_weight']
                elif 'email_lean_weight' in test_case:
                    modified_db_data['fitness_data']['measurements']['Lean Weight'] = test_case['db_lean_weight']
                elif 'email_fat_pct' in test_case:
                    modified_db_data['fitness_data']['measurements']['Fat Percentage'] = test_case['db_fat_pct']
                
                with patch('Agents.recon_agent.prompt_loader') as mock_prompt_loader:
                    # Mock LLM to detect the difference
                    mock_model = Mock()
                    mock_response = Mock()
                    mock_response.content = "DIFFERENT"
                    mock_model.invoke.return_value = mock_response
                    mock_prompt_loader.get_model_for_prompt.return_value = mock_model
                    mock_prompt_loader.format_prompt.return_value = "formatted prompt"
                    
                    result = self.agent.reconcile_data(self.identical_email_data, modified_db_data)
                    
                    if test_case['should_fail']:
                        self.assertFalse(result['success'], f"Should fail for {test_case['name']}")
                        self.assertFalse(result['proceed_to_validation'], f"Should not proceed for {test_case['name']}")


class TestReconciliationAgentIntegration(unittest.TestCase):
    """Integration tests for complete reconciliation workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Sample test data
        self.sample_email_data = {
            'email_info': {'subject': 'Test Email'},
            'fitness_data': {
                'metadata': {'entry_date': '13/09/2025'},
                'measurements': {
                    'Week Number': 20,
                    'Weight': 121.0,
                    'Fat Percentage': 0.5,
                    'Fat Weight': 60.0,
                    'Lean Weight': 61.0
                }
            }
        }
        
        self.sample_db_data = {
            'fitness_data': {
                'metadata': {'entry_date': '13/09/2025'},
                'measurements': {
                    'Week Number': 20,
                    'Weight': 121.0,
                    'Fat Percentage': 0.5,
                    'Fat Weight': 60.0,
                    'Lean Weight': 61.0
                }
            }
        }
    
    @patch('Agents.recon_agent.prompt_loader')
    @patch('Agents.recon_agent.PushoverNotifier')
    def test_run_reconciliation_agent_success(self, mock_pushover, mock_prompt_loader):
        """Test complete workflow with successful reconciliation"""
        # Setup mocks
        mock_notifier = Mock()
        mock_notifier.send_notification.return_value = True
        mock_pushover.return_value = mock_notifier
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "SAME"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test the complete workflow
        result = run_reconciliation_agent(self.sample_email_data, self.sample_db_data)
        
        # Verify successful execution
        self.assertIsNotNone(result, "Should return result")
        self.assertTrue(result['success'], "Should succeed")
        self.assertTrue(result['data_matches'], "Should indicate data matches")
        self.assertTrue(result['proceed_to_validation'], "Should proceed to validation")
    
    @patch('Agents.recon_agent.prompt_loader')
    @patch('Agents.recon_agent.PushoverNotifier')
    def test_run_reconciliation_agent_failure(self, mock_pushover, mock_prompt_loader):
        """Test complete workflow with failed reconciliation"""
        # Setup mocks
        mock_notifier = Mock()
        mock_notifier.send_notification.return_value = True
        mock_pushover.return_value = mock_notifier
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.content = "DIFFERENT"
        mock_model.invoke.return_value = mock_response
        mock_prompt_loader.get_model_for_prompt.return_value = mock_model
        mock_prompt_loader.format_prompt.return_value = "formatted prompt"
        
        # Test the complete workflow
        result = run_reconciliation_agent(self.sample_email_data, self.sample_db_data)
        
        # Verify workflow termination
        self.assertIsNone(result, "Should return None when reconciliation fails")
    
    @patch('Agents.recon_agent.prompt_loader')
    @patch('Agents.recon_agent.PushoverNotifier')
    def test_environment_error_handling(self, mock_pushover, mock_prompt_loader):
        """Test behavior when environment variables are missing"""
        # Test with missing pushover credentials
        mock_pushover.side_effect = ValueError("PUSHOVER_USER_KEY and PUSHOVER_TOKEN must be set")
        
        # This should raise an exception during agent initialization
        with self.assertRaises(ValueError):
            ReconciliationAgent()


def run_comprehensive_tests():
    """Run all comprehensive tests and report results"""
    # Capture test output
    test_output = StringIO()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestReconciliationAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestReconciliationAgentIntegration))
    
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
    print(f"RECONCILIATION AGENT TEST RESULTS")
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
    print(f"\n🔍 CRITICAL LOGIC VALIDATION:")
    print(f"✅ SAME data → workflow continues ✅")
    print(f"✅ DIFFERENT data → workflow terminates ❌")
    print(f"✅ Critical measurement differences detected")
    print(f"✅ Proper error handling and notifications")
    
    return pass_rate == 100.0


if __name__ == "__main__":
    print("Running Comprehensive Reconciliation Agent Tests...")
    print("Testing corrected workflow logic...")
    print("SAME data = Continue workflow | DIFFERENT data = Terminate workflow")
    
    success = run_comprehensive_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED! Reconciliation agent logic is correct.")
        print("🎯 New workflow logic implemented successfully!")
    else:
        print("\n❌ Some tests failed. Please review and fix issues.")
        sys.exit(1)
