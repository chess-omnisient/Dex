#!/usr/bin/env python3
"""
Verify calendar permission by attempting to create a test event.
"""

import subprocess
import os

# Use osascript to check and request calendar access
script = """
on run
    tell application "System Events"
        tell application "Calendar"
            set myCalendars to title of calendars
            if (count of myCalendars) > 0 then
                return "✅ Calendar access confirmed: " & item 1 of myCalendars
            else
                return "❌ No calendars found"
            end if
        end tell
    end tell
end run
"""

try:
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("Calendar access check (via Calendar.app):")
    print(result.stdout.strip())
    
    if result.returncode == 0 and "✅" in result.stdout:
        print("\n✅ Calculator verified that Calendar is accessible!")
    else:
        print(f"\nNote: {result.stderr}")
        
except Exception as e:
    print(f"Error: {e}")
