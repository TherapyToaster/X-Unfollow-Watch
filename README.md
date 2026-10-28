# X Unfollow Watch

A small, read-only tool (and Grok Bot assistant setup) that checks once a day which
X accounts you follow have stopped following you back, and optionally emails you the list.

It never follows, unfollows, blocks, posts, or DMs anything.

## How it works

1. Looks up your account with the official **X API v2** using an app Bearer Token.
2. Fetches your full `followers` and `following` lists (paginated, 1000 per page, with rate-limit retries).
3. Skips the run if either list is more than ~3% short of your profile counts (a partial fetch shouldn't create false alarms).
4. Computes "accounts I follow that don't follow me" and diffs it against the previous run saved in a state JSON file.
5. Prints any **new** non-followers (handle, display name, profile link) and, with `--email`, sends them via SMTP. Nothing is sent when there's nothing new.

The first run only saves a baseline.

## Setup

Requires Python 3.8+ and no third-party packages. You need an X developer app with
API access that covers the followers/following endpoints (these may require a paid tier).

```bash
cp .env.example .env    # fill in your values
set -a; . ./.env; set +a
python3 unfollow_watch.py yourhandle               # print only
python3 unfollow_watch.py yourhandle --email       # print and email
python3 unfollow_watch.py yourhandle --state ~/.x-unfollow-state.json
```

### Run it daily (cron)

```cron
0 8 * * * cd /path/to/repo && set -a && . ./.env && python3 unfollow_watch.py yourhandle --email
```

## Environment variables

| Variable | Purpose |
|---|---|
| `X_BEARER_TOKEN` | X API v2 app Bearer Token (required) |
| `SMTP_HOST`, `SMTP_PORT` | SMTP server (587 = STARTTLS, 465 = SSL) |
| `SMTP_USER`, `SMTP_PASSWORD` | SMTP login (use an app password) |
| `EMAIL_FROM`, `EMAIL_TO` | Sender and recipient |

The state file and `.env` are git-ignored; they contain your follower data and secrets.

## Grok Bot

`grok-bot/` holds the assistant instructions (`SKILL.md`) and a sample bot description
(`profile.md`) for running the same check as a Grok Bot assistant that emails you daily.

## License

MIT, see [LICENSE](LICENSE).
