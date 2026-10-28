#!/usr/bin/env python3
"""X Unfollow Watch: find accounts you follow that stopped following you back.

Read-only. Uses the official X API v2 with an app Bearer Token (X_BEARER_TOKEN).
"""
import argparse, datetime, json, os, smtplib, sys, time
import urllib.error, urllib.parse, urllib.request
from email.message import EmailMessage

API = "https://api.x.com/2"


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            if e.code == 429 and attempt < 4:
                reset = e.headers.get("x-rate-limit-reset")
                wait = max(5, int(reset) - int(time.time())) if reset else 60
                print(f"Rate limited; waiting {min(wait, 900)}s", file=sys.stderr)
                time.sleep(min(wait, 900))
                continue
            sys.exit(f"HTTP {e.code} on {url.split('?')[0]}: {body}")
    sys.exit("Too many retries")


def lookup_user(username, token):
    u = urllib.parse.quote(username.lstrip("@"))
    j = get(f"{API}/users/by/username/{u}?user.fields=public_metrics", token)
    if "data" not in j:
        sys.exit(f"User not found: {j}")
    return j["data"]


def fetch_list(uid, kind, token):
    out, page = {}, None
    while True:
        q = {"max_results": "1000", "user.fields": "username,name"}
        if page:
            q["pagination_token"] = page
        j = get(f"{API}/users/{uid}/{kind}?" + urllib.parse.urlencode(q), token)
        for u in j.get("data", []):
            out[u["id"]] = {"username": u["username"], "name": u["name"]}
        page = j.get("meta", {}).get("next_token")
        if not page:
            return out


def send_email(subject, body):
    host = os.environ.get("SMTP_HOST")
    if not host:
        sys.exit("SMTP_HOST not set; cannot email")
    port = int(os.environ.get("SMTP_PORT", "587"))
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("EMAIL_FROM") or os.environ.get("SMTP_USER")
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)
    if port == 465:
        s = smtplib.SMTP_SSL(host, port, timeout=60)
    else:
        s = smtplib.SMTP(host, port, timeout=60)
        s.starttls()
    with s:
        if os.environ.get("SMTP_USER"):
            s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
        s.send_message(msg)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("username", help="X username to watch (with or without @)")
    ap.add_argument("--state", default="state.json", help="state file path")
    ap.add_argument("--email", action="store_true", help="email new non-followers via SMTP")
    ap.add_argument("--tolerance", type=float, default=0.03,
                    help="max fraction a list may fall short of the profile count (default 0.03)")
    a = ap.parse_args()

    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        sys.exit("Set X_BEARER_TOKEN")

    user = lookup_user(a.username, token)
    m = user["public_metrics"]
    followers = fetch_list(user["id"], "followers", token)
    following = fetch_list(user["id"], "following", token)

    partial = (len(followers) < m["followers_count"] * (1 - a.tolerance) or
               len(following) < m["following_count"] * (1 - a.tolerance))
    if partial:
        sys.exit(f"Partial fetch (followers {len(followers)}/{m['followers_count']}, "
                 f"following {len(following)}/{m['following_count']}); state not updated.")

    prev = None
    if os.path.exists(a.state):
        with open(a.state) as f:
            prev = json.load(f)

    now_non = {i: u for i, u in following.items() if i not in followers}
    today = datetime.date.today().isoformat()

    if prev is None:
        print(f"Baseline saved: {len(followers)} followers, {len(following)} following, "
              f"{len(now_non)} not following back.")
        new = {}
    else:
        prev_non = set(prev.get("not_following_back", {}))
        new = {i: u for i, u in now_non.items() if i not in prev_non}

    with open(a.state, "w") as f:
        json.dump({"date": today, "user_id": user["id"], "followers": followers,
                   "following": following, "not_following_back": now_non}, f, indent=1)

    if prev is None:
        return
    if not new:
        print("No new non-followers.")
        return
    lines = [f"@{u['username']}  {u['name']}  https://x.com/{u['username']}"
             for u in sorted(new.values(), key=lambda u: u["username"].lower())]
    body = f"{len(new)} account(s) you follow stopped following back:\n\n" + "\n".join(lines) + "\n"
    print(body)
    if a.email:
        send_email(f"X unfollows for {today}", body)
        print("Email sent.")


if __name__ == "__main__":
    main()
