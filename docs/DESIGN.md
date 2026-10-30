# How it works and why

Technical decisions that aren't obvious from the code. Tested on Windows 11, Claude Code CLI 2.1.310, Telegram plugin 0.0.7, Bun 1.4.4 (October 2026).

## Overview

```
You --text--> [Claude Code session in the project folder] --Trello connector----------> [Trello] <-- Trello app and website
                                                          --Google Calendar connector--> [Google Calendar]

Phone --Telegram: text, voice--> [Telegram plugin server] -> [Claude Code session in agent/] --connectors--> Trello, Calendar
                                                                    |-- transcribe_audio (mcp_voice, local Whisper)
                                                                    +-- WebSearch / WebFetch

Claude app, daily on schedule -> [sync-calendar-trello task] -> routines/sync-calendar-trello.md
```

There is no server or database of its own: Trello keeps the tasks, Google Calendar keeps the schedule, and the assistant is the Claude Code session itself. State between sessions lives only in Trello, the calendar and card comments.

## Decisions

1. **The list is "when", the label is "what about".** One board, lists by timeframe (Inbox, Today, This week), big projects as a separate backlog list with a project label. Priority is the order within a list: free Trello has no custom fields.
2. **Personal data in `local/`, rules in `CLAUDE.md`.** `CLAUDE.md` imports `local/*.md` (`@local/board.md`), and the folder is in `.gitignore`. So `CLAUDE.md` and the routine can be updated from the public repository without touching your IDs and routine.
3. **No other Claude Code processes with the Telegram server.** On start the plugin server kills the previous poller via `bot.pid`: any second `claude` with the plugin enabled steals the bot from the main session. That's why the Telegram server is defined only in `agent/.mcp.json`, the plugin is disabled in `agent/` (`enabledPlugins: false`) and not enabled anywhere else.
4. **The Telegram server comes from `agent/.mcp.json`, not from the plugin.** In Claude Code 2.1.310 the plugin's server didn't start with `--channels plugin:telegram@...`: the plugin loaded, but no `bun` process appeared. The same `server.ts` from the plugin cache (`~/.claude/plugins/cache/claude-plugins-official/telegram/<version>`), defined in `.mcp.json`, starts right away. The channel is attached with `--dangerously-load-development-channels server:telegram`, and Claude asks for confirmation on every launch. If `--channels plugin:telegram@claude-plugins-official` works in your Claude Code version, you can switch back to it. After a plugin update, fix the version in `agent/.mcp.json` and `scripts\agent.cmd`.
5. **`BUN_INSPECT` is cleared** in `agent/.mcp.json`: the Claude CLI passed it to child processes and Bun crashed on start ("Failed to start inspector ... port in use").
6. **The bot's permissions are a strict list** (`agent/.claude/settings.json`): `--permission-mode dontAsk` in `scripts\agent.cmd` (the interactive session ignored `defaultMode` from settings); only the Trello and Google Calendar connectors, Telegram, `transcribe_audio`, `WebSearch`, `WebFetch` and `Read` of the inbox folder are allowed. **Bash, PowerShell, Write and Edit are explicitly denied**: the bot reads third-party shop pages, and without an explicit deny dontAsk still runs harmless read-only commands like `echo`. As a result the plugin's skills (`/telegram:access`) don't work in the bot - access is edited from a regular session in the project root.
7. **Voice is local.** `mcp_voice` is a small MCP server on faster-whisper (model `large-v3-turbo`, CPU, int8): it accepts only files from the plugin's inbox folder, loads the model at start and keeps it in memory, and deletes files older than 7 days (the plugin doesn't clean them up). Audio is decoded with PyAV: the built-in faster-whisper 1.2.1 decoder doesn't work with av 19. On an i5-11320H a 10-second voice message takes ~8 seconds.
8. **Delete = archive**, only after asking. The connector can't delete permanently anyway.
9. **All the assistant's actions in Trello are recorded as the user**, so the assistant's comments are tagged "[assistant]".
10. **The calendar is filled with one-off events** a week ahead, from the standard week in `local/schedule.md`. The routine is colored and has no reminders; tasks are blue with a 30-minute reminder.
11. **The routine is a Claude app task**, not `/loop` or `CronCreate`: those live only while a session is open and expire after 7 days. The task only says to read `routines/sync-calendar-trello.md`, so the instructions can be edited in git.

## Trello connector limits (October 2026)

- Can't create or rename labels; can't restore cards from the archive; can't permanently delete checklist items, checklists, comments or cards.
- Can't upload attachments (photos) - only lists them.
- Card `get` doesn't return checklists; they're read separately.
- Trello Planner (`trelloWritePlanner`) can't move events - use only Google Calendar for the schedule.

## Risks

- Telegram Channels is a research preview: flags and plugin behavior change between Claude Code versions.
- Subscription limits: heavy shop searching can hit the 5-hour limit and the bot goes silent. The bot's default model is Sonnet (`agent/.claude/settings.json`).
- The bot works only while the `scripts\agent.cmd` window is open and the computer is awake.
- Data lives in Atlassian's and Google's clouds; board members see all cards.
