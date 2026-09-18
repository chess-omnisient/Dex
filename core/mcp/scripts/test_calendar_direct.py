#!/usr/bin/env python3
"""
Test direct calendar access without prompting.
"""

try:
    import EventKit
    from Foundation import NSDate
    
    # Create event store
    store = EventKit.EKEventStore.alloc().init()
    
    # Check authorization status
    status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
    status_names = {0: "NotDetermined", 1: "Restricted", 2: "Denied", 3: "Authorized"}
    print(f"Authorization status: {status_names[status]}")
    
    # Try to get calendars
    calendars = store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
    print(f"Calendars found: {calendars.count() if calendars else 0}")
    
    if calendars and calendars.count() > 0:
        print("✅ Calendar access is working!")
        for i in range(min(3, calendars.count())):
            cal = calendars.objectAtIndex_(i)
            print(f"  - {cal.title()}")
    else:
        print("❌ No calendars found or access denied")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
