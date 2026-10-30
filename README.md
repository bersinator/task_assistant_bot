# task_assistant_bot - a personal task assistant on Claude Code

Tasks live in **Trello**, the schedule lives in **Google Calendar**, and the assistant is a **Claude Code** session that understands free-form speech: typed in Claude Code, or typed and spoken in **Telegram**. There is no server and no database of its own: Trello and Google keep the data, and the assistant's rules are markdown files in this repository.

The assistant answers in whatever language you set in your profile (it was built and used in Russian).

## What it does

- "Add a task: get my passport renewed, urgent, by Friday" -> a card in Inbox with the urgent label and a due date; the assistant names its number (#383).
- "What's on for today?" -> overdue items, today's tasks, suggestions from this week.
- "Let's plan the week" -> goes through Inbox card by card, shows the top of the backlogs, suggests what to take into this week (no more than ~15 cards).
- "Buy screws for the shelf" -> clarifying questions (size, which shops), options from the shops you named with a link and price - saved as comments on the card; later "give me the link for the screws" -> the saved link.
- "Done with the passport" -> the card moves to Done and is marked complete. "Delete ..." -> asks first -> archives.
- "Put a haircut on Thursday at 19:30" -> a calendar event and a Trello card linked to each other; if it overlaps work, the work block is shortened.
- "Lay out next week" -> your routine (work, sleep, meals, family) as one-off events from your standard week, free slots left for tasks.
- Every morning (optional) - a sync: today's calendar tasks -> into "Today"; tasks in "Today" without a time -> into a free calendar slot.
- The same in Telegram, plus voice messages: the bot replies "🎙 <what it heard>" and what it did.

## How it works

```
You --text--> [Claude Code in the project folder] --Trello connector----------> [Trello] <-- Trello app
                                                  --Google Calendar connector--> [Google Calendar]
Phone --Telegram--> [Telegram plugin server] -> [Claude Code in agent/] --connectors--> Trello, Calendar
                                                       +-- transcribe_audio (local Whisper, mcp_voice/)
```

| File | What's in it |
|---|---|
| `CLAUDE.md` | the assistant's rules: list roles, turning speech into card fields, weekly rhythm, task discussions, calendar |
| `local/` (not in git) | **yours**: profile and time zone, the board with list and label IDs, your weekly routine. Samples - `templates/local/` |
| `agent/` | the Telegram bot session: `CLAUDE.md` (what changes in Telegram), `.claude/settings.json` (strict permission list), `.mcp.json` (Telegram server and voice) |
| `mcp_voice/` | MCP server that transcribes voice messages (faster-whisper), tests - `tests/` |
| `routines/sync-calendar-trello.md` | instructions for the morning calendar/Trello sync |
| `scripts/setup.cmd`, `scripts/agent.cmd` | voice environment setup and bot launcher (Windows) |
| `docs/DESIGN.md` | why it is built this way: Telegram plugin, permissions, voice, connector limits |

## What you need

| What | Why | Required |
|---|---|---|
| A **Claude Pro or Max** subscription (personal) | Claude Code and connectors. Telegram Channels on Team/Enterprise only work if the org owner enables them | yes |
| A **Trello** account (free is enough) | tasks | yes |
| A **Google** account | schedule | for the calendar |
| The **Claude** desktop app (Code tab) or **Claude Code CLI** | the assistant itself; the morning routine needs the desktop app | yes |
| **Windows 10/11**, Git, Python 3.12+, Bun, Claude Code CLI, ~3 GB disk, 8+ GB RAM | Telegram bot and voice recognition | for the bot |
| A **Telegram** account | the bot | for the bot |

The parts are independent: you can stop at the assistant in Claude Code (parts 1-2) without the calendar or the bot.

## Security: what lives where

**The repository has no tokens or personal data and must never get any.** Everything secret lives outside the project folder or in the ignored `local/`:

| What | Where | In git |
|---|---|---|
| Trello and Google sign-in | connector OAuth on the claude.ai side | no, never in files |
| Telegram bot token | `%USERPROFILE%\.claude\channels\telegram\.env` | no, outside the project |
| Who may message the bot | `%USERPROFILE%\.claude\channels\telegram\access.json` | no, outside the project |
| Board, list and label IDs, names, routine | `local/*.md` | no, `local/` is in `.gitignore` |
| Voice messages and photos from Telegram | `%USERPROFILE%\.claude\channels\telegram\inbox\`, deleted after 7 days | no |

Rules for people and agents:
- never send the bot token in a chat - not to Claude, not to anyone: enter it only with the command from step 4.4;
- don't commit `local/` or remove it from `.gitignore`; check `git status` before pushing your fork;
- everyone on your Trello board sees all its cards, including the assistant's comments.

## Setup

Steps are marked **[you]** - needs a human (account sign-in, OAuth, tokens, confirmations) and **[agent]** - Claude can do it following "Instructions for an AI agent". The easiest path: do steps 1.1-1.3 by hand, then open the folder in Claude Code and say:

> Read README.md and set up the assistant.

### Part 1. The assistant in Claude Code

**1.1 [you] Clone the repository** (or fork it and clone your fork):

```bash
git clone https://github.com/bersinator/task_assistant_bot.git
```

**1.2 [you] Connect the connectors.** In the Claude app: "+" -> Connectors (or claude.ai -> Settings -> Connectors) -> **Trello** (by Atlassian) and **Google Calendar** -> Connect, sign in and grant access. Connectors belong to your Claude account, so they are then available both in the desktop app and in the CLI. You may need to restart the session afterwards.

**1.3 [you] Open the project folder in Claude Code**: in the Claude app - Code tab -> choose the folder; or in a terminal `cd task_assistant_bot` and `claude`. Check: asked "which Trello boards do I have?", the assistant lists your boards.

**1.4 [you + agent] The Trello board.** You need one board where the list is "when" and the label is "what about". Example - the lists of the author's board:

| List | Role |
|---|---|
| Inbox | everything new, no date |
| Today | 3 main tasks + small stuff |
| This week | no more than ~15 cards |
| Renovation - backlog | a separate big project with its own backlog: renovating a house, a country house, or a pet project you work on every evening. It has many tasks, so it gets its own list; order = priority |
| To buy | everything to buy |
| DONE | finished |
| NOTES - IMPORTANT | notes for the future |
| BIG IDEAS / RESEARCH | ideas, "look into", "someday" |

Labels, for example: RENOVATION (the backlog project), URGENT, FINANCE, WORK, FAMILY, MUSIC.

- You can use an existing board: the agent reads its lists and suggests which list plays which role.
- The agent creates missing lists itself (after you agree).
- **You create labels** in Trello (card -> Labels -> "Create a new label"): the connector can't.

**1.5 [agent] Fill in `local/`.** The agent asks you (name, language, time zone, who else is on the board, your vocabulary such as "renovation" = the backlog project), reads the board, list and label IDs through the connector and writes `local/profile.md` and `local/board.md` from the samples in `templates/local/`. By hand:

```bash
mkdir local && cp templates/local/*.md local/
```

then replace everything in `<...>`. The easiest way to get list and label IDs is to ask the assistant: "show the ARIs of my board's lists and labels".

**1.6 [you] Check:** "add a task to buy light bulbs by Friday" -> a card in "To buy" due Friday; "what's on for today?" -> a plan; "remove the light bulbs" -> asks first -> archives.

### Part 2. The calendar

Trello is the task database, Google Calendar is when things get done. Only things set for a specific time go into the calendar; your weekly routine lives only in the calendar.

**2.1 [you + agent] Routine.** The agent asks about your standard week (sleep, morning, meals, work, commute, kids, hobbies) and writes `local/schedule.md` from `templates/local/schedule.md`.

**2.2 Colors and reminders** (an assistant rule; change it if you like). Color marks the routine, blue marks tasks. **Reminders only on blue events - the default one, 30 minutes before**; colored events get no reminders, otherwise your phone rings all day. The author's scheme:

| Color | `colorId` | What | Reminder |
|---|---|---|---|
| Flamingo (pink) | `4` | work | none |
| Graphite (grey) | `8` | sleep, morning routine, breakfast, lunch, dinner, commute home | none |
| Banana (yellow) | `5` | kids and family: daycare drop-off and pick-up, bedtime, family time | none |
| default blue | not set | everything else: hobbies, Trello tasks, meetings, trips | 30 minutes before |

**2.3 [you] Default reminder** in Google Calendar: Settings -> your main calendar -> "Event notifications" -> "Notification, 30 minutes". The assistant keeps the default reminder on blue events, so the reminder time is set here.

**2.4 [you] Check:** "lay out next week" -> the agent shows the plan and, after you agree, creates one-off events; "put a haircut on Thursday at 19:30" -> a blue event linked to a new card.

### Part 3. Morning sync (optional)

Every morning a Claude app task reconciles the calendar and Trello following `routines/sync-calendar-trello.md`: today's calendar tasks -> their cards into "Today"; tasks in "Today" without an event -> into a free slot. It deletes nothing, and with a suspiciously large number of changes it does nothing and says so in the report.

**3.1 [you] Create the task** in the Claude desktop app: sidebar -> **Scheduled** -> new task:
- name: `sync-calendar-trello`;
- schedule: daily at 06:00 (cron `0 6 * * *`);
- folder: the project folder;
- permission mode: **Bypass permissions** (nobody is around; the routine only works with Trello and the calendar);
- prompt:

```
Read `routines/sync-calendar-trello.md` in the current folder and follow it completely. This is the morning Google Calendar and Trello sync; the user is not around, don't ask any questions.

If the file is missing or can't be read, change nothing in Trello or the calendar, and make your last message: "Sync not run: routines/sync-calendar-trello.md not found".
```

The task only says to read the file, so edits to `routines/sync-calendar-trello.md` apply from the next run. It runs while the Claude app is open; a missed run happens the next time the app opens. The schedule is stored in the app, so on another computer you have to create the task again.

**3.2 [you] Check:** run the task by hand ("Run now") and read the report.

### Part 4. The Telegram bot (Windows)

The bot is a separate Claude Code session in `agent/` with the Telegram channel. It answers while the `scripts\agent.cmd` window is open and the computer is awake.

**4.1 [you] Install the tools** (PowerShell):

```powershell
winget install Git.Git Python.Python.3.13
```

```powershell
irm https://claude.ai/install.ps1 | iex
```

```powershell
irm bun.sh/install.ps1 | iex
```

Claude Code goes to `%USERPROFILE%\.local\bin`, Bun to `%USERPROFILE%\.bun\bin`; `scripts\agent.cmd` adds both to `PATH` itself. Sign in to Claude Code with your personal account: run `claude` and complete the sign-in.

**4.2 [agent or you] Voice environment:**

```bat
scripts\setup.cmd
```

Creates `.venv` and installs `requirements.txt`. Check - `.venv\Scripts\python.exe -m pytest tests` (5 tests). The Whisper model `large-v3-turbo` (~1.6 GB) is downloaded to the Hugging Face cache the first time the bot starts. Settings are environment variables: `WHISPER_MODEL` (default `large-v3-turbo`; on a slow computer - `small`), `WHISPER_LANGUAGE` (language code such as `en` or `ru`; empty - detect automatically), `WHISPER_BEAM_SIZE` (`5`), `WHISPER_MODELS_DIR` (a folder with already downloaded models).

**4.3 [you] Install the Telegram plugin** - it's needed only for the cached `server.ts`, it must not be enabled (see `docs/DESIGN.md`, items 3-4):

1. In a terminal: `cd agent`, `claude`, then in the session `/plugin install telegram@claude-plugins-official`, scope **project**. Exit the session.
2. Turn the plugin back off: `git checkout -- agent/.claude/settings.json` (it must keep `"telegram@claude-plugins-official": false`). Make sure the plugin isn't enabled in `agent/.claude/settings.local.json` or globally in `%USERPROFILE%\.claude\settings.json`: otherwise every Claude session will steal the bot.
3. Check the version: `dir %USERPROFILE%\.claude\plugins\cache\claude-plugins-official\telegram`. If it's not `0.0.7`, replace the version in `agent/.mcp.json` and `scripts/agent.cmd` (the agent can do it).

**4.4 [you] Create the bot and save the token.** In Telegram, message [@BotFather](https://t.me/BotFather) `/newbot` and get a token. **Don't send the token to anyone, Claude included.** Save it to a file outside the project (PowerShell; you type the token in the terminal):

```powershell
$t = Read-Host "Bot token"; $d = "$env:USERPROFILE\.claude\channels\telegram"; New-Item -ItemType Directory -Force $d | Out-Null; Set-Content -Encoding ascii "$d\.env" "TELEGRAM_BOT_TOKEN=$t"; Remove-Variable t
```

**4.5 [you] First launch:** `scripts\agent.cmd` (double-click or from a terminal). The first time Claude asks you to trust the folder and possibly to allow importing `../local/*.md` - agree. To the "development channels" warning answer "1. I am using this for local development" - this happens on every launch. Keep the window open.

**4.6 [you + agent] Pair yourself with the bot.** Send the bot anything in Telegram - it replies with a 6-character code. In a **regular** Claude Code session in the project root (not in `agent/`!) say: "pair the bot, code abc123". The agent edits `access.json`: moves you into `allowFrom`, sets `dmPolicy: "allowlist"` (the bot ignores everyone else from now on) and `ackReaction: "👀"` (a reaction on every received message). The bot sends "Paired!".

**4.7 [you] Check:** type "what's on for today?", send a voice message "buy wood screws by Friday" -> "🎙 ...", a card in Trello.

Don't: start a second session in `agent/` or enable the Telegram plugin anywhere else - a second process steals the bot from the first one.

### macOS and Linux

Not tested. What to change: in `agent/.mcp.json` the Python path becomes `../.venv/bin/python` and the plugin path uses `${HOME}`; instead of `scripts/*.cmd` use shell scripts with the same commands (`python3 -m venv .venv`, `pip install -r requirements.txt`; `cd agent && claude --dangerously-load-development-channels server:telegram --permission-mode dontAsk`). Everything else is OS-independent.

## Instructions for an AI agent

This section is for Claude (or another agent) asked to "set up the assistant". Go in order, and at each step briefly tell the user what you're doing and what you need from them. Talk to the user in their language.

Hard rules:
- **Secrets:** never ask for tokens, passwords or OAuth codes in the chat; never read or show `~/.claude/channels/telegram/.env`. The user enters the bot token themselves with the command from step 4.4.
- **Personal data** (board, list and label IDs, names, time zone, routine) goes only into `local/`. Don't tailor `CLAUDE.md`, `routines/`, `templates/` or other tracked files to the user; don't commit `local/`.
- **Account sign-ins** (connector OAuth, Claude sign-in, BotFather) are done by the user only.
- Changes in Trello and the calendar only after the user agrees: show what you're about to create and wait for a "yes".

Steps:

1. **Check the connectors.** Are there `trello*` tools and Google Calendar tools (`list_events`, `create_event`)? If not, ask the user to do step 1.2 and restart the session; don't go on without Trello, and skip step 4 without the calendar.
2. **Profile.** Ask: how to address them, reply language, time zone (IANA, e.g. `Europe/Berlin`; suggest the one from `trelloReadMember` `get_me`, `prefs.timezone`), who else is on the board, special words (the backlog project, kids' names). Copy `templates/local/profile.md` to `local/profile.md` and fill it in, computing the UTC offset and "12:00 local" in UTC.
3. **Board.** Find the user's boards (`trelloReadMember`, `trelloReadWorkspace`, `trelloReadBoard`), ask which one to use, or suggest creating a new one in Trello by hand. Read the board's lists (`trelloReadList`) and labels, map lists to the roles in `CLAUDE.md` ("Board"), show the mapping and ask for confirmation. Offer to create missing lists (`trelloWriteList` `create`, positions in role order). Missing labels (urgent, project) are created by the user by hand - explain how and wait. Write `local/board.md` from `templates/local/board.md` with the board, list and label ARIs taken from the connector's responses.
4. **Calendar.** Ask about the standard week day by day (sleep, morning, meals, work, commute, kids, hobbies) and which colors to use (suggest the scheme from step 2.2). Write `local/schedule.md` from the sample and compute the free slots. Ask the user to set the default 30-minute reminder (step 2.3). Offer to lay out next week - only after they agree.
5. **Check the assistant.** Make sure no `<...>` placeholders are left in `local/`. Suggest the user runs the checks from steps 1.6 and 2.4. Archive test cards afterwards, asking first.
6. **Morning sync** - optional. If you have a tool for creating scheduled tasks (`create_scheduled_task`), offer to create the task with the settings from step 3.1; otherwise give the user those settings.
7. **Bot** - optional, Windows only. The user installs the tools (4.1), installs the plugin (4.3, item 1), gets and saves the token (4.4), launches the bot (4.5). You can: run `scripts\setup.cmd` and the tests (4.2); restore `agent/.claude/settings.json` and check the plugin isn't enabled anywhere (4.3, item 2); check the plugin version and fix `agent/.mcp.json` and `scripts/agent.cmd` (4.3, item 3); pair the user by code (4.6, procedure in `CLAUDE.md`, "Development"). If the connector tool names in the bot session aren't `mcp__claude_ai_Trello__*` / `mcp__claude_ai_Google_Calendar__*`, fix the `allow` list in `agent/.claude/settings.json`.
8. **Wrap-up.** List what's set up, what was skipped, and what the user must do themselves.

## Using it

Just talk: "add ...", "move ... to tomorrow", "done with ...", "what's on for today?", "let's plan the week", "let's discuss buying screws", "give me the link for ...", "put ... on Friday at 18:00", "take ... off the schedule".

- The list is "when", the label is "what about". "Today" -> Today, "this week" -> This week, no date -> Inbox, "someday" -> the project backlog or Big ideas.
- Priority is the order of cards in a list; "urgent" is a label.
- Rhythm: once a week spend ~15 minutes clearing Inbox and picking the week's tasks; in the morning - 3 main tasks for today.
- You can view and edit tasks in the Trello app: the assistant always reads the current state.

## Updating

```bash
git pull
```

`local/` isn't in git, so the rules (`CLAUDE.md`, the routine) get updated while your settings stay. If `templates/local/` gained new fields, ask the assistant to compare them with your `local/`.

## Troubleshooting

| Problem | What to do |
|---|---|
| The assistant says there are no Trello or calendar tools | connect the connector (step 1.2), restart the session |
| The assistant doesn't know your lists, asks to set up `local/` | step 1.5: "read README.md and set up the assistant" |
| Trello due dates shift by a day | wrong time zone or offset in `local/profile.md` |
| The bot is silent | is the `scripts\agent.cmd` window open, is the computer awake; is there a second session in `agent/` or the Telegram plugin enabled somewhere |
| `Telegram plugin 0.0.7 not found` at launch | a different plugin version - step 4.3, item 3 |
| Bun crashes: "Failed to start inspector ... port in use" | the `telegram` server in `agent/.mcp.json` must have `"BUN_INSPECT": ""` |
| The bot replies with a pairing code instead of doing things | not paired or pairing got reset - step 4.6 |
| Voice messages are slow to transcribe | set `WHISPER_MODEL=small` (or `medium`) in your user environment variables |
| The bot can't do something ("permission denied") | in dontAsk only what's in `allow` of `agent/.claude/settings.json` is permitted; Bash and file edits are blocked on purpose |

## License

MIT, see `LICENSE`.
