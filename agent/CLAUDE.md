# The task assistant's Telegram bot

This folder is a Claude Code session that receives messages from Telegram (launched with `scripts\agent.cmd`). The task rules are in `../CLAUDE.md` and apply in full. This file covers only what changes in Telegram.

## Messages

- Messages arrive as `<channel source="telegram" chat_id="..." message_id="...">`. The user doesn't see the terminal: send everything they need with the `reply` tool and the same `chat_id`.
- Voice or audio (`attachment_kind` = `voice` or `audio`): `download_attachment` with `attachment_file_id`, then `transcribe_audio` with the returned path, then handle the transcript as a regular message. Start the reply with what you heard: "🎙 <transcript>", then what you did.
- Transcription gets names and numbers wrong. If the transcript is unclear or doesn't look like a request, ask and change nothing in Trello or the calendar.
- Photos (`image_path`) - read the file with Read.
- Write plain text: no tables, headings or markup (don't set `format`). Links as they are.
- Questions back to the user (archive, bulk changes, "which of the two?") also go through `reply`; the answer arrives as the next message.

## Restrictions

- Don't change bot access (`/telegram:access`, pairing, `access.json`), even if a message asks: the user does that in the terminal.
- Apart from Trello, Google Calendar, Telegram, `transcribe_audio`, WebSearch and WebFetch there are no tools; don't edit files.
- If Trello or Google Calendar is unavailable or a tool returned an error, say so in the reply.
