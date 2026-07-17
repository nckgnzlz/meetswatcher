# Meet Watcher

Meet Watcher sits in your Google Meet meeting as you (using your own saved
Google session), keeps an eye on the waiting room, and sends a push
notification to your phone the moment someone is waiting to be admitted. It's
useful for office hours, drop-in calls, or any "join whenever" meeting where
you'd rather do something else until somebody actually shows up. Notifications
go through [ntfy.sh](https://ntfy.sh), a free push service — no accounts or
API keys needed, just a topic name you make up.

Everything is bring-your-own: your Google account, your meeting link, your
notification topic, and (optionally) your server. Nothing in this repo is tied
to anyone else's setup.

## Quick Start

1. Clone this repo and install dependencies:

   ```bash
   git clone <this-repo-url>
   cd meet-watcher
   python -m venv venv
   source venv/bin/activate        # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Copy the config template and fill in your own values:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   - `MEET_URL` — your own Google Meet link (see **Google Meet setup** below
     for how to make one that stays permanent).
   - `NTFY_TOPIC` — a topic name you invent. Pick something long and
     unguessable, because anyone who knows it can read your notifications.
     Then install the [ntfy app](https://ntfy.sh/) on your phone and subscribe
     to that same topic.

3. Save your Google session (opens a browser window; log in manually):

   ```bash
   python auth_setup.py
   ```

4. Run the monitor:

   ```bash
   python monitor.py
   ```

   You should get a "Monitor started ✅" notification on your phone right
   away. Then open your Meet link from another browser or an incognito window
   and ask to join — within a few seconds you should get a "guest(s) waiting
   to join!" push. That's the whole loop working.

   Tip: set `HEADLESS=false` in `.env` for this first run if you want to
   watch the browser do its thing.

## Google Meet setup

Read this before running the script — a couple of Meet settings determine
whether there's even a waiting room to watch.

**Use a recurring meeting so the link never changes.** Create a recurring
event in Google Calendar (e.g. weekly office hours) and let Calendar attach a
Meet link to it. That link stays the same for every occurrence, so you can set
`MEET_URL` once and forget it. If you instead start ad-hoc meetings from
meet.google.com, you get a new link every time.

**Turn Quick Access OFF for that meeting.** Quick Access is the Meet setting
that lets people in your organization (or invited guests) join instantly
without knocking. While it's on, there is no waiting room at all — so this
tool would never see anyone waiting. Turn it off either in the Calendar
event's host controls (the gear/settings icon on the Meet options) or from the
host controls panel inside the meeting itself.

**A quirk worth knowing:** if you end a recurring meeting with **"End the
call for everyone"** rather than just **"Leave the call"**, Meet turns Quick
Access off for all future occurrences too. That happens to be exactly the
effect you want here — but it's a side effect, so the reliable approach is
still to set Quick Access off directly in host controls.

**Sessions can quietly expire.** Long-idle Google sessions occasionally hit
account inactivity or session timeouts that have nothing to do with Meet
itself. When that happens, the saved session in `auth.json` silently stops
working. If notifications stop arriving, the first thing to try is
regenerating the session:

```bash
python auth_setup.py
```

## Deploying to your own server

The monitor is happy to run on any Linux VPS — it just needs Python, a
Chromium it can drive, and network access. Nothing about it assumes a
particular hosting provider.

1. **Generate `auth.json` locally first.** The auth setup opens a visible
   browser window for you to log into, which you can't do on a headless
   remote box. Run `python auth_setup.py` on your own machine, then copy the
   resulting `auth.json` to the server (e.g. with `scp`). Remember this file
   is equivalent to being logged into your Google account — transfer it only
   over secure channels and don't leave copies lying around.

2. **Set up the project on the server:**

   ```bash
   git clone <this-repo-url>
   cd meet-watcher
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   venv/bin/playwright install --with-deps chromium
   ```

   (`--with-deps` also installs the system libraries headless Chromium needs.)

3. **Add your `.env`** with your `MEET_URL` and `NTFY_TOPIC`, and copy in the
   `auth.json` from step 1. Keep `HEADLESS=true`.

4. **Run it:**

   ```bash
   venv/bin/python monitor.py
   ```

   For anything longer than a test, run it under a process manager so it
   survives reboots and crashes — a systemd service, `tmux`, or whatever you
   prefer. If your meeting only happens during certain hours, systemd timers
   or cron entries that start and stop the service on your schedule work
   nicely and save resources the rest of the time.

## A note on Google's Terms of Service

This tool automates a real browser interacting with Google Meet — there is no
official Meet API for watching a waiting room. Automated access to Google
services falls under the general restrictions in Google's Terms of Service.
Nothing here does anything a signed-in human couldn't do by hand, but you're
the one signing in, so run it at your own discretion with respect to your own
Google account.

## Limitations

- The script finds the waiting room by looking for specific text and buttons
  in Meet's UI ("Join now", the People panel, "Admit N guests"). Google
  changes this UI from time to time, and when they do, the selectors here may
  need updating. If the monitor stops working after a Meet redesign, that's
  the first place to look.
- It watches one meeting per running instance.
- Saved Google sessions expire eventually; see **Sessions can quietly
  expire** above.

## License

MIT — see [LICENSE](LICENSE).
