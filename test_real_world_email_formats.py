#!/usr/bin/env python3
"""
Real-World Email Format Tests for Fetcher Agent
Tests various email formats that might be encountered in production.
"""

import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.fetcher_agent1_latestemail import LatestEmailFetcher

class TestRealWorldEmailFormats(unittest.TestCase):
    """Test fetcher agent with real-world email formats"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_fetcher = LatestEmailFetcher()

    def test_html_table_format(self):
        """Test HTML table format that might be in actual emails"""
        print("\n🧪 Testing HTML Table Format")
        
        html_table_email = """
<html>
<head>
<title>Fitness Data Entry</title>
</head>
<body>
<h2>Fitness Data Entry - 21/08/2025</h2>
<p>Submitted: 21/08/2025 09:40:34</p>

<table border="1" cellpadding="5" cellspacing="0">
<tr>
<th>Measurement</th>
<th>Value</th>
</tr>
<tr>
<td>Week Number</td>
<td>9</td>
</tr>
<tr>
<td>Weight</td>
<td>124.4</td>
</tr>
<tr>
<td>Fat Percentage</td>
<td>.514</td>
</tr>
<tr>
<td>Bmi</td>
<td>45.7</td>
</tr>
<tr>
<td>Fat Weight</td>
<td>64</td>
</tr>
<tr>
<td>Lean Weight</td>
<td>60.4</td>
</tr>
<tr>
<td>Neck</td>
<td>16</td>
</tr>
<tr>
<td>Shoulders</td>
<td>18</td>
</tr>
<tr>
<td>Biceps</td>
<td>18</td>
</tr>
<tr>
<td>Forearms</td>
<td>12.5</td>
</tr>
<tr>
<td>Chest</td>
<td>43</td>
</tr>
<tr>
<td>Above Navel</td>
<td>39</td>
</tr>
<tr>
<td>Navel</td>
<td>43</td>
</tr>
<tr>
<td>Waist</td>
<td>42</td>
</tr>
<tr>
<td>Hips</td>
<td>48</td>
</tr>
<tr>
<td>Thighs</td>
<td>29</td>
</tr>
<tr>
<td>Calves</td>
<td>17</td>
</tr>
</table>
</body>
</html>
        """
        
        result = self.email_fetcher.parse_fitness_data(html_table_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ HTML table format: {len(measurements)} measurements parsed correctly")

    def test_html_div_format(self):
        """Test HTML div format with CSS styling"""
        print("\n🧪 Testing HTML Div Format")
        
        html_div_email = """
<!DOCTYPE html>
<html>
<head>
<style>
.measurement { margin: 5px 0; }
.label { font-weight: bold; display: inline-block; width: 150px; }
.value { display: inline-block; }
</style>
</head>
<body>
<div class="header">
<h1>Fitness Data Entry</h1>
<p>Date: 21/08/2025</p>
<p>Submitted: 21/08/2025 09:40:34</p>
</div>

<div class="measurements">
<div class="measurement">
<span class="label">Week Number:</span>
<span class="value">9</span>
</div>
<div class="measurement">
<span class="label">Weight:</span>
<span class="value">124.4</span>
</div>
<div class="measurement">
<span class="label">Fat Percentage:</span>
<span class="value">.514</span>
</div>
<div class="measurement">
<span class="label">Bmi:</span>
<span class="value">45.7</span>
</div>
<div class="measurement">
<span class="label">Fat Weight:</span>
<span class="value">64</span>
</div>
<div class="measurement">
<span class="label">Lean Weight:</span>
<span class="value">60.4</span>
</div>
<div class="measurement">
<span class="label">Neck:</span>
<span class="value">16</span>
</div>
<div class="measurement">
<span class="label">Shoulders:</span>
<span class="value">18</span>
</div>
<div class="measurement">
<span class="label">Biceps:</span>
<span class="value">18</span>
</div>
<div class="measurement">
<span class="label">Forearms:</span>
<span class="value">12.5</span>
</div>
<div class="measurement">
<span class="label">Chest:</span>
<span class="value">43</span>
</div>
<div class="measurement">
<span class="label">Above Navel:</span>
<span class="value">39</span>
</div>
<div class="measurement">
<span class="label">Navel:</span>
<span class="value">43</span>
</div>
<div class="measurement">
<span class="label">Waist:</span>
<span class="value">42</span>
</div>
<div class="measurement">
<span class="label">Hips:</span>
<span class="value">48</span>
</div>
<div class="measurement">
<span class="label">Thighs:</span>
<span class="value">29</span>
</div>
<div class="measurement">
<span class="label">Calves:</span>
<span class="value">17</span>
</div>
</div>
</body>
</html>
        """
        
        result = self.email_fetcher.parse_fitness_data(html_div_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ HTML div format: {len(measurements)} measurements parsed correctly")

    def test_mixed_format_email(self):
        """Test email with mixed plain text and HTML"""
        print("\n🧪 Testing Mixed Format Email")
        
        mixed_email = """
Fitness Data Entry - 21/08/2025
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

Additional notes: This is a mixed format email with both text and HTML content.
        """
        
        result = self.email_fetcher.parse_fitness_data(mixed_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Mixed format: {len(measurements)} measurements parsed correctly")

    def test_unstructured_text_format(self):
        """Test unstructured text format"""
        print("\n🧪 Testing Unstructured Text Format")
        
        unstructured_email = """
Hi,

Here are my fitness measurements for this week:

Week Number is 9
My Weight is 124.4 kg
Fat Percentage is .514
Bmi reading is 45.7
Fat Weight is 64 kg
Lean Weight is 60.4 kg
Neck measurement is 16 inches
Shoulders are 18 inches
Biceps are 18 inches
Forearms are 12.5 inches
Chest is 43 inches
Above Navel is 39 inches
Navel is 43 inches
Waist is 42 inches
Hips are 48 inches
Thighs are 29 inches
Calves are 17 inches

Thanks!
        """
        
        result = self.email_fetcher.parse_fitness_data(unstructured_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Unstructured text: {len(measurements)} measurements parsed correctly")

    def test_csv_like_format(self):
        """Test CSV-like format with commas and tabs"""
        print("\n🧪 Testing CSV-like Format")
        
        csv_email = """
Fitness Data Entry, 21/08/2025
Submitted, 21/08/2025 09:40:34

Measurements:
Week Number,9
Weight,124.4
Fat Percentage,.514
Bmi,45.7
Fat Weight,64
Lean Weight,60.4
Neck,16
Shoulders,18
Biceps,18
Forearms,12.5
Chest,43
Above Navel,39
Navel,43
Waist,42
Hips,48
Thighs,29
Calves,17
        """
        
        result = self.email_fetcher.parse_fitness_data(csv_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ CSV-like format: {len(measurements)} measurements parsed correctly")

    def test_email_with_extra_content(self):
        """Test email with extra content and formatting"""
        print("\n🧪 Testing Email with Extra Content")
        
        extra_content_email = """
From: fitness@example.com
To: charlesparmar@gmail.com
Subject: Fitness Data Entry - 21/08/2025
Date: Thu, 21 Aug 2025 02:40:34 -0700 (PDT)

Dear Charles,

Please find below your fitness measurements for this week:

===========================================
FITNESS DATA ENTRY - 21/08/2025
===========================================
Submitted: 21/08/2025 09:40:34

MEASUREMENTS:
===========================================
Week Number: 9
Weight: 124.4 kg
Fat Percentage: .514
Bmi: 45.7
Fat Weight: 64 kg
Lean Weight: 60.4 kg
Neck: 16 inches
Shoulders: 18 inches
Biceps: 18 inches
Forearms: 12.5 inches
Chest: 43 inches
Above Navel: 39 inches
Navel: 43 inches
Waist: 42 inches
Hips: 48 inches
Thighs: 29 inches
Calves: 17 inches
===========================================

Notes:
- All measurements taken in the morning
- Weight measured in kg
- Body measurements in inches
- Fat percentage as decimal

Best regards,
Fitness Tracking System
        """
        
        result = self.email_fetcher.parse_fitness_data(extra_content_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Extra content format: {len(measurements)} measurements parsed correctly")

    def test_minimal_format(self):
        """Test minimal format with just measurements"""
        print("\n🧪 Testing Minimal Format")
        
        minimal_email = """
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
        
        result = self.email_fetcher.parse_fitness_data(minimal_email)
        measurements = result['measurements']
        
        # Verify critical measurements
        self.assertEqual(measurements['Above Navel'], 39)
        self.assertEqual(measurements['Navel'], 43)
        self.assertEqual(measurements['Fat Percentage'], 0.514)
        
        print(f"✅ Minimal format: {len(measurements)} measurements parsed correctly")

def run_real_world_tests():
    """Run all real-world email format tests"""
    print("🚀 Starting Real-World Email Format Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRealWorldEmailFormats)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"📊 Real-World Test Results:")
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("🎉 All real-world format tests passed! Fetcher agent is robust.")
        return True
    else:
        print("❌ Some real-world format tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_real_world_tests()
    sys.exit(0 if success else 1)
