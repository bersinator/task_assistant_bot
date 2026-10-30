Morning Google Calendar and Trello sync. You are the user's task assistant (rules - `CLAUDE.md` in this folder; they apply here too, together with the settings from `local/`). The user is not around: don't ask anything, do what is described below, and put everything else in the report. Reply in the language from `local/profile.md`.

If `local/profile.md`, `local/board.md` or `local/schedule.md` is missing or still has `<...>` placeholders, change nothing and make your last message: "Sync not run: local/ is not set up".

## Inputs

- The user's time zone is in `local/profile.md`. "Today" is the current date in that zone. In the calendar always pass that zone's `timeZone`, with times without `Z` or an offset. Trello stores due dates in UTC.
- Calendar - the user's primary calendar, Google Calendar connector (`list_events`, `create_event`, `update_event`).
- Trello - the board from `local/board.md`, Trello connector (`trelloReadCard`, `trelloWriteCard`, `trelloSearch`). Lists and labels go by role; their ARIs are in `local/board.md`. The routine never sets the urgent label.
- Event <-> card link: the event description contains the card link `https://trello.com/c/<shortLink>` (8 characters). An event for a card: same title as the card, description `Trello card: https://trello.com/c/<shortLink>`, no `colorId`, default reminders.
- Read lists with `trelloReadCard` `list_by_list` (with pagination). Don't read the whole board with `list_by_board`. Trello search may show a card's old location - trust the lists for the exact state.

## Stage 1. Calendar -> Trello

1. Get today's events: `list_events` from 00:00 to 24:00 today, `orderBy: startTime`.
2. Keep only "tasks". Skip:
   - events with a `colorId` (the routine from `local/schedule.md`);
   - recurring events (they have a `recurringEventId`);
   - uncolored routine listed in `local/schedule.md`, plus routine blocks such as morning routine, meals, sleep and work;
   - all-day events (`start.date` without a time) - only list them in the report.
3. For each remaining event find its card:
   - the description has a `trello.com/c/...` link -> the card by that link (`trelloReadCard` `get`). Several links - all those cards. If the card is archived (`closed: true`) or won't open, don't create a new one; put it in the report;
   - no link -> look for a card with the same or a very similar title: the Today, This week and Inbox lists, the project backlogs, then `trelloSearch` by title on the board. Exactly one open card found -> add its link to the event description (`update_event`, keep the old description: a new line `Trello card: ...` at the end). Several matches -> change nothing, put it in the report;
   - nothing found -> create a card in Today: title as the event's, labels by meaning (from `local/board.md`; if none fits - no labels), `due` - the event start in UTC. Then add the new card's link to the event description as above.
4. **A task in today's calendar means its card belongs in Today.** For each card found:
   - the card is in Done or marked complete (`dueComplete`/`complete`) -> leave it, put it in the report ("in today's calendar but already done");
   - the card is in any other list (Inbox, This week, a backlog, To buy, etc.) -> move it to Today (`trelloWriteCard` `move`), keeping its labels;
   - no due date or it isn't today -> set `due` = the event start in UTC. If the card is already due today, don't change it.
   - Order in Today: by event start time, earlier is higher.
5. If Today has more than 3 cards after this, don't postpone anything yourself; just note it in the report ("Today has N tasks, more than 3 main ones").

## Stage 2. Trello -> calendar

1. Read the Today and This week lists again (after stage 1). Skip finished cards (`dueComplete` or `complete`).
2. For each card check whether it's in the calendar: `list_events` with `fullText` = the card's shortLink, range from 14 days ago to 30 days ahead. Nothing found - the same search with `fullText` = the card title, matching the event title to the card title case-insensitively. Found - the card is in the calendar, do nothing.
3. Cards that aren't in the calendar:
   - **due with a specific time** (a `due` whose local time isn't 12:00; 12:00 local means "date only"), due today or later -> an event at that time, 1 hour;
   - **Today cards with no due date, due today by date only, or overdue**, plus This week cards due today by date only -> a 1-hour event in the nearest free slot today, in list order (higher - earlier);
   - **everything else** (This week cards with no due date, due by date on another day, overdue This week cards) -> don't schedule, list them in the report.
4. A free slot today is a gap of at least an hour between 07:00 and 23:00 with **no** events at all (including routine, colored and recurring ones), and not earlier than now. Before each new event, account for the ones already created in this run. No slot - don't schedule, put it in the report.
5. An event at a specific time overlaps "Work" (the work color from `local/schedule.md`) - shorten work on the overlapping side; if it lands in the middle of work, split "Work" in two (the new one gets the same `colorId`, `useDefaultReminders: false`). Don't overlap other events: if the time is taken by something other than work, still create the event and note the overlap in the report.

## Restrictions

- Don't delete, archive or mark anything complete. Move cards only into Today, per stage 1. Change events only by adding a link to the description or shortening "Work" per stage 2.
- If one stage would create more than 5 new cards, more than 5 new events or more than 8 moves, that looks like a mistake: create and move nothing in that stage, and list in the report what you were going to do.
- Don't mention other board members and don't assign members.
- Running again the same day must not duplicate anything: always search by link and title first.

## Report

The last message is a short report (up to ~15 lines), cards with the number from their link (`/c/<shortLink>/390-...` -> #390):

```
Sync <YYYY-MM-DD>
Calendar -> Trello: moved to Today N, created M cards, linked K events
- #383 Get the passport renewed - 09:00, from Inbox
Trello -> calendar: scheduled K events
- #411 Haircut - 19:30-20:30
No time in the calendar (to decide):
- ...
Problems: ...
```

Skip empty sections. If nothing changed, say so in one line and list the "No time in the calendar" section if it isn't empty.
