---
name: x-unfollow-check
description: >-
  Use this to snapshot an X account's followers and following through the X API
  and find accounts the owner follows that stopped following them back.
---
# X unfollow check

Read-only. Never follow, unfollow, block, post, DM, or change anything on X. The X connector
tools can't list followers or following, so this uses the official X API v2 with the owner's own
app Bearer Token, stored in the env var `X_BEARER_TOKEN`. Never print the token.

## Setup (once)
Copy `unfollow_watch.py` from this repo into the bot's persistent store and pick a state file
path inside that store (for example `<STORE>/state.json`).

## Each check
1. Back up the state file, then run:
   `python3 unfollow_watch.py <USERNAME> --state <STORE>/state.json`
2. Completeness: the script exits without updating state if either list is more than ~3% below
   the profile count. Tell the owner the check was partial and don't report unfollows.
3. The script compares by user id against the previous run and prints accounts the owner still
   follows that are newly not following back.
4. If there are any, send a short report email from the owner's mail connector to their own
   address, subject `X unfollows for <date>`, listing each `@handle`, display name, and
   `https://x.com/<handle>`. Send nothing on days with nothing new.
5. If the API fails (rejected token, no credits, rate limits), tell the owner what failed and stop.
