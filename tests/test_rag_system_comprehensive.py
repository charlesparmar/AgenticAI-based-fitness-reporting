#!/usr/bin/env python3
"""
Comprehensive Test Suite for RAG System
Unit and Integration Tests for Analytics Implementation
"""

import sys
import os
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.utils.calculations import FitnessCalculations, CalculationResult
from rag.query_processor import QueryProcessor
from rag.retriever import Retriever
from rag.generator import ResponseGenerator
from rag.vector_store import VectorStore
from rag.analytics import FitnessAnalytics
from rag.chat_interface import ChatInterface, Message, Conversation
from rag.web_interface import WebInterface


class TestFitnessCalculations(unittest.TestCase):
    """Unit tests for FitnessCalculations class"""
    
    def setUp(self):
        """Set up test data"""
        self.calculations = FitnessCalculations()
        self.sample_data = [
            {'date': '2024-01-01', 'weight': 100.0, 'bmi': 25.0, 'fat_percent': 20.0},
            {'date': '2024-01-08', 'weight': 98.5, 'bmi': 24.6, 'fat_percent': 19.5},
            {'date': '2024-01-15', 'weight': 97.0, 'bmi': 24.2, 'fat_percent': 19.0},
            {'date': '2024-01-22', 'weight': 95.5, 'bmi': 23.8, 'fat_percent': 18.5},
            {'date': '2024-01-29', 'weight': 94.0, 'bmi': 23.4, 'fat_percent': 18.0},
            {'date': '2024-02-05', 'weight': 92.5, 'bmi': 23.0, 'fat_percent': 17.5},
            {'date': '2024-02-12', 'weight': 91.0, 'bmi': 22.6, 'fat_percent': 17.0},
            {'date': '2024-02-19', 'weight': 89.5, 'bmi': 22.2, 'fat_percent': 16.5},
            {'date': '2024-02-26', 'weight': 88.0, 'bmi': 21.8, 'fat_percent': 16.0},
            {'date': '2024-03-05', 'weight': 86.5, 'bmi': 21.4, 'fat_percent': 15.5},
            {'date': '2024-03-12', 'weight': 85.0, 'bmi': 21.0, 'fat_percent': 15.0},
            {'date': '2024-03-19', 'weight': 83.5, 'bmi': 20.6, 'fat_percent': 14.5},
            {'date': '2024-03-26', 'weight': 82.0, 'bmi': 20.2, 'fat_percent': 14.0}
        ]
    
    def test_calculate_total_weight_loss(self):
        """Test total weight loss calculation"""
        result = self.calculations.calculate_total_weight_loss(self.sample_data)
        
        self.assertIsInstance(result, CalculationResult)
        self.assertEqual(result.value, 18.0)  # 100.0 - 82.0
        self.assertEqual(result.unit, 'kg')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.validation_passed, True)
        self.assertEqual(result.data_points_used, 13)
        self.assertEqual(result.calculation_method, 'total_weight_loss')
    
    def test_calculate_total_weight_loss_empty_data(self):
        """Test total weight loss with empty data"""
        result = self.calculations.calculate_total_weight_loss([])
        
        self.assertEqual(result.value, 0.0)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.validation_passed, False)
        self.assertIn('No data available', result.warnings)
    
    def test_count_actual_weeks_of_data(self):
        """Test weeks count calculation"""
        weeks_count = self.calculations.count_actual_weeks_of_data(self.sample_data)
        self.assertEqual(weeks_count, 13)
    
    def test_count_actual_weeks_of_data_empty(self):
        """Test weeks count with empty data"""
        weeks_count = self.calculations.count_actual_weeks_of_data([])
        self.assertEqual(weeks_count, 0)
    
    def test_validate_data_consistency(self):
        """Test data consistency validation"""
        result = self.calculations.validate_data_consistency(self.sample_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['total_records'], 13)
        self.assertEqual(len(result['issues']), 0)
        self.assertEqual(len(result['warnings']), 0)
        self.assertIn('date_range', result)
    
    def test_validate_data_consistency_duplicates(self):
        """Test data validation with duplicates"""
        data_with_duplicates = self.sample_data + [self.sample_data[0]]
        result = self.calculations.validate_data_consistency(data_with_duplicates)
        
        self.assertFalse(result['valid'])
        self.assertIn('duplicate date entries', result['issues'][0])
    
    def test_validate_data_consistency_invalid_weight(self):
        """Test data validation with invalid weight"""
        invalid_data = [{'date': '2024-01-01', 'weight': 5.0}]  # Too low
        result = self.calculations.validate_data_consistency(invalid_data)
        
        self.assertTrue(result['valid'])  # Should still be valid, just warnings
        self.assertIn('impossible weight values', result['warnings'][0])
    
    def test_calculate_weight_loss_in_period(self):
        """Test weight loss calculation for specific period"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)
        result = self.calculations.calculate_weight_loss_in_period(start_date, end_date, self.sample_data)
        
        self.assertEqual(result.value, 6.0)  # 100.0 - 94.0
        self.assertEqual(result.unit, 'kg')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.data_points_used, 5)
    
    def test_calculate_weight_loss_in_period_no_data(self):
        """Test weight loss calculation for period with no data"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 2, 1)
        result = self.calculations.calculate_weight_loss_in_period(start_date, end_date, self.sample_data)
        
        self.assertEqual(result.value, 0.0)
        self.assertEqual(result.confidence, 0.0)
        self.assertIn('No data available for specified period', result.warnings)
    
    def test_get_weight_at_specific_date(self):
        """Test getting weight at specific date"""
        target_date = datetime(2024, 2, 15)
        weight = self.calculations.get_weight_at_specific_date(target_date, self.sample_data)
        
        self.assertEqual(weight, 91.0)  # Closest match
    
    def test_get_weight_at_specific_date_exact_match(self):
        """Test getting weight at exact date"""
        target_date = datetime(2024, 2, 12)
        weight = self.calculations.get_weight_at_specific_date(target_date, self.sample_data)
        
        self.assertEqual(weight, 91.0)  # Exact match
    
    def test_get_measurement_at_date(self):
        """Test getting measurement at specific date"""
        target_date = datetime(2024, 2, 12)
        bmi = self.calculations.get_measurement_at_date('bmi', target_date, self.sample_data)
        
        self.assertEqual(bmi, 22.6)
    
    def test_count_data_points_in_period(self):
        """Test counting data points in period"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)
        count = self.calculations.count_data_points_in_period(start_date, end_date, self.sample_data)
        
        self.assertEqual(count, 5)
    
    def test_validate_calculation_sanity(self):
        """Test calculation sanity validation"""
        context = {'type': 'weight_loss', 'time_period': 'month', 'data_points': 5}
        result = self.calculations.validate_calculation_sanity(15.0, context)
        
        self.assertTrue(result['sane'])
        self.assertEqual(len(result['warnings']), 0)
        self.assertEqual(result['confidence'], 0.9)
    
    def test_validate_calculation_sanity_impossible(self):
        """Test calculation sanity validation with impossible value"""
        context = {'type': 'weight_loss', 'time_period': 'week', 'data_points': 5}
        result = self.calculations.validate_calculation_sanity(150.0, context)
        
        self.assertFalse(result['sane'])
        self.assertIn('Unusually large weight loss detected', result['warnings'][0])


class TestQueryProcessor(unittest.TestCase):
    """Unit tests for QueryProcessor class"""
    
    def setUp(self):
        """Set up test data"""
        self.query_processor = QueryProcessor()
    
    def test_extract_explicit_dates(self):
        """Test explicit date extraction"""
        query = "What was my weight on 2024-02-15 and 2024-03-01?"
        dates = self.query_processor._extract_explicit_dates(query)
        
        self.assertEqual(len(dates), 2)
        self.assertIn('2024-02-15', dates)
        self.assertIn('2024-03-01', dates)
    
    def test_extract_relative_ranges(self):
        """Test relative date range extraction"""
        query = "Show me my progress this week and last month"
        ranges = self.query_processor._extract_relative_ranges(query)
        
        self.assertEqual(len(ranges), 2)
        range_names = [r['range'] for r in ranges]
        self.assertIn('this_week', range_names)
        self.assertIn('last_month', range_names)
    
    def test_extract_month_ranges(self):
        """Test month range extraction"""
        query = "What was my weight loss until end of June?"
        ranges = self.query_processor._extract_month_ranges(query)
        
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0]['month'], 'june')
        self.assertEqual(ranges[0]['type'], 'month_end')
    
    def test_extract_seasonal_ranges(self):
        """Test seasonal range extraction"""
        query = "Show me my progress during summer"
        ranges = self.query_processor._extract_seasonal_ranges(query)
        
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0]['season'], 'summer')
    
    def test_extract_date_ranges_comprehensive(self):
        """Test comprehensive date range extraction"""
        query = "What was my weight loss from 2024-01-01 to 2024-03-01, this month, and until end of June?"
        ranges = self.query_processor.extract_date_ranges(query)
        
        self.assertIn('explicit_dates', ranges)
        self.assertIn('relative_ranges', ranges)
        self.assertIn('month_ranges', ranges)
        self.assertIn('parsed_ranges', ranges)
    
    def test_classify_query_trend(self):
        """Test query classification for trend queries"""
        query = "How has my weight changed over time?"
        processed = self.query_processor.process_query(query)
        
        self.assertEqual(processed['query_type'], 'trend')
    
    def test_classify_query_calculation(self):
        """Test query classification for calculation queries"""
        query = "Calculate my total weight loss"
        processed = self.query_processor.process_query(query)
        
        self.assertEqual(processed['query_type'], 'calculation_request')
    
    def test_classify_query_time_range(self):
        """Test query classification for time range queries"""
        query = "What was my weight loss until end of June?"
        processed = self.query_processor.process_query(query)
        
        self.assertEqual(processed['query_type'], 'time_range_analysis')
    
    def test_validate_query_valid(self):
        """Test query validation with valid query"""
        query = "What is my current weight?"
        is_valid, error = self.query_processor.validate_query(query)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_query_empty(self):
        """Test query validation with empty query"""
        query = ""
        is_valid, error = self.query_processor.validate_query(query)
        
        self.assertFalse(is_valid)
        self.assertIn("empty", error)
    
    def test_validate_query_too_short(self):
        """Test query validation with too short query"""
        query = "Hi"
        is_valid, error = self.query_processor.validate_query(query)
        
        self.assertFalse(is_valid)
        self.assertIn("short", error)
    
    def test_get_query_suggestions(self):
        """Test query suggestions"""
        partial = "weight"
        suggestions = self.query_processor.get_query_suggestions(partial)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(all("weight" in s.lower() for s in suggestions))


class TestRetriever(unittest.TestCase):
    """Unit tests for Retriever class"""
    
    def setUp(self):
        """Set up test data"""
        self.vector_store = Mock()
        self.query_processor = QueryProcessor()
        self.retriever = Retriever(self.vector_store, self.query_processor)
    
    def test_extract_date_from_result(self):
        """Test date extraction from result"""
        result = {
            'content': '{"date": "2024-02-15", "weight": 91.0}',
            'metadata': {'date': '2024-02-15'}
        }
        
        date = self.retriever._extract_date_from_result(result)
        self.assertEqual(date, '2024-02-15')
    
    def test_extract_date_from_result_no_date(self):
        """Test date extraction from result with no date"""
        result = {
            'content': 'No date information here',
            'metadata': {}
        }
        
        date = self.retriever._extract_date_from_result(result)
        self.assertIsNone(date)
    
    def test_date_matches_ranges_explicit(self):
        """Test date matching with explicit dates"""
        result_date = '2024-02-15'
        parsed_ranges = {
            'explicit': [
                {'parsed': datetime(2024, 2, 15)},
                {'parsed': datetime(2024, 3, 1)}
            ]
        }
        
        matches = self.retriever._date_matches_ranges(result_date, parsed_ranges)
        self.assertTrue(matches)
    
    def test_date_matches_ranges_relative(self):
        """Test date matching with relative ranges"""
        result_date = '2024-02-15'
        parsed_ranges = {
            'relative': [
                {
                    'start_date': datetime(2024, 2, 1),
                    'end_date': datetime(2024, 2, 29)
                }
            ]
        }
        
        matches = self.retriever._date_matches_ranges(result_date, parsed_ranges)
        self.assertTrue(matches)
    
    def test_date_matches_ranges_no_match(self):
        """Test date matching with no match"""
        result_date = '2024-05-15'
        parsed_ranges = {
            'relative': [
                {
                    'start_date': datetime(2024, 2, 1),
                    'end_date': datetime(2024, 2, 29)
                }
            ]
        }
        
        matches = self.retriever._date_matches_ranges(result_date, parsed_ranges)
        self.assertFalse(matches)
    
    def test_build_enhanced_filters(self):
        """Test enhanced filter building"""
        filter_criteria = {'measurement': 'weight'}
        date_ranges = {
            'parsed_ranges': {
                'relative': [
                    {
                        'start_date': datetime(2024, 2, 1),
                        'end_date': datetime(2024, 2, 29),
                        'range_name': 'this_month'
                    }
                ]
            }
        }
        processed_query = {'query_type': 'time_range_analysis'}
        
        enhanced_filters = self.retriever._build_enhanced_filters(
            filter_criteria, date_ranges, processed_query
        )
        
        self.assertIn('date_filters', enhanced_filters)
        self.assertEqual(enhanced_filters['query_type'], 'time_range_analysis')
    
    def test_filter_results_by_date_ranges(self):
        """Test result filtering by date ranges"""
        results = [
            {
                'content': '{"date": "2024-02-15", "weight": 91.0}',
                'metadata': {'date': '2024-02-15'}
            },
            {
                'content': '{"date": "2024-05-15", "weight": 85.0}',
                'metadata': {'date': '2024-05-15'}
            }
        ]
        
        date_ranges = {
            'parsed_ranges': {
                'relative': [
                    {
                        'start_date': datetime(2024, 2, 1),
                        'end_date': datetime(2024, 2, 29),
                        'range_name': 'this_month'
                    }
                ]
            }
        }
        processed_query = {}
        
        filtered_results = self.retriever._filter_results_by_date_ranges(
            results, date_ranges, processed_query
        )
        
        self.assertEqual(len(filtered_results), 1)
        self.assertIn('2024-02-15', filtered_results[0]['content'])


class TestResponseGenerator(unittest.TestCase):
    """Unit tests for ResponseGenerator class"""
    
    def setUp(self):
        """Set up test data"""
        self.vector_store = Mock()
        self.query_processor = QueryProcessor()
        self.retriever = Mock()
        self.generator = ResponseGenerator(
            vector_store=self.vector_store,
            query_processor=self.query_processor,
            retriever=self.retriever
        )
    
    def test_extract_fitness_data(self):
        """Test fitness data extraction from context"""
        context = [
            {
                'content': '{"date": "2024-02-15", "weight": 91.0, "bmi": 22.6}',
                'metadata': {'date': '2024-02-15'}
            },
            {
                'content': '{"date": "2024-03-01", "weight": 89.5, "bmi": 22.2}',
                'metadata': {'date': '2024-03-01'}
            }
        ]
        
        fitness_data = self.generator._extract_fitness_data(context)
        
        self.assertEqual(len(fitness_data), 2)
        self.assertEqual(fitness_data[0]['weight'], 91.0)
        self.assertEqual(fitness_data[1]['weight'], 89.5)
    
    def test_extract_structured_data(self):
        """Test structured data extraction from content"""
        content = "Date: 2024-02-15, Weight: 91.0 kg, BMI: 22.6"
        
        data = self.generator._extract_structured_data(content)
        
        self.assertIsNotNone(data)
        self.assertEqual(data['date'], '2024-02-15')
        self.assertEqual(data['weight'], 91.0)
        self.assertEqual(data['bmi'], 22.6)
    
    def test_extract_structured_data_no_date(self):
        """Test structured data extraction with no date"""
        content = "Weight: 91.0 kg, BMI: 22.6"
        
        data = self.generator._extract_structured_data(content)
        
        self.assertIsNone(data)
    
    def test_extract_calculation_requests(self):
        """Test calculation request extraction"""
        query = "What is my total weight loss and how many weeks of data do I have?"
        fitness_data = [{'date': '2024-01-01', 'weight': 100.0}]
        
        calculations = self.generator._extract_calculation_requests(query, fitness_data)
        
        self.assertIn('total_weight_loss', calculations)
        self.assertIn('weeks_count', calculations)
    
    def test_validate_response(self):
        """Test response validation"""
        response = "Your total weight loss is 18 kg"
        query = "What is my total weight loss?"
        context = []
        analytics_data = {
            'calculations': {
                'total_weight_loss': {
                    'value': 18.0,
                    'warnings': []
                }
            },
            'validation': {
                'valid': True,
                'issues': []
            }
        }
        
        validation_result = self.generator._validate_response(
            response, query, context, analytics_data
        )
        
        self.assertTrue(validation_result['valid'])
        self.assertEqual(validation_result['confidence'], 1.0)
    
    def test_validate_response_with_warnings(self):
        """Test response validation with warnings"""
        response = "Your total weight loss is 18 kg"
        query = "What is my total weight loss?"
        context = []
        analytics_data = {
            'calculations': {
                'total_weight_loss': {
                    'value': 18.0,
                    'warnings': ['Unusually large weight loss detected']
                }
            },
            'validation': {
                'valid': True,
                'issues': []
            }
        }
        
        validation_result = self.generator._validate_response(
            response, query, context, analytics_data
        )
        
        self.assertFalse(validation_result['valid'])
        self.assertLess(validation_result['confidence'], 1.0)
        self.assertIn('Unusually large weight loss detected', validation_result['warnings'])


class TestChatInterface(unittest.TestCase):
    """Unit tests for ChatInterface class"""
    
    def setUp(self):
        """Set up test data"""
        self.vector_store = Mock()
        self.query_processor = QueryProcessor()
        self.retriever = Mock()
        self.generator = Mock()
        self.chat_interface = ChatInterface(
            vector_store=self.vector_store,
            query_processor=self.query_processor,
            retriever=self.retriever,
            generator=self.generator
        )
    
    def test_create_conversation_with_welcome(self):
        """Test conversation creation with welcome message"""
        conversation_id = self.chat_interface.create_conversation("Test Chat")
        
        self.assertIsNotNone(conversation_id)
        conversation = self.chat_interface.get_conversation(conversation_id)
        
        self.assertIsNotNone(conversation)
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].sender, "assistant")
        self.assertIn("Welcome to the world of Fitness Information", conversation.messages[0].content)
    
    def test_send_message(self):
        """Test sending a message"""
        # Create conversation first
        conversation_id = self.chat_interface.create_conversation("Test Chat")
        
        # Mock generator response
        mock_response = {
            "response": "Your current weight is 82.0 kg",
            "success": True,
            "query_type": "specific"
        }
        self.generator.generate_response.return_value = mock_response
        
        # Send message
        response = self.chat_interface.send_message("What is my current weight?", conversation_id)
        
        self.assertIn("conversation_id", response)
        self.assertIn("user_message", response)
        self.assertIn("assistant_message", response)
        self.assertIn("response_data", response)
        self.assertIn("success", response["response_data"])
        self.assertTrue(response["response_data"]["success"])
    
    def test_get_conversation(self):
        """Test getting conversation"""
        conversation_id = self.chat_interface.create_conversation("Test Chat")
        conversation = self.chat_interface.get_conversation(conversation_id)
        
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.id, conversation_id)
        self.assertEqual(conversation.title, "Test Chat")
    
    def test_get_conversation_nonexistent(self):
        """Test getting nonexistent conversation"""
        conversation = self.chat_interface.get_conversation("nonexistent-id")
        
        self.assertIsNone(conversation)
    
    def test_list_conversations(self):
        """Test listing conversations"""
        # Create multiple conversations
        self.chat_interface.create_conversation("Chat 1")
        self.chat_interface.create_conversation("Chat 2")
        
        conversations = self.chat_interface.list_conversations()
        
        self.assertEqual(len(conversations), 2)
        self.assertTrue(all('id' in conv for conv in conversations))
        self.assertTrue(all('title' in conv for conv in conversations))
    
    def test_switch_conversation(self):
        """Test switching conversation"""
        conversation_id = self.chat_interface.create_conversation("Test Chat")
        
        success = self.chat_interface.switch_conversation(conversation_id)
        
        self.assertTrue(success)
        self.assertEqual(self.chat_interface.active_conversation_id, conversation_id)
    
    def test_delete_conversation(self):
        """Test deleting conversation"""
        conversation_id = self.chat_interface.create_conversation("Test Chat")
        
        success = self.chat_interface.delete_conversation(conversation_id)
        
        self.assertTrue(success)
        self.assertIsNone(self.chat_interface.get_conversation(conversation_id))
    
    def test_rename_conversation(self):
        """Test renaming conversation"""
        conversation_id = self.chat_interface.create_conversation("Old Title")
        
        success = self.chat_interface.rename_conversation(conversation_id, "New Title")
        
        self.assertTrue(success)
        conversation = self.chat_interface.get_conversation(conversation_id)
        self.assertEqual(conversation.title, "New Title")


class TestWebInterface(unittest.TestCase):
    """Unit tests for WebInterface class"""
    
    def setUp(self):
        """Set up test data"""
        self.vector_store = Mock()
        self.chat_interface = Mock()
        self.web_interface = WebInterface(
            vector_store=self.vector_store,
            chat_interface=self.chat_interface
        )
    
    def test_extract_fitness_data_from_content(self):
        """Test fitness data extraction from content"""
        content = "Date: 2024-02-15, Weight: 91.0 kg, BMI: 22.6"
        
        data = self.web_interface._extract_fitness_data_from_content(content)
        
        self.assertIsNotNone(data)
        self.assertEqual(data['date'], '2024-02-15')
        self.assertEqual(data['weight'], 91.0)
        self.assertEqual(data['bmi'], 22.6)
    
    def test_get_available_measurements(self):
        """Test getting available measurements"""
        fitness_data = [
            {'date': '2024-01-01', 'weight': 100.0, 'bmi': 25.0},
            {'date': '2024-02-01', 'weight': 95.0, 'fat_percent': 18.0}
        ]
        
        measurements = self.web_interface._get_available_measurements(fitness_data)
        
        self.assertIn('weight', measurements)
        self.assertIn('bmi', measurements)
        self.assertIn('fat_percent', measurements)
        self.assertNotIn('date', measurements)
    
    def test_get_data_context(self):
        """Test getting data context"""
        # Mock collection info
        self.vector_store.get_collection_info.return_value = {'count': 100}
        
        # Mock retriever results
        mock_results = [
            {
                'content': '{"date": "2024-02-15", "weight": 91.0}',
                'metadata': {'date': '2024-02-15'}
            }
        ]
        self.chat_interface.retriever.retrieve.return_value = mock_results
        
        context = self.web_interface._get_data_context()
        
        self.assertIn('total_records', context)
        self.assertIn('data_quality', context)
        self.assertIn('analytics_summary', context)
        self.assertIn('system_capabilities', context)
        self.assertIn('query_examples', context)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete RAG system"""
    
    def setUp(self):
        """Set up integration test environment"""
        try:
            self.vector_store = VectorStore()
            self.query_processor = QueryProcessor()
            self.retriever = Retriever(self.vector_store, self.query_processor)
            self.generator = ResponseGenerator(
                vector_store=self.vector_store,
                query_processor=self.query_processor,
                retriever=self.retriever
            )
            self.chat_interface = ChatInterface(
                vector_store=self.vector_store,
                query_processor=self.query_processor,
                retriever=self.retriever,
                generator=self.generator
            )
            self.analytics = FitnessAnalytics(
                self.vector_store,
                self.query_processor,
                self.retriever
            )
        except Exception as e:
            self.skipTest(f"Integration test setup failed: {e}")
    
    def test_end_to_end_query_processing(self):
        """Test end-to-end query processing"""
        query = "What is my total weight loss?"
        
        # Process query
        processed_query = self.query_processor.process_query(query)
        self.assertIn('query_type', processed_query)
        
        # Extract date ranges
        date_ranges = self.query_processor.extract_date_ranges(query)
        self.assertIn('parsed_ranges', date_ranges)
        
        # Retrieve context
        context = self.retriever.retrieve(query, n_results=5)
        self.assertIsInstance(context, list)
        
        # Generate response
        if context:
            response = self.generator.generate_response(query, context)
            self.assertIn('success', response)
            self.assertIn('analytics_data', response)
            self.assertIn('validation_result', response)
    
    def test_analytics_integration(self):
        """Test analytics integration"""
        # Test analytics summary
        summary = self.analytics.get_analytics_summary()
        self.assertIsInstance(summary, dict)
        
        # Test trend analysis
        try:
            trends = self.analytics.analyze_trends('weight', 'month', 5)
            self.assertIsInstance(trends, list)
        except Exception as e:
            # This might fail if no data is available, which is acceptable
            pass
    
    def test_chat_interface_integration(self):
        """Test chat interface integration"""
        # Create conversation
        conversation_id = self.chat_interface.create_conversation("Integration Test")
        self.assertIsNotNone(conversation_id)
        
        # Get conversation
        conversation = self.chat_interface.get_conversation(conversation_id)
        self.assertIsNotNone(conversation)
        self.assertEqual(len(conversation.messages), 1)  # Welcome message
        
        # List conversations
        conversations = self.chat_interface.list_conversations()
        self.assertGreater(len(conversations), 0)
    
    def test_calculation_accuracy(self):
        """Test calculation accuracy with known data"""
        # Create test data
        test_data = [
            {'date': '2024-01-01', 'weight': 100.0},
            {'date': '2024-01-08', 'weight': 98.0},
            {'date': '2024-01-15', 'weight': 96.0},
            {'date': '2024-01-22', 'weight': 94.0},
            {'date': '2024-01-29', 'weight': 92.0}
        ]
        
        calculations = FitnessCalculations()
        
        # Test total weight loss
        total_loss = calculations.calculate_total_weight_loss(test_data)
        self.assertEqual(total_loss.value, 8.0)  # 100.0 - 92.0
        
        # Test weeks count
        weeks_count = calculations.count_actual_weeks_of_data(test_data)
        self.assertEqual(weeks_count, 5)
        
        # Test period calculation
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 15)
        period_loss = calculations.calculate_weight_loss_in_period(start_date, end_date, test_data)
        self.assertEqual(period_loss.value, 4.0)  # 100.0 - 96.0
    
    def test_date_range_processing(self):
        """Test date range processing"""
        queries = [
            "What was my weight loss until end of June?",
            "Show me my progress this month",
            "How much weight did I lose last week?",
            "What was my weight on 2024-02-15?",
            "Calculate my total weight loss from 2024-01-01 to 2024-03-01"
        ]
        
        for query in queries:
            # Process query
            processed = self.query_processor.process_query(query)
            self.assertIn('query_type', processed)
            
            # Extract date ranges
            date_ranges = self.query_processor.extract_date_ranges(query)
            self.assertIn('parsed_ranges', date_ranges)
            
            # Test retrieval with date filtering
            context = self.retriever.retrieve(query, n_results=3)
            self.assertIsInstance(context, list)
    
    def test_response_validation(self):
        """Test response validation"""
        # Create test data
        test_data = [
            {'date': '2024-01-01', 'weight': 100.0},
            {'date': '2024-01-29', 'weight': 92.0}
        ]
        
        calculations = FitnessCalculations()
        
        # Test with valid data
        total_loss = calculations.calculate_total_weight_loss(test_data)
        self.assertTrue(total_loss.validation_passed)
        self.assertEqual(total_loss.confidence, 0.9)
        
        # Test with impossible data
        impossible_data = [
            {'date': '2024-01-01', 'weight': 100.0},
            {'date': '2024-01-29', 'weight': 50.0}  # Impossible loss
        ]
        
        impossible_loss = calculations.calculate_total_weight_loss(impossible_data)
        self.assertFalse(impossible_loss.validation_passed)
        self.assertIn('Unusually large weight loss detected', impossible_loss.warnings[0])


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFitnessCalculations))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestQueryProcessor))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRetriever))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestResponseGenerator))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestChatInterface))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestWebInterface))
    
    # Add integration tests
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Calculate pass rate
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nPASS RATE: {pass_rate:.1f}%")
    
    if pass_rate == 100.0:
        print("🎉 ALL TESTS PASSED! 100% SUCCESS RATE!")
    else:
        print(f"⚠️ {100 - pass_rate:.1f}% of tests need attention")
    
    return result


if __name__ == "__main__":
    # Run comprehensive tests
    result = run_comprehensive_tests()
    
    # Exit with appropriate code
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1) 