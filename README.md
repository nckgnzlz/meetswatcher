# MeetsWatcher

MeetsWatcher sits in your Google Meet meeting, keeping an eye on the waiting room, and sends a notification to your phone the moment someone is waiting to be admitted. 

MeetsWatcher is useful for teachers or TAs hosting office hours, drop-in calls, or any "join whenever" meeting. 

This allows users to  be away from the computer during meetings until somebody actually shows up. Once uploaded to a virtual machine, there is no need to even turn on your computer; the session begins monitoring automatically based on your provided office hours. 

Notifications are administered through [ntfy.sh](https://ntfy.sh), a free push service that requires no accounts or API keys, just a topic name you create in the app.

Everything is bring-your-own: your Google account, your meeting link, your
notification topic, and (optionally) your server.

## Quick Start

1. Clone this repo and install dependencies:

   ```bash
   git clone https://github.com/nckgnzlz/meetswatcher.git
   cd meetswatcher
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
   - `MEET_URL` // this is your own Google Meet link (see **Google Meet setup** below
     for how to make one that stays permanent).
   - `NTFY_TOPIC` // a topic name you invent. Pick something long and
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
   away. To test functionality, open your Meet link from another browser or an incognito window
   and ask to join, within a few seconds you should get a "guest(s) waiting
   to join!" push.

   Tip: set `HEADLESS=false` in `.env` for this first run to
   run the progam on your device before uploading it to a virtual machine.

## Google Meet setup 

Read this before running the script. You must change a couple of Meet settings to make sure the link doesnt expire or kick out the monitor.

**Creating the Link** 

To create a link for this program, navigate to https://meet.google.com/landing and login. From here, click on "New Meeting" as shown below:
<p align="center">
<img width="702" height="292" alt="meet1" src="https://github.com/user-attachments/assets/ec8de7a2-ba26-4125-b105-2ef5758b11c3" />
</p>
CLick on "Create a meeting for later" to receive your indefinite meets link:
<p align="center">
<img width="246" height="138" alt="meet2" src="https://github.com/user-attachments/assets/289bce21-e963-4de8-91b2-5923919e8b7d" />
</p>
Copy the link provided and set `MEET_URL`. Make sure to jot down or bookmark the link for yourself to access when someone wants to join.
<p align="center">
<img width="337" height="198" alt="meet3" src="https://github.com/user-attachments/assets/fb109cff-dfc5-4776-91db-f145c8d36a2d" />
</p>

**Updating Access Type.**

Your default meet setting could be letting people in your organization (or invited guests) join instantly
without knocking rendering this tool useless. To ensure your meeting is correctly set, join your meeting and navigate to the padlock icon at the bottom of your meet:
<p align="center">
<img width="1007" height="66" alt="rules1" src="https://github.com/user-attachments/assets/36514de5-eb19-4888-b57f-a192bd501d7a" />
</p>
From here, scroll down and find "Meeting access type" and ensure your meeting is set to "Restricted"
<p align="center">
<img width="323" height="348" alt="rules2" src="https://github.com/user-attachments/assets/e550d657-c6c4-452e-9640-45e22e41b143" />
</p>

**Leaving After a Meet** 

When leaving a meet, make sure you leave using "Just leave the call" to ensure there is still a call for MeetWatcher to come back to. 
<p align="center">
<img width="376" height="155" alt="leave1" src="https://github.com/user-attachments/assets/ea1f9aa4-5a46-41eb-8426-97d0d23352ac" />
</p>

**Sessions can quietly expire.** Long-idle Google sessions occasionally hit
account inactivity or session timeouts that have nothing to do with Meet
itself. When that happens, the saved session in `auth.json` silently stops
working. If notifications stop arriving, the first thing to try is
regenerating the session:

```bash
python auth_setup.py
```

## Deploying to your own server

The monitor is happy to run on any Linux VPS, it just needs Python, a
Chromium it can drive, and network access. Nothing about it assumes a
particular hosting provider. MeetsWatcher was developed uising DigitalOcean, running on Ubuntu 24.04 (LTS) x64, with droplet specs: vCPU: 1, RAM: 2GB, Disk 50GB. These specifications are billed at about $12.00/mo and are subject to change.

1. **Generate `auth.json` locally first.** The auth setup opens a visible
   browser window for you to log into, which you can't through the VPS. Run `python auth_setup.py` on your own machine, then copy the
   resulting `auth.json` to the server (e.g. with `scp`). This file
   is the equivalent to being logged into your Google account so proceed with caution.

2. **Set up the project on the server:**

   ```bash
   git clone https://github.com/nckgnzlz/meetswatcher.git
   cd meetswatcher
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
   survives reboots and crashes, a systemd service, `tmux`, or whatever you
   prefer. If your meeting only happens during certain hours, systemd timers
   or cron entries that start and stop the service on your schedule work
   nicely and save resources the rest of the time.

## A note on Google's Terms of Service

This tool automates a real browser interacting with Google Meet. There is no
official Meet API for watching a waiting room. Automated access to Google
services falls under the general restrictions in Google's Terms of Service.
Nothing here does anything a signed-in human couldn't do by hand, but you're
the one signing in, so run it at your own discretion with respect to your own
Google account.

## Limitations

- The script finds the waiting room by looking for specific text and buttons
  in Meet's UI ("Join now", the People panel, "Admit N guests"). Google
  changes this UI from time to time, and when they do, the selectors here may
  need updating. If the monitor ceases to work, check for any UI changes.
- It watches one meeting per running instance.
- Saved Google sessions expire eventually; see **Sessions can quietly
  expire** above.

## License

MIT — see [LICENSE](LICENSE).
