#!/usr/bin/env python3
"""
Email Configuration Module for Fitness Reporting System
Provides flexible email recipient management and configuration.
"""

import os
import json
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class EmailRecipient:
    """Email recipient configuration"""
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    active: bool = True

@dataclass
class EmailConfig:
    """Email configuration settings"""
    primary_recipient: str
    cc_recipients: List[str] = None
    subject_prefix: str = "Charles Parmar : Progress Report"
    reply_to: Optional[str] = None
    send_notifications: bool = True

class EmailConfigurationManager:
    """Manages email configuration with support for multiple recipients and environments"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the email configuration manager
        
        Args:
            config_file: Optional path to JSON configuration file
        """
        self.config_file = config_file or "config/email_recipients.json"
        self._recipients: List[EmailRecipient] = []
        self._config: Optional[EmailConfig] = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load email configuration from file and environment variables"""
        # Load from JSON file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self._load_from_json(data)
            except Exception as e:
                print(f"⚠️ Warning: Could not load email config from {self.config_file}: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Set default configuration if none exists
        if not self._config:
            self._config = EmailConfig(
                primary_recipient=self._get_primary_recipient(),
                subject_prefix=os.getenv('EMAIL_SUBJECT_PREFIX', '[Fitness Report]'),
                send_notifications=os.getenv('EMAIL_SEND_NOTIFICATIONS', 'true').lower() == 'true'
            )
    
    def _load_from_json(self, data: Dict):
        """Load configuration from JSON data"""
        # Load recipients
        if 'recipients' in data:
            for recipient_data in data['recipients']:
                recipient = EmailRecipient(
                    email=recipient_data['email'],
                    name=recipient_data.get('name'),
                    role=recipient_data.get('role'),
                    active=recipient_data.get('active', True)
                )
                self._recipients.append(recipient)
        
        # Load email config
        if 'config' in data:
            config_data = data['config']
            self._config = EmailConfig(
                primary_recipient=config_data.get('primary_recipient', ''),
                cc_recipients=config_data.get('cc_recipients', []),
                subject_prefix=config_data.get('subject_prefix', 'Charles Parmar : Progress Report'),
                reply_to=config_data.get('reply_to'),
                send_notifications=config_data.get('send_notifications', True)
            )
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Load EMAIL_TO as primary recipient
        email_to = os.getenv('EMAIL_TO')
        if email_to and not self._recipients:
            self._recipients.append(EmailRecipient(
                email=email_to,
                name="Primary Coach",
                role="coach",
                active=True
            ))
        
        # Load CC recipients from environment
        cc_emails = os.getenv('EMAIL_CC', '').split(',')
        for email in cc_emails:
            email = email.strip()
            if email and email not in [r.email for r in self._recipients]:
                self._recipients.append(EmailRecipient(
                    email=email,
                    role="cc",
                    active=True
                ))
    
    def _get_primary_recipient(self) -> str:
        """Get the primary recipient email"""
        # First try to get from active recipients
        active_recipients = [r for r in self._recipients if r.active]
        if active_recipients:
            # Find primary coach or first active recipient
            primary = next((r for r in active_recipients if r.role == 'coach'), active_recipients[0])
            return primary.email
        
        # Fallback to environment variable
        return os.getenv('EMAIL_TO', 'coach@example.com')
    
    def get_primary_recipient(self) -> str:
        """Get the primary recipient email address"""
        return self._config.primary_recipient if self._config else self._get_primary_recipient()
    
    def get_all_recipients(self) -> List[str]:
        """Get all active recipient email addresses"""
        return [r.email for r in self._recipients if r.active]
    
    def get_cc_recipients(self) -> List[str]:
        """Get CC recipient email addresses"""
        if self._config and self._config.cc_recipients:
            return self._config.cc_recipients
        return [r.email for r in self._recipients if r.active and r.role == 'cc']
    
    def get_bcc_recipients(self) -> List[str]:
        """Get BCC recipient email addresses (deprecated - always returns empty list)"""
        return []
    
    def get_subject_prefix(self) -> str:
        """Get email subject prefix"""
        return self._config.subject_prefix if self._config else '[Fitness Report]'
    
    def get_reply_to(self) -> Optional[str]:
        """Get reply-to email address"""
        return self._config.reply_to if self._config else None
    
    def should_send_notifications(self) -> bool:
        """Check if notifications should be sent"""
        return self._config.send_notifications if self._config else True
    
    def add_recipient(self, email: str, name: Optional[str] = None, role: str = 'cc', active: bool = True):
        """Add a new recipient"""
        recipient = EmailRecipient(email=email, name=name, role=role, active=active)
        self._recipients.append(recipient)
        self._save_configuration()
    
    def remove_recipient(self, email: str):
        """Remove a recipient by email"""
        self._recipients = [r for r in self._recipients if r.email != email]
        self._save_configuration()
    
    def update_recipient(self, email: str, **kwargs):
        """Update recipient properties"""
        for recipient in self._recipients:
            if recipient.email == email:
                for key, value in kwargs.items():
                    if hasattr(recipient, key):
                        setattr(recipient, key, value)
                break
        self._save_configuration()
    
    def _save_configuration(self):
        """Save configuration to JSON file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            data = {
                'recipients': [
                    {
                        'email': r.email,
                        'name': r.name,
                        'role': r.role,
                        'active': r.active
                    }
                    for r in self._recipients
                ],
                'config': {
                    'primary_recipient': self._config.primary_recipient if self._config else '',
                    'cc_recipients': self._config.cc_recipients if self._config else [],
                    'subject_prefix': self._config.subject_prefix if self._config else 'Charles Parmar : Progress Report',
                    'reply_to': self._config.reply_to if self._config else None,
                    'send_notifications': self._config.send_notifications if self._config else True
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Warning: Could not save email configuration: {e}")
    
    def get_configuration_summary(self) -> Dict:
        """Get a summary of the current email configuration"""
        return {
            'primary_recipient': self.get_primary_recipient(),
            'all_recipients': self.get_all_recipients(),
            'cc_recipients': self.get_cc_recipients(),
            'subject_prefix': self.get_subject_prefix(),
            'reply_to': self.get_reply_to(),
            'send_notifications': self.should_send_notifications(),
            'total_recipients': len(self.get_all_recipients())
        }

# Global instance for easy access
email_config = EmailConfigurationManager()

def get_email_to() -> str:
    """Get the primary email recipient (backward compatibility)"""
    return email_config.get_primary_recipient()

def get_email_recipients() -> List[str]:
    """Get all email recipients"""
    return email_config.get_all_recipients()

def get_email_cc() -> List[str]:
    """Get CC email recipients"""
    return email_config.get_cc_recipients()


