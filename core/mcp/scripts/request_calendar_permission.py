#!/usr/bin/env python3
"""
Request calendar permission with EventKit.
"""

import sys
import time
import subprocess

try:
    import EventKit
except ImportError as e:
    print(f"❌ EventKit not installed: {e}")
    print("Run: pip3 install pyobjc-framework-EventKit")
    sys.exit(1)


def show_notification(title, message):
    """Show a macOS notification."""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script], capture_output=True)


def main():
    store = EventKit.EKEventStore.alloc().init()
    status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
    
    status_names = {
        0: "NotDetermined",
        1: "Restricted",
        2: "Denied",
        3: "Authorized"
    }
    
    current_status = status_names.get(status, 'Unknown')
    print(f"Current calendar access: {current_status}")
    
    if status == 3:  # Authorized
        print("✅ Calendar access already granted!")
        return 0
    
    elif status == 2:  # Denied
        print("❌ Calendar access was previously denied.")
        print("\nTo enable:")
        print("1. Open System Settings")
        print("2. Go to Privacy & Security > Calendars")
        print("3. Find 'Python' in the list")
        print("4. Enable the checkbox")
        print("\nThen run this script again.")
        return 1
    
    elif status == 1:  # Restricted
        print("❌ Calendar access is restricted by system policies.")
        print("   (parental controls or enterprise MDM)")
        return 1
    
    else:  # NotDetermined (0)
        print("Requesting calendar access...")
        print("⏳ A system permission dialog should appear. Check your screen...")
        
        access_granted = [None]
        
        def completion_handler(granted, error):
            access_granted[0] = granted
            if granted:
                print("✅ Calendar access granted!")
            else:
                print("❌ Calendar access was not granted.")
        
        store.requestAccessToEntityType_completion_(
            EventKit.EKEntityTypeEvent,
            completion_handler
        )
        
        # Wait for response (max 30 seconds)
        for i in range(300):
            if access_granted[0] is not None:
                break
            time.sleep(0.1)
            if i % 50 == 0:
                print(".", end="", flush=True)
        
        print()
        
        if access_granted[0]:
            return 0
        else:
            print("\nIf 'Python' appears in System Settings > Privacy & Security > Calendars,")
            print("enable it and run this script again.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
