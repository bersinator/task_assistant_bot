# Trello board

Sample - lists and labels from the project author's board. Copy to `local/board.md` and replace everything in `<...>`; lists and labels can have your own names, only the roles matter. The agent takes ARIs from the Trello connector's responses (`trelloReadBoard`, `trelloReadList`).

Board **"<My tasks>"** (workspace "<...>"): https://trello.com/b/<shortLink>, ARI `ari:cloud:trello::board/workspace/<workspaceId>/<boardId>`.

## Lists

ARIs look like `ari:cloud:trello::list/workspace/<workspaceId>/<id>`. Roles are from `CLAUDE.md`, "Board".

| Role | List | What goes there | id |
|---|---|---|---|
| Inbox | Inbox | everything new, with no clear date or list | `<id>` |
| Today | Today | "today", "now"; 3 main tasks + small stuff | `<id>` |
| This week | This week | "this week", "before the weekend"; no more than ~15 cards | `<id>` |
| Project backlog | <Renovation> - backlog | a separate big project with its own backlog: renovating a house, a country house, a pet project you work on every evening. It has many tasks, hence its own list; **order = priority**, the top one is next | `<id>` |
| To buy | To buy | everything to buy (for the project or anything else) | `<id>` |
| Done | DONE | "done", "finished" | `<id>` |
| Notes | NOTES - IMPORTANT | notes, important things for later | `<id>` |
| Someday | BIG IDEAS / RESEARCH | big projects, ideas, "look into", "someday" (not about the backlog project) | `<id>` |

There can be several backlog projects (a list and a label for each) or none.

## Labels

ARIs look like `ari:cloud:trello::label/workspace/<workspaceId>/<id>`. Labels can only be created by hand in Trello: the connector can't. Rooms, stages and the like don't need labels - put them in the card title.

| Label | When | id |
|---|---|---|
| <RENOVATION> | everything about the backlog project | `<id>` |
| URGENT | really on fire (the urgent label) | `<id>` |
| FINANCE | money | `<id>` |
| WORK | work | `<id>` |
| FAMILY | tasks with the kids and family | `<id>` |
| MUSIC | a hobby | `<id>` |
