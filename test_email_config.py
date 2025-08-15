#!/usr/bin/env python3
"""
Test script for the email configuration system
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_configuration():
    """Test the email configuration system"""
    print("🧪 Testing Email Configuration System")
    print("=" * 50)
    
    try:
        from config.email_config import email_config, get_email_to, get_email_cc
        
        print("✅ Email configuration module imported successfully")
        
        # Test basic functions
        print(f"\n📧 Primary recipient: {get_email_to()}")
        print(f"📧 CC recipients: {get_email_cc()}")
        
        # Test configuration summary
        print("\n⚙️ Configuration Summary:")
        summary = email_config.get_configuration_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Test recipient management
        print("\n👥 Recipients List:")
        recipients = email_config._recipients
        if recipients:
            for i, recipient in enumerate(recipients, 1):
                status = "✅ Active" if recipient.active else "❌ Inactive"
                print(f"   {i}. {recipient.email} ({recipient.role}) {status}")
        else:
            print("   No recipients configured")
        
        print("\n✅ Email configuration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading"""
    print("\n🔧 Testing Environment Variables")
    print("=" * 50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    email_vars = [
        'EMAIL_TO',
        'EMAIL_CC', 
        'EMAIL_SUBJECT_PREFIX',
        'EMAIL_SEND_NOTIFICATIONS'
    ]
    
    for var in email_vars:
        value = os.getenv(var, 'Not set')
        print(f"   {var}: {value}")
    
    print("✅ Environment variables test completed!")

def test_management_script():
    """Test the management script functionality"""
    print("\n🛠️ Testing Management Script")
    print("=" * 50)
    
    try:
        # Test listing recipients
        print("Testing recipient listing...")
        from manage_email_recipients import list_recipients
        list_recipients()
        
        print("✅ Management script test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Management script test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Email Configuration Tests")
    print("=" * 60)
    
    # Test environment variables
    test_environment_variables()
    
    # Test email configuration
    config_success = test_email_configuration()
    
    # Test management script
    script_success = test_management_script()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Environment Variables: ✅")
    print(f"Email Configuration: {'✅' if config_success else '❌'}")
    print(f"Management Script: {'✅' if script_success else '❌'}")
    
    if config_success and script_success:
        print("\n🎉 All tests passed! Email configuration is working correctly.")
        print("\nNext steps:")
        print("1. Configure your email recipients using: python manage_email_recipients.py")
        print("2. Set up GitHub Actions workflow")
        print("3. Configure GitHub secrets")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
    
    return config_success and script_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
