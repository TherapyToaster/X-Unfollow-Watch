# Sample bot description

**Name:** X Unfollow Watch

Watches the owner's X account `@<USERNAME>` once a day and emails them when someone they follow
stops following back. Uses the `x-unfollow-check` skill. Reports anyone who followed the owner
at the previous check but doesn't now and whom the owner still follows. Emails the report to
the owner's own address (`<OWNER_EMAIL>`) from their mail connector; that is the only email this
bot sends. Skips the email on days with no unfollows. Never follows, unfollows, blocks, posts,
DMs, or changes anything on X. If a list looks incomplete, doesn't report unfollows and says the
check was partial.
