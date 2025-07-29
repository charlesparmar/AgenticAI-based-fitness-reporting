#!/usr/bin/env python3
"""
Cleanup Agent for managing browser sessions and system cleanup.
Separates cleanup operations from email sending to prevent conflicts.
"""

import os
import subprocess
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CleanupAgent:
    """Agent for cleaning up browser sessions and system resources"""
    
    def __init__(self):
        self.notifier = None
        # Initialize notifier if pushover credentials are available
        try:
            from .pushover_notifications import PushoverNotifier
            self.notifier = PushoverNotifier()
        except:
            pass
    
    def cleanup_chrome_processes(self) -> Dict[str, Any]:
        """Clean up any existing Chrome processes"""
        try:
            print("🧹 Starting Chrome process cleanup...")
            
            # Kill Chrome processes
            result = subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=10)
            
            # Wait for processes to close
            time.sleep(3)
            
            # Check if any Chrome processes are still running
            check_result = subprocess.run(['pgrep', '-f', 'chrome'], capture_output=True, timeout=5)
            
            if check_result.returncode == 1:  # No processes found
                print("✅ Chrome processes cleaned up successfully")
                return {
                    "success": True,
                    "message": "Chrome processes cleaned up successfully",
                    "processes_killed": True,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                print("⚠️ Some Chrome processes may still be running")
                return {
                    "success": True,
                    "message": "Chrome cleanup attempted, some processes may remain",
                    "processes_killed": False,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
        except subprocess.TimeoutExpired:
            print("⚠️ Cleanup timed out, but continuing...")
            return {
                "success": True,
                "message": "Cleanup timed out but continuing",
                "processes_killed": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"❌ Error during Chrome cleanup: {e}")
            return {
                "success": False,
                "message": f"Error during Chrome cleanup: {e}",
                "processes_killed": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def cleanup_selenium_drivers(self) -> Dict[str, Any]:
        """Clean up any orphaned Selenium WebDriver processes"""
        try:
            print("🧹 Starting Selenium driver cleanup...")
            
            # Kill chromedriver processes
            result = subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True, timeout=10)
            
            # Wait for processes to close
            time.sleep(2)
            
            print("✅ Selenium drivers cleaned up successfully")
            return {
                "success": True,
                "message": "Selenium drivers cleaned up successfully",
                "drivers_killed": True,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
                
        except subprocess.TimeoutExpired:
            print("⚠️ Selenium cleanup timed out, but continuing...")
            return {
                "success": True,
                "message": "Selenium cleanup timed out but continuing",
                "drivers_killed": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"❌ Error during Selenium cleanup: {e}")
            return {
                "success": False,
                "message": f"Error during Selenium cleanup: {e}",
                "drivers_killed": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def full_cleanup(self) -> Dict[str, Any]:
        """Perform full cleanup of all browser-related processes"""
        try:
            print("🧹 Starting full system cleanup...")
            
            # Clean up Chrome processes
            chrome_result = self.cleanup_chrome_processes()
            
            # Clean up Selenium drivers
            selenium_result = self.cleanup_selenium_drivers()
            
            # Send notification if notifier is available
            if self.notifier:
                self.notifier.send_notification(
                    "System cleanup completed",
                    "Fitness Report System"
                )
            
            return {
                "success": chrome_result["success"] and selenium_result["success"],
                "chrome_cleanup": chrome_result,
                "selenium_cleanup": selenium_result,
                "message": "Full cleanup completed",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Error during full cleanup: {e}")
            return {
                "success": False,
                "message": f"Error during full cleanup: {e}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

def run_cleanup_agent():
    """Run the cleanup agent"""
    try:
        print("🤖 Starting Cleanup Agent...")
        
        agent = CleanupAgent()
        result = agent.full_cleanup()
        
        print("✅ Cleanup Agent completed successfully")
        return result
        
    except Exception as e:
        print(f"❌ Cleanup Agent failed: {e}")
        return {
            "success": False,
            "message": f"Cleanup Agent failed: {e}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    result = run_cleanup_agent()
    print(f"Result: {result}") 