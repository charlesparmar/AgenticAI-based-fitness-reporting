#!/usr/bin/env python3
"""
Email Recipients Management Utility
Allows easy management of email recipients for the fitness reporting system.
"""

import sys
import os
import argparse
from typing import List, Optional

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.email_config import email_config
except ImportError:
    print("❌ Error: Email configuration module not found. Please ensure config/email_config.py exists.")
    sys.exit(1)

def list_recipients():
    """List all current email recipients"""
    print("\n📧 Current Email Recipients:")
    print("=" * 50)
    
    recipients = email_config._recipients
    if not recipients:
        print("No recipients configured.")
        return
    
    for i, recipient in enumerate(recipients, 1):
        status = "✅ Active" if recipient.active else "❌ Inactive"
        role_display = f"({recipient.role})" if recipient.role else ""
        name_display = f" - {recipient.name}" if recipient.name else ""
        print(f"{i}. {recipient.email}{name_display} {role_display} {status}")

def add_recipient(email: str, name: Optional[str] = None, role: str = "cc", active: bool = True):
    """Add a new email recipient"""
    try:
        email_config.add_recipient(email=email, name=name, role=role, active=active)
        print(f"✅ Added recipient: {email}")
        if name:
            print(f"   Name: {name}")
        print(f"   Role: {role}")
        print(f"   Status: {'Active' if active else 'Inactive'}")
    except Exception as e:
        print(f"❌ Error adding recipient: {e}")

def remove_recipient(email: str):
    """Remove an email recipient"""
    try:
        email_config.remove_recipient(email)
        print(f"✅ Removed recipient: {email}")
    except Exception as e:
        print(f"❌ Error removing recipient: {e}")

def update_recipient(email: str, **kwargs):
    """Update recipient properties"""
    try:
        email_config.update_recipient(email, **kwargs)
        print(f"✅ Updated recipient: {email}")
        for key, value in kwargs.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Error updating recipient: {e}")

def show_configuration():
    """Show current email configuration summary"""
    print("\n⚙️ Email Configuration Summary:")
    print("=" * 50)
    
    summary = email_config.get_configuration_summary()
    
    print(f"Primary Recipient: {summary['primary_recipient']}")
    print(f"Total Recipients: {summary['total_recipients']}")
    print(f"CC Recipients: {', '.join(summary['cc_recipients']) if summary['cc_recipients'] else 'None'}")
    print(f"Subject Prefix: {summary['subject_prefix']}")
    print(f"Reply To: {summary['reply_to'] or 'Not set'}")
    print(f"Send Notifications: {'Yes' if summary['send_notifications'] else 'No'}")

def set_primary_recipient(email: str):
    """Set the primary recipient"""
    try:
        # Find the recipient and update their role to 'coach'
        email_config.update_recipient(email, role='coach')
        
        # Update the configuration
        if email_config._config:
            email_config._config.primary_recipient = email
            email_config._save_configuration()
        
        print(f"✅ Set primary recipient to: {email}")
    except Exception as e:
        print(f"❌ Error setting primary recipient: {e}")

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Manage email recipients for the fitness reporting system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_email_recipients.py list
  python manage_email_recipients.py add coach@example.com --name "Primary Coach" --role coach
  python manage_email_recipients.py add assistant@example.com --name "Assistant" --role cc
  python manage_email_recipients.py remove assistant@example.com
  python manage_email_recipients.py update coach@example.com --active false
  python manage_email_recipients.py set-primary coach@example.com
  python manage_email_recipients.py config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all email recipients')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new email recipient')
    add_parser.add_argument('email', help='Email address')
    add_parser.add_argument('--name', help='Recipient name')
    add_parser.add_argument('--role', choices=['coach', 'cc'], default='cc', 
                           help='Recipient role (default: cc)')
    add_parser.add_argument('--active', type=bool, default=True, 
                           help='Whether recipient is active (default: True)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove an email recipient')
    remove_parser.add_argument('email', help='Email address to remove')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update recipient properties')
    update_parser.add_argument('email', help='Email address to update')
    update_parser.add_argument('--name', help='New recipient name')
    update_parser.add_argument('--role', choices=['coach', 'cc'], help='New recipient role')
    update_parser.add_argument('--active', type=bool, help='Whether recipient is active')
    
    # Set primary command
    primary_parser = subparsers.add_parser('set-primary', help='Set the primary recipient')
    primary_parser.add_argument('email', help='Email address to set as primary')
    
    # Config command
    subparsers.add_parser('config', help='Show configuration summary')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_recipients()
        elif args.command == 'add':
            add_recipient(args.email, args.name, args.role, args.active)
        elif args.command == 'remove':
            remove_recipient(args.email)
        elif args.command == 'update':
            kwargs = {}
            if args.name is not None:
                kwargs['name'] = args.name
            if args.role is not None:
                kwargs['role'] = args.role
            if args.active is not None:
                kwargs['active'] = args.active
            update_recipient(args.email, **kwargs)
        elif args.command == 'set-primary':
            set_primary_recipient(args.email)
        elif args.command == 'config':
            show_configuration()
    
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
