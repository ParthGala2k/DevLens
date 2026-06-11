#!/usr/bin/env python3
"""
Google Calendar Seeding Script — DevLens Hackathon
Creates calendar events for each persona consistent with the sprint story.

Usage:
  python3 seed_calendar.py --persona riya
  python3 seed_calendar.py --persona arjun
  python3 seed_calendar.py --persona priya
  python3 seed_calendar.py --persona james

Each person runs this with their OWN Google account.
Browser will open once for authorization, then events are created automatically.
"""

import argparse
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SPRINT_START = datetime(2025, 5, 1)  # Thursday

def day_to_dt(day, hour, minute=0):
    """Convert day number to real datetime."""
    return SPRINT_START + timedelta(days=day-1, hours=hour, minutes=minute)

def event(summary, day, start_hour, end_hour,
          start_min=0, end_min=0, color_id=None, description=None):
    """Build a Google Calendar event dict."""
    start = day_to_dt(day, start_hour, start_min)
    end   = day_to_dt(day, end_hour,   end_min)
    e = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": "America/Los_Angeles"},
        "end":   {"dateTime": end.isoformat(),   "timeZone": "America/Los_Angeles"},
    }
    if color_id:
        e["colorId"] = color_id
    if description:
        e["description"] = description
    return e


# ─── Sprint ceremonies — appear on ALL 4 calendars ───────────────────────────

SHARED_EVENTS = [
    # Sprint 1
    event("Sprint 1 Planning — Service Registry",        day=1,  start_hour=10, end_hour=12),
    event("Sprint 1 Review / Demo",                      day=13, start_hour=15, end_hour=16),
    event("Sprint 1 Retrospective",                      day=14, start_hour=14, end_hour=15),
    # Sprint 2
    event("Sprint 2 Planning — Health Dashboard",        day=15, start_hour=10, end_hour=12),
    event("Sprint 2 Review / Demo",                      day=27, start_hour=15, end_hour=16),
    event("Sprint 2 Retrospective",                      day=28, start_hour=14, end_hour=15),
    # Sprint 3
    event("Sprint 3 Planning — Deployment Manager",      day=29, start_hour=10, end_hour=12),
    # Weekly team sync — every Monday (Days 5, 12, 19, 26, 33)
    event("Weekly Team Sync",                            day=5,  start_hour=9,  end_hour=10),
    event("Weekly Team Sync",                            day=12, start_hour=9,  end_hour=10),
    event("Weekly Team Sync",                            day=19, start_hour=9,  end_hour=10),
    event("Weekly Team Sync",                            day=26, start_hour=9,  end_hour=10),
    event("Weekly Team Sync",                            day=33, start_hour=9,  end_hour=10),
]


# ─── Riya Desai — Senior Backend Eng + On-Call ───────────────────────────────
# Pattern: Incident blocks explain delayed PR reviews
# Incident 1: Day 16 (Tue May 20) 11:23pm → Day 17 (Wed May 21) 3:41am
# Incident 2: Day 26 (Mon May 26) 10:58pm → Day 27 (Tue May 27) 12:30am
# Incident 3: Day 35 (Wed Jun 4)  2:17pm  → Day 35 4:55pm

RIYA_EVENTS = SHARED_EVENTS + [
    # Normal engineering meetings
    event("Technical Spec Review",          day=3,  start_hour=14, end_hour=15),
    event("Code Review Office Hours",       day=2,  start_hour=10, end_hour=11),
    event("Architecture Design Review",     day=8,  start_hour=11, end_hour=12),
    event("Code Review Office Hours",       day=9,  start_hour=10, end_hour=11),
    event("1:1 with Engineering Manager",   day=12, start_hour=14, end_hour=15),
    event("Technical Spec Review",          day=17, start_hour=14, end_hour=15),
    event("Code Review Office Hours",       day=23, start_hour=10, end_hour=11),
    event("1:1 with Engineering Manager",   day=26, start_hour=11, end_hour=12),
    event("On-Call Rotation Handoff",       day=29, start_hour=9,  end_hour=10),
    event("Code Review Office Hours",       day=30, start_hour=10, end_hour=11),

    # ── INCIDENT 1: Tue May 20 11:23pm → Wed May 21 3:41am ──────────────────
    # This is the incident that causes 3-day PR review delay on SLS-41
    {
        "summary": "🚨 ON-CALL: health-check-service 503 outage",
        "description": (
            "PagerDuty alert: health-check-service returning 503.\n"
            "Woke up at 11:23pm. Resolved at 3:41am.\n"
            "Root cause: DB connection pool exhausted under load.\n"
            "This explains slow PR reviews on Wednesday May 21."
        ),
        "start": {
            "dateTime": day_to_dt(16, 23, 23).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": day_to_dt(17, 3, 41).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "colorId": "11",  # Red
    },
    # Wednesday morning recovery — no early meetings
    event("Recovery / Catch-up (post-incident)",
          day=17, start_hour=10, end_hour=11,
          description="Post-incident review and rest after overnight on-call."),

    # ── INCIDENT 2: Mon May 26 10:58pm → Tue May 27 12:30am ─────────────────
    {
        "summary": "🚨 ON-CALL: service-registry DB connection failure",
        "description": (
            "PagerDuty alert: service-registry DB connections exhausted.\n"
            "Paged at 10:58pm Monday. Resolved at 12:30am Tuesday."
        ),
        "start": {
            "dateTime": day_to_dt(26, 22, 58).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": day_to_dt(27, 0, 30).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "colorId": "11",  # Red
    },

    # ── INCIDENT 3: Wed Jun 4 2:17pm → 4:55pm ───────────────────────────────
    # This incident happens during work hours — directly cuts into review time
    {
        "summary": "🚨 ON-CALL: deployment-service job queue timeout",
        "description": (
            "PagerDuty alert during work hours.\n"
            "Deployment jobs stuck in queue, timing out after 30 min.\n"
            "Start: 2:17pm. Resolved: 4:55pm."
        ),
        "start": {
            "dateTime": day_to_dt(35, 14, 17).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": day_to_dt(35, 16, 55).isoformat(),
            "timeZone": "America/Los_Angeles"
        },
        "colorId": "11",  # Red
    },
]


# ─── Arjun Mehta — Mid-level Backend Eng ─────────────────────────────────────
# Pattern: Normal schedule, no special calendar patterns
# His story is told through commits and PR timing, not calendar

ARJUN_EVENTS = SHARED_EVENTS + [
    event("1:1 with Riya (mentoring check-in)", day=3,  start_hour=11, end_hour=12),
    event("Backend Team Sync",                  day=8,  start_hour=14, end_hour=15),
    event("1:1 with Engineering Manager",       day=12, start_hour=15, end_hour=16),
    event("Backend Team Sync",                  day=22, start_hour=14, end_hour=15),
    event("1:1 with Engineering Manager",       day=26, start_hour=15, end_hour=16),
    event("Backend Team Sync",                  day=36, start_hour=14, end_hour=15),
    # Sprint 3 SLS-46 unblocking meeting
    event("OAuth Implementation Review (SLS-46 final sign-off)", day=33,
          start_hour=14, end_hour=15,
          description="Blocked on Riya's review. Trying to get this unblocked."),
]


# ─── Priya Nair — Frontend Tech Lead ─────────────────────────────────────────
# KEY PATTERN: Packed Tue/Wed every week. Zero productive coding time those days.
# DevLens should detect: meeting load on Tue/Wed correlates with slow PR cycle times.

PRIYA_EVENTS = SHARED_EVENTS + [
    # ── Sprint 1 Week 2: Tue May 6 + Wed May 7 ───────────────────────────────
    event("1:1 with Engineering Manager",           day=6,  start_hour=9,  end_hour=10),
    event("Architecture Review — Service Registry", day=6,  start_hour=10, end_hour=12),
    event("Product Roadmap Planning",               day=6,  start_hour=13, end_hour=14),
    event("Design Review — UI Components",          day=6,  start_hour=14, end_hour=15),
    event("Frontend Guild Meeting",                 day=6,  start_hour=15, end_hour=16,
          description="Weekly frontend guild — UI patterns, component library updates."),

    event("Cross-team Sync — Platform Dependencies", day=7, start_hour=10, end_hour=12),
    event("Design Review with Yuki",                 day=7, start_hour=13, end_hour=14),
    event("Quarterly Planning Prep",                 day=7, start_hour=14, end_hour=15),
    event("Sprint Commitment Review",                day=7, start_hour=15, end_hour=16),

    # ── Sprint 1 Week 3: Tue May 13 + Wed May 14 ─────────────────────────────
    event("API Review with Backend Team",            day=13, start_hour=9,  end_hour=10),
    event("UX Walkthrough — Service Registry",       day=13, start_hour=10, end_hour=11),
    event("Stakeholder Demo Prep",                   day=13, start_hour=13, end_hour=14),
    event("Product Sync — Q2 Roadmap",               day=13, start_hour=14, end_hour=15),
    # Sprint 1 Review already in shared at day=13 15-16

    event("Performance Review Prep",                 day=14, start_hour=10, end_hour=11),
    event("1:1 with Engineering Manager",            day=14, start_hour=11, end_hour=12),
    # Sprint 1 Retro already in shared at day=14 14-15

    # ── Sprint 2 Week 1: Tue May 20 + Wed May 21 ─────────────────────────────
    # Note: May 20 is the PagerDuty incident night for Riya
    event("Sprint 2 Kickoff Sync",                   day=20, start_hour=9,  end_hour=10),
    event("Stakeholder Demo — Service Registry",     day=20, start_hour=10, end_hour=12),
    event("Product Roadmap Q2 Review",               day=20, start_hour=13, end_hour=14),
    event("Design Review — Health Dashboard",        day=20, start_hour=14, end_hour=15),
    event("Frontend Hiring Interview",               day=20, start_hour=15, end_hour=16),

    event("Cross-team Architecture Review",          day=21, start_hour=10, end_hour=12),
    event("1:1 Backend-Frontend Sync",               day=21, start_hour=13, end_hour=14),
    event("Frontend Guild Meeting",                  day=21, start_hour=14, end_hour=15),

    # ── Sprint 2 Week 2: Tue May 27 + Wed May 28 ─────────────────────────────
    event("Quarterly Business Review",               day=27, start_hour=9,  end_hour=11),
    event("Product Feature Review",                  day=27, start_hour=11, end_hour=12),
    event("1:1 with Engineering Manager",            day=27, start_hour=13, end_hour=14),
    event("Sprint Demo Prep",                        day=27, start_hour=14, end_hour=15),
    # Sprint 2 Review already in shared at day=27 15-16

    event("Cross-team Dependency Mapping",           day=28, start_hour=10, end_hour=12),
    event("Technical Roadmap Review",                day=28, start_hour=13, end_hour=14),
    # Sprint 2 Retro already in shared at day=28 14-15

    # ── Sprint 3 Week 1: Tue Jun 3 + Wed Jun 4 ───────────────────────────────
    event("Sprint 3 Kickoff + Planning Deep Dive",   day=34, start_hour=9,  end_hour=11),
    event("Product Sync — Deployment Manager",       day=34, start_hour=11, end_hour=12),
    event("Design Review — Deployment Status UI",    day=34, start_hour=13, end_hour=14),
    event("Architecture Review — Access Control",    day=34, start_hour=14, end_hour=16),

    event("Frontend Guild Meeting",                  day=35, start_hour=10, end_hour=11),
    event("Quarterly Business Review (QBR)",         day=35, start_hour=11, end_hour=13),
    event("1:1 with Engineering Manager",            day=35, start_hour=14, end_hour=15),

    # Light days Mon/Thu/Fri — shows the contrast
    event("1:1 with Designer",                       day=1,  start_hour=14, end_hour=15),
    event("Tech Lead Sync",                          day=8,  start_hour=11, end_hour=12),
    event("1:1 with Engineering Manager",            day=12, start_hour=14, end_hour=15),
    event("Tech Lead Sync",                          day=22, start_hour=11, end_hour=12),
    event("1:1 with EM",                             day=26, start_hour=14, end_hour=15),
]


# ─── James Okwu — Junior Full-Stack Developer ─────────────────────────────────
# Pattern: Normal junior schedule — learning-focused, improving over time

JAMES_EVENTS = SHARED_EVENTS + [
    event("1:1 with Riya (mentoring)",            day=3,  start_hour=11, end_hour=12),
    event("Code Review Discussion — SLS-32",      day=8,  start_hour=15, end_hour=16,
          description="Discussing Riya's review feedback on the search component."),
    event("1:1 with Riya (mentoring)",            day=10, start_hour=11, end_hour=12),
    event("Junior Dev Learning Session",          day=12, start_hour=15, end_hour=16),
    event("1:1 with Riya (mentoring)",            day=17, start_hour=11, end_hour=12),
    event("Code Review Discussion — SLS-41",      day=22, start_hour=10, end_hour=11,
          description="Following up on review comments from Riya on SLS-41."),
    event("1:1 with Riya (mentoring)",            day=24, start_hour=11, end_hour=12),
    event("Junior Dev Learning Session",          day=26, start_hour=15, end_hour=16),
    event("1:1 with Riya (mentoring)",            day=31, start_hour=11, end_hour=12),
    event("Team Social Lunch",                    day=23, start_hour=12, end_hour=13),
]


# ─── Persona map ──────────────────────────────────────────────────────────────

ALL_EVENTS = {
    "riya":  RIYA_EVENTS,
    "arjun": ARJUN_EVENTS,
    "priya": PRIYA_EVENTS,
    "james": JAMES_EVENTS,
}


# ─── Auth ─────────────────────────────────────────────────────────────────────

def authenticate(persona):
    """OAuth2 flow. Opens browser once, saves token for future runs."""
    token_file = f"token_{persona}.json"
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0, prompt="select_account")
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed Google Calendar for DevLens personas.")
    parser.add_argument("--persona", required=True,
                        choices=["riya", "arjun", "priya", "james"],
                        help="Which persona's events to create on YOUR calendar")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print events without creating them")
    args = parser.parse_args()

    persona    = args.persona
    events     = ALL_EVENTS[persona]
    persona_names = {
        "riya":  "Riya Desai — Senior Backend Eng",
        "arjun": "Arjun Mehta — Mid Backend Eng",
        "priya": "Priya Nair — Frontend Tech Lead",
        "james": "James Okwu — Junior Full-Stack",
    }

    print(f"\n{'='*55}")
    print(f"DevLens Calendar Seeder — {persona_names[persona]}")
    print(f"{'='*55}")
    print(f"Events to create: {len(events)}")

    if args.dry_run:
        print("\nDRY RUN — no events will be created:\n")
        for e in events:
            start = e["start"]["dateTime"]
            print(f"  {start[:16]}  {e['summary']}")
        return

    print("\nOpening browser for Google authorization...")
    service = authenticate(persona)
    print("✓ Authenticated\n")

    created = 0
    failed  = 0
    for e in events:
        try:
            service.events().insert(calendarId="primary", body=e).execute()
            print(f"  ✓ {e['start']['dateTime'][:16]}  {e['summary']}")
            created += 1
        except Exception as err:
            print(f"  ✗ FAILED: {e['summary']} — {err}")
            failed += 1

    print(f"\n{'='*55}")
    print(f"Done! Created: {created}  Failed: {failed}")
    print(f"\nIMPORTANT: Add your real email to persona_mapping table:")
    mapping = {
        "riya":  ("Riya Desai",  "Senior Backend Engineer"),
        "arjun": ("Arjun Mehta", "Mid-level Backend Engineer"),
        "priya": ("Priya Nair",  "Frontend Tech Lead"),
        "james": ("James Okwu",  "Junior Full-Stack Developer"),
    }
    name, role = mapping[persona]
    print(f'  INSERT INTO cadence_analytics.persona_mapping VALUES')
    print(f'  ("YOUR_REAL_EMAIL@gmail.com", "{name}", "{role}");')
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()