"""
Delete handyman test events from the user's primary Google Calendar.

Targets future events whose summary starts with
"Handyman Appointment - Test" or "Handyman Appointment - TEST".
Run before or after manual testing to keep the calendar clean.

Usage:
    python cleanup_test_events.py
"""
from datetime import datetime, timezone

from dotenv import load_dotenv

from myscheduling_tool import get_calendar_service


TEST_PREFIXES = (
    "Handyman Appointment - Test",
    "Handyman Appointment - TEST",
)


def main():
    load_dotenv()
    svc = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()

    result = svc.events().list(
        calendarId="primary",
        q="Handyman Appointment",
        timeMin=now,
        maxResults=250,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    test_events = [
        ev for ev in result.get("items", [])
        if ev.get("summary", "").startswith(TEST_PREFIXES)
    ]

    if not test_events:
        print("No test events found.")
        return

    print(f"Found {len(test_events)} test event(s):")
    for ev in test_events:
        start = ev.get("start", {}).get("dateTime", "?")
        print(f"  - {ev.get('summary')} | {start}")

    print("\nDeleting...")
    for ev in test_events:
        svc.events().delete(calendarId="primary", eventId=ev["id"]).execute()
        print(f"  deleted: {ev.get('summary')}")

    print(f"\nDone. Removed {len(test_events)} event(s).")


if __name__ == "__main__":
    main()
