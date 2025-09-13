#!/usr/bin/env python3
"""
Comprehensive test suite for Final Email Agent
Tests all functionality with mocking to avoid external dependencies
"""

import unittest
import os
import tempfile
import json
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module under test
from Agents.final_email_agent import FinalEmailAgent, PushoverNotifier, run_final_email_agent

class TestPushoverNotifier(unittest.TestCase):
    """Test cases for PushoverNotifier class"""
    
    @patch.dict(os.environ, {'PUSHOVER_USER_KEY': 'test_user', 'PUSHOVER_TOKEN': 'test_token'})
    def test_pushover_init_success(self):
        """Test successful PushoverNotifier initialization"""
        notifier = PushoverNotifier()
        self.assertEqual(notifier.user_key, 'test_user')
        self.assertEqual(notifier.app_token, 'test_token')
        self.assertEqual(notifier.api_url, "https://api.pushover.net/1/messages.json")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_pushover_init_missing_credentials(self):
        """Test PushoverNotifier initialization with missing credentials"""
        with self.assertRaises(ValueError) as context:
            PushoverNotifier()
        self.assertIn("PUSHOVER_USER_KEY and PUSHOVER_TOKEN must be set", str(context.exception))
    
    @patch.dict(os.environ, {'PUSHOVER_USER_KEY': 'test_user', 'PUSHOVER_TOKEN': 'test_token'})
    @patch('requests.post')
    def test_send_notification_success(self, mock_post):
        """Test successful notification sending"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": 1}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = PushoverNotifier()
        result = notifier.send_notification("Test message", title="Test Title")
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch.dict(os.environ, {'PUSHOVER_USER_KEY': 'test_user', 'PUSHOVER_TOKEN': 'test_token'})
    @patch('requests.post')
    def test_send_notification_failure(self, mock_post):
        """Test notification sending failure"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": 0, "errors": ["Invalid token"]}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = PushoverNotifier()
        result = notifier.send_notification("Test message")
        
        self.assertFalse(result)


class TestFinalEmailAgent(unittest.TestCase):
    """Test cases for FinalEmailAgent class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_env = {
            'GMAIL_ADDRESS': 'test@example.com',
            'EMAIL_TO': 'coach@example.com',
            'SQLITE_API_KEY': 'test_sqlite_key',
            'PUSHOVER_USER_KEY': 'test_user',
            'PUSHOVER_TOKEN': 'test_token'
        }
    
    @patch.dict(os.environ, clear=True)
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    def test_init_missing_gmail_address(self, mock_get_cc, mock_get_to, mock_email_config):
        """Test initialization fails when GMAIL_ADDRESS is missing"""
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        
        with self.assertRaises(ValueError) as context:
            FinalEmailAgent()
        self.assertIn("GMAIL_ADDRESS not found in environment variables", str(context.exception))
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    def test_init_success(self, mock_build, mock_creds, mock_exists, mock_pushover, 
                         mock_get_cc, mock_get_to, mock_email_config):
        """Test successful initialization"""
        # Mock email configuration
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = ['cc@example.com']
        mock_email_config.get_subject_prefix.return_value = 'Test Prefix'
        
        # Mock file existence and credentials
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        
        # Mock Gmail service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock Pushover
        mock_pushover.return_value = Mock()
        
        agent = FinalEmailAgent()
        
        self.assertEqual(agent.email_address, 'test@example.com')
        self.assertEqual(agent.coach_email, 'coach@example.com')
        self.assertEqual(agent.cc_recipients, ['cc@example.com'])
        self.assertIsNotNone(agent.service)
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com', 'SQLITE_API_KEY': 'test_key'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    @patch('sqlitecloud.connect')
    @patch('pandas.read_sql_query')
    def test_fetch_supabase_data_success(self, mock_read_sql, mock_connect, mock_build, 
                                       mock_creds, mock_exists, mock_pushover,
                                       mock_get_cc, mock_get_to, mock_email_config):
        """Test successful data fetching from Supabase"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        # Setup database mocking
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'weight': [70.0, 71.0],
            'fat_percent': [15.0, 14.8]
        })
        mock_read_sql.return_value = test_data
        
        agent = FinalEmailAgent()
        result = agent.fetch_supabase_data()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        mock_conn.close.assert_called_once()
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'}, clear=True)
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    def test_fetch_supabase_data_no_api_key(self, mock_build, mock_creds, mock_exists, 
                                          mock_pushover, mock_get_cc, mock_get_to, mock_email_config):
        """Test data fetching fails when SQLite API key is missing"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        agent = FinalEmailAgent()
        result = agent.fetch_supabase_data()
        
        self.assertIsNone(result)
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    def test_create_excel_file_success(self, mock_build, mock_creds, mock_exists, 
                                     mock_pushover, mock_get_cc, mock_get_to, mock_email_config):
        """Test successful Excel file creation"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        agent = FinalEmailAgent()
        
        # Use a real temporary file for this test to avoid mocking complications
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create test data
            test_data = pd.DataFrame({
                'date': ['2024-01-01'],
                'weight': [70.0]
            })
            
            # Create Excel file using pandas directly
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                test_data.to_excel(writer, sheet_name='Fitness Data', index=False)
            
            # Test that file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Test agent's Excel creation method with a simple mock
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp_instance = Mock()
                mock_temp_instance.name = temp_path
                mock_temp.return_value = mock_temp_instance
                
                result = agent.create_excel_file(test_data)
                self.assertEqual(result, temp_path)
                
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    def test_create_excel_file_empty_data(self, mock_build, mock_creds, mock_exists, 
                                        mock_pushover, mock_get_cc, mock_get_to, mock_email_config):
        """Test Excel file creation with empty data"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        agent = FinalEmailAgent()
        result = agent.create_excel_file(None)
        
        self.assertIsNone(result)
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        result = agent.create_excel_file(empty_df)
        self.assertIsNone(result)
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    def test_create_final_email_body(self, mock_build, mock_creds, mock_exists, 
                                   mock_pushover, mock_get_cc, mock_get_to, mock_email_config):
        """Test email body creation with feedback request"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        agent = FinalEmailAgent()
        
        # Test with "Warm Regards" in body
        original_body = "Hello coach,\n\nThis is my report.\n\nWarm Regards,\nCharles"
        result = agent.create_final_email_body(original_body)
        
        self.assertIn("Please kindly let me know your feedback", result)
        self.assertIn("Warm Regards,", result)
        
        # Test without "Warm Regards"
        original_body = "Hello coach,\n\nThis is my report.\n\nBest,\nCharles"
        result = agent.create_final_email_body(original_body)
        
        self.assertIn("Please kindly let me know your feedback", result)
    
    @patch.dict(os.environ, {'GMAIL_ADDRESS': 'test@example.com'})
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('Agents.final_email_agent.PushoverNotifier')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test file content')
    def test_create_message_with_attachment(self, mock_file, mock_build, mock_creds, mock_exists, 
                                          mock_pushover, mock_get_cc, mock_get_to, mock_email_config):
        """Test email message creation with attachment"""
        # Setup agent
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = []
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        mock_build.return_value = Mock()
        mock_pushover.return_value = Mock()
        
        # Mock os.path.exists for attachment
        with patch('os.path.exists', return_value=True):
            agent = FinalEmailAgent()
            
            result = agent.create_message_with_attachment(
                to_email="coach@example.com",
                subject="Test Subject",
                body="Test Body",
                attachment_path="/tmp/test.xlsx",
                cc_emails=["cc@example.com"]
            )
            
            self.assertIn('raw', result)
            self.assertIsInstance(result['raw'], str)


class TestRunFinalEmailAgent(unittest.TestCase):
    """Test cases for the run_final_email_agent function"""
    
    @patch('Agents.final_email_agent.FinalEmailAgent')
    def test_run_final_email_agent_success(self, mock_agent_class):
        """Test successful run of final email agent"""
        mock_agent = Mock()
        mock_agent.send_final_email.return_value = {
            'success': True,
            'message_id': 'test_id',
            'timestamp': datetime.now().isoformat()
        }
        mock_agent_class.return_value = mock_agent
        
        email_body_data = {'email_body': 'Test email body'}
        result = run_final_email_agent(email_body_data, 1)
        
        self.assertTrue(result['success'])
        mock_agent.send_final_email.assert_called_once_with(email_body_data, 1)
    
    @patch('Agents.final_email_agent.FinalEmailAgent')
    def test_run_final_email_agent_no_body(self, mock_agent_class):
        """Test run with missing email body"""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        email_body_data = {}
        result = run_final_email_agent(email_body_data, 1)
        
        self.assertFalse(result['success'])
        self.assertIn('No email body found', result['error'])
    
    @patch('Agents.final_email_agent.FinalEmailAgent')
    def test_run_final_email_agent_exception(self, mock_agent_class):
        """Test run with exception during initialization"""
        mock_agent_class.side_effect = Exception("Test exception")
        
        email_body_data = {'email_body': 'Test body'}
        result = run_final_email_agent(email_body_data, 1)
        
        self.assertFalse(result['success'])
        self.assertIn('Test exception', result['error'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow"""
    
    @patch.dict(os.environ, {
        'GMAIL_ADDRESS': 'test@example.com',
        'SQLITE_API_KEY': 'test_key',
        'PUSHOVER_USER_KEY': 'test_user',
        'PUSHOVER_TOKEN': 'test_token'
    })
    @patch('Agents.final_email_agent.email_config')
    @patch('Agents.final_email_agent.get_email_to')
    @patch('Agents.final_email_agent.get_email_cc')
    @patch('os.path.exists')
    @patch('Agents.final_email_agent.Credentials')
    @patch('Agents.final_email_agent.build')
    @patch('sqlitecloud.connect')
    @patch('pandas.read_sql_query')
    @patch('tempfile.NamedTemporaryFile')
    @patch('pandas.ExcelWriter')
    @patch('requests.post')
    def test_full_email_workflow(self, mock_post, mock_excel_writer, mock_temp_file,
                                mock_read_sql, mock_connect, mock_build, mock_creds,
                                mock_exists, mock_get_cc, mock_get_to, mock_email_config):
        """Test the complete email sending workflow"""
        # Setup all mocks
        mock_get_to.return_value = 'coach@example.com'
        mock_get_cc.return_value = ['cc@example.com']
        mock_email_config.get_subject_prefix.return_value = 'Test Prefix'
        
        mock_exists.return_value = True
        mock_cred_instance = Mock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance
        
        # Mock Gmail service
        mock_service = Mock()
        mock_send = Mock()
        mock_send.execute.return_value = {'id': 'test_message_id'}
        mock_service.users().messages().send.return_value = mock_send
        mock_build.return_value = mock_service
        
        # Mock database
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        test_data = pd.DataFrame({'date': ['2024-01-01'], 'weight': [70.0]})
        mock_read_sql.return_value = test_data
        
        # Mock Excel creation
        mock_temp = Mock()
        mock_temp.name = '/tmp/test.xlsx'
        mock_temp_file.return_value = mock_temp
        mock_writer = Mock()
        mock_excel_writer.return_value.__enter__.return_value = mock_writer
        
        # Mock Pushover response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 1}
        mock_post.return_value = mock_response
        
        # Mock file operations
        with patch('os.path.exists', return_value=True), \
             patch('os.unlink'), \
             patch('builtins.open', mock_open(read_data=b'test')):
            
            email_body_data = {
                'email_body': 'This is a test fitness report.\n\nWarm Regards,\nCharles'
            }
            
            result = run_final_email_agent(email_body_data, 1)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['message_id'], 'test_message_id')
            self.assertEqual(result['to_email'], 'coach@example.com')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
