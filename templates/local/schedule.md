# Google Calendar schedule

Sample - the project author's colors and routine. Copy to `local/schedule.md` and replace the routine with yours (the agent asks about it following `README.md`). If you don't use the calendar, leave only the line "The calendar is not used".

## Colors and reminders

Color marks the routine, blue (no color set) marks tasks. Reminders are **only on blue events, the default one, 30 minutes before**; colored events have no reminders (`useDefaultReminders: false`), otherwise the phone rings all day.

| Color | `colorId` | What | Reminder |
|---|---|---|---|
| Flamingo (pink) | `4` | work | none |
| Graphite (grey) | `8` | sleep, morning routine, breakfast, lunch, dinner, commute home | none |
| Banana (yellow) | `5` | kids and family: daycare drop-off and pick-up, the commute with the kid, bedtime, family time | none |
| default blue | not set | everything else: hobbies, Trello tasks, one-off meetings and trips | default, 30 minutes before |

The default 30-minute reminder is set in Google Calendar itself: Settings -> the calendar -> "Event notifications".

Uncolored routine (not tasks: don't create them in Trello, the routine doesn't move them): <"Guitar practice">.

## Standard week

- **Every weekday:** <06:50-07:50 Morning routine, 14:00-14:30 Lunch, 14:30-15:00 Guitar practice, 21:00-21:30 Dinner, 21:30-22:00 Family time>. Sleep <23:00-06:50> - every night from Sunday to the night from Friday to Saturday.
- **Mon** (<I drop off and pick up the kid>): <07:50-09:00 Daycare drop-off, 09:00-09:30 Breakfast, 09:30-14:00 Work, 15:00-17:30 Work, 17:30-19:30 Daycare pick-up, 22:00-23:00 Bedtime>.
- **Tue-Thu:** <07:50-08:20 Breakfast, 09:00-14:00 Work, 15:00-18:00 Work>.
- **Fri:** <07:50-08:50 Daycare drop-off, 08:50-09:20 Commute home, 09:20-10:00 Breakfast, 10:00-14:00 Work, 15:00-19:00 Work, 22:00-23:00 Bedtime>.
- **Sat, Sun:** <not planned>.

Free slots in the standard week (for Trello tasks): <Mon 19:30-21:00; Tue-Thu 08:20-09:00, 18:00-21:00, 22:00-23:00; Fri 19:00-21:00>.
