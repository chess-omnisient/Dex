# Meeting Prep - Agent Instructions

You are gathering context for a meeting prep brief. Gather context from every
available source about the meeting and its attendees, then return a structured
brief. You gather; the main conversation confirms which meeting is meant and
presents the brief to the user.

**Meeting:** {{MEETING_TITLE}}
**Attendees:** {{ATTENDEES}}
**Date:** {{TARGET_DATE}}

---

## Phase 1: Context Gathering

Gather ALL of the following, in parallel where possible. If any source fails or
is not set up, skip it silently.

### 1.1 Meeting Intelligence

```
Use: get_meeting_context(meeting_title="{{MEETING_TITLE}}", attendees=[...attendee names...])
```

Get: related project, project status, outstanding tasks with attendees, prep
suggestions.

### 1.2 Attendee Lookup

For each attendee:

1. **Fast lookup first:** `lookup_person(name="Attendee Name")`
2. **If found**, read the person page and extract: role and company, last
   interaction date and topic, open action items involving them, key context
   and relationship notes
3. **If not found in the index**, check `05-Areas/People/Internal/` and
   `05-Areas/People/External/` via glob
4. **If no person page exists**, note: "No person page for [Name]; consider
   creating one after the meeting"

### 1.3 Related Projects

Search `04-Projects/` for projects that are mentioned in attendees' person
pages, relate to the meeting topic, or were surfaced by `get_meeting_context`.

### 1.4 Recent Meeting History

```
Use: query_meeting_cache(attendee="Attendee Name")
Use: query_meeting_cache(keyword="{{MEETING_TITLE}}")
```

Extract: previous discussions, decisions, open follow-ups, recurring topics.

### 1.5 Semantic Context Enrichment (if QMD available)

Check the QMD `status` tool. If available:

1. **Topic search:** `query` with the meeting title (exact) and a semantic
   variant ("discussions and decisions about {{MEETING_TITLE}}")
2. **Attendee search (beyond person pages):** `query` per attendee for
   context, discussions, decisions and commitments

Only surface NEW insights not found in steps 1.1 to 1.4. If QMD is
unavailable, skip silently.

### 1.6 Integration Context (if available)

Check `System/integrations/config.yaml` for enabled integrations (email, Slack,
Teams, Notion, and similar). For each enabled and responding MCP:
- Search for the attendees and the meeting topic
- Look for recent exchanges, outstanding requests, shared documents
- Label context by source and deduplicate across sources

Skip silently for anything not connected.

---

## Phase 2: Assemble the Brief

Combine context into:
- **People Context:** role, last interaction, open items, key context per
  attendee
- **Related Projects:** active projects connecting to this meeting, with status
  and relevance
- **Recent History:** previous meetings, decisions, open follow-ups
- **Integration Context:** labelled by source, only where something was found
- **Semantic Connections:** thematically related past discussions
- **Suggested Talking Points:** prioritised by importance
- **Questions to Consider:** strategic questions for the meeting's goals

---

## Final Output

Return the assembled brief as structured findings, matching this skill's
Output Format so the conversation can present it directly. Prefix with a short
header:

```
AGENT COMPLETE

Meeting: {{MEETING_TITLE}} on {{TARGET_DATE}}
Attendees with person pages: [N] of [M]
Related projects: [N]
Key open items: [N]

[The full brief follows, in the skill's Output Format]
```

---

## Important Notes

- Be concise: focus on what is actionable for this specific meeting
- Use real data from tools; never fabricate
- Omit empty sections entirely
- Flag anything you could not verify rather than guessing

---

## Matching a capture to a calendar event

A capture and a calendar event are the same meeting when their **start times
agree within about five minutes**. Start time is the key. The title is
corroborating evidence, and a good one where it exists.

Title alone cannot be the key, because a recorder names a capture from whatever
it can see. Where the recorder has calendar access the title is the invite
subject and is highly reliable. Where it does not, the same meeting arrives
named after a participant, as "Untitled", or with no title at all. Start time is
the one field every source populates and the one the user did not type, so it is
what holds in both cases.

**Use the title when you have it.** A title matching the event raises confidence
and breaks ties. A title that disagrees is worth noting, and is not on its own a
reason to reject a start-time match, since the mismatch is usually the recorder
having named the capture some other way.

**The trap that makes this fail silently.** Sources commonly return UTC (an ISO
timestamp ending in `Z`) while the calendar returns local time with an offset.
Comparing the two as text, or as naive datetimes, is wrong by exactly the
UTC offset: under a summer offset of one hour, a perfect match reads as a 60
minute gap and the meeting is filed as ad-hoc. **Convert both to a common
timezone before subtracting.** Never compare the strings.

**When two events are close together:**

- Take the nearest start within the window. If two are inside it, break the tie
  on title agreement first, then on participant overlap, and say the match was
  ambiguous.
- Outside the window, do not stretch it to force a match. An unmatched capture
  recorded as ad-hoc is recoverable; one attached to the wrong meeting is not,
  because everything downstream inherits the error.

**Take the identity, not the payload.** A matched event contributes the meeting
it *is*: title, time, attendees. Where the capture is untitled or poorly titled
and the calendar event is not, **prefer the calendar title** and carry it
through to the note, so a capture named "Untitled" is filed under the meeting it
actually was. Joining links, dial-ins and access codes belong to the invite and
are not written into notes or person pages.

This is source-agnostic on purpose. Start time is the only field it *requires*,
so it holds for whichever recorder the user has configured, and it uses the
title, participants and anything else the source provides as corroboration
wherever those exist.
