#!/usr/bin/env python3
"""
Request calendar permission using osascript (more reliable).
"""

import subprocess
import sys
import time

try:
    import EventKit
except ImportError:
    print("❌ EventKit not installed. Run: pip3 install pyobjc-framework-EventKit")
    sys.exit(1)


def check_permission():
    """Check current permission status."""
    store = EventKit.EKEventStore.alloc().init()
    status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
    
    status_names = {
        0: "NotDetermined",
        1: "Restricted",
        2: "Denied",
        3: "Authorized"
    }
    return status, status_names.get(status, 'Unknown')


def main():
    status, status_name = check_permission()
    print(f"Current calendar access: {status_name}")
    
    if status == 3:  # Authorized
        print("✅ Calendar access already granted!")
        return 0
    
    elif status == 2:  # Denied
        print("❌ Calendar access was previously denied.")
        print("\nTo enable:")
        print("1. Open System Settings")
        print("2. Go to Privacy & Security > Calendars")
        print("3. Find the app you use (Terminal, Cursor, VS Code, etc)")
        print("4. Toggle it ON")
        print("\nThen run this script again.")
        return 1
    
    elif status == 1:  # Restricted
        print("❌ Calendar access is restricted by system policies.")
        return 1
    
    # Try via Calendar.app (which definitely has calendar access)
    print("\nRequesting calendar access via Calendar.app...")
    
    apple_script = """
tell application "Calendar"
    activate
end tell
"""
    
    try:
        subprocess.run(['osascript', '-e', apple_script], check=True, timeout=5)
    except Exception as e:
        print(f"Note: {e}")
    
    # Now try the EventKit request
    print("Requesting EventKit access...")
    
    access_granted = [None]
    
    def completion_handler(granted, error):
        access_granted[0] = granted
        if granted:
            print("✅ Access granted!")
        else:
            print("❌ Access not granted")
    
    store = EventKit.EKEventStore.alloc().init()
    store.requestAccessToEntityType_completion_(
        EventKit.EKEntityTypeEvent,
        completion_handler
    )
    
    # Wait up to 30 seconds
    for i in range(300):
        if access_granted[0] is not None:
            break
        time.sleep(0.1)
        if i % 50 == 0:
            print(".", end="", flush=True)
    
    print()
    
    # Check final status
    status, status_name = check_permission()
    if status == 3:
        print("✅ Success! Calendar access is now enabled.")
        return 0
    else:
        print(f"Status: {status_name}")
        print("\nIf you see 'Terminal' or 'Python' in System Settings > Privacy & Security > Calendars,")
        print("make sure it's toggled ON.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
