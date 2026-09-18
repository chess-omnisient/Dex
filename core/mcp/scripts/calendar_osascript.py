#!/usr/bin/env python3
"""
Calendar queries using osascript (reliable fallback when EventKit permission fails).

Usage:
    calendar_osascript.py list
    calendar_osascript.py events <calendar_name> <start_offset> <end_offset>
    calendar_osascript.py next <calendar_name> <days>
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta


def run_osascript(script):
    """Execute AppleScript and return result."""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        return None


def list_calendars():
    """List all available calendars using osascript."""
    script = '''
tell application "Calendar"
    set calNames to name of every calendar
    set result to ""
    repeat with calName in calNames
        set result to result & calName & linefeed
    end repeat
    return result
end tell
'''
    
    output = run_osascript(script)
    if not output:
        print(json.dumps({"error": "Could not access calendars via osascript"}))
        sys.exit(1)
    
    calendars = [cal.strip() for cal in output.split('\n') if cal.strip()]
    result = [{"title": cal, "type": "local", "identifier": cal} for cal in calendars]
    print(json.dumps({"calendars": result}, indent=2))


def get_events(calendar_name, start_offset, end_offset):
    """Get events from a calendar using osascript."""
    start_date = datetime.now() + timedelta(days=int(start_offset))
    end_date = datetime.now() + timedelta(days=int(end_offset))
    
    start_str = start_date.strftime("%.1m/%.1d/%Y")
    end_str = end_date.strftime("%.1m/%.1d/%Y")
    
    script = f'''
tell application "Calendar"
    set targetCalendar to calendar "{calendar_name}"
    set myEvents to events of targetCalendar whose start date is greater than or equal to date "{start_str}" and end date is less than or equal to date "{end_str}"
    
    set result to ""
    repeat with myEvent in myEvents
        set eventTitle to summary of myEvent
        set eventStart to start date of myEvent
        set eventEnd to end date of myEvent
        set eventDetails to eventTitle & "|" & (eventStart as string) & "|" & (eventEnd as string)
        set result to result & eventDetails & linefeed
    end repeat
    return result
end tell
'''
    
    output = run_osascript(script)
    if not output:
        print(json.dumps({"error": f"Could not retrieve events from calendar '{calendar_name}'"}))
        sys.exit(1)
    
    events = []
    for line in output.split('\n'):
        if line.strip() and '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                events.append({
                    "title": parts[0].strip(),
                    "start": parts[1].strip(),
                    "end": parts[2].strip()
                })
    
    print(json.dumps({"events": events}, indent=2))


def get_next_event(calendar_name, days=7):
    """Get next upcoming event from a calendar."""
    end_date = datetime.now() + timedelta(days=int(days))
    end_str = end_date.strftime("%.1m/%.1d/%Y")
    
    script = f'''
tell application "Calendar"
    set targetCalendar to calendar "{calendar_name}"
    set myEvents to events of targetCalendar whose start date is greater than or equal to (current date) and start date is less than or equal to date "{end_str}"
    
    if (count of myEvents) > 0 then
        set firstEvent to item 1 of myEvents
        set eventTitle to summary of firstEvent
        set eventStart to start date of firstEvent
        set eventEnd to end date of firstEvent
        return eventTitle & "|" & (eventStart as string) & "|" & (eventEnd as string)
    else
        return ""
    end if
end tell
'''
    
    output = run_osascript(script)
    if not output:
        print(json.dumps({"error": "No events found", "calendar": calendar_name}))
    else:
        parts = output.split('|')
        if len(parts) >= 3:
            print(json.dumps({
                "title": parts[0].strip(),
                "start": parts[1].strip(),
                "end": parts[2].strip()
            }, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: calendar_osascript.py list|events|next <args>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_calendars()
    elif command == "events" and len(sys.argv) >= 5:
        get_events(sys.argv[2], sys.argv[3], sys.argv[4])  
    elif command == "next" and len(sys.argv) >= 3:
        get_next_event(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 7)
    else:
        print(f"Unknown command or missing arguments: {command}")
        sys.exit(1)
