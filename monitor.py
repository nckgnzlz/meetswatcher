"""Watch a Google Meet waiting room and send a push notification (via ntfy.sh)
whenever guests are waiting to be admitted.

Configuration comes from environment variables (or a .env file) -- see
.env.example. Your Google session must first be saved with auth_setup.py.
"""

import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

MEET_URL = os.getenv("MEET_URL")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
AUTH_STATE_PATH = os.getenv("AUTH_STATE_PATH", "auth.json")
HEADLESS = os.getenv("HEADLESS", "true").strip().lower() not in ("false", "0", "no")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))

ADMIT_PATTERN = re.compile(r"Admit (\d+) guest")
JOIN_BUTTON_PATTERN = re.compile(r"Join now|Ask to join")


def die(message):
    print(f"\nError: {message}\n", file=sys.stderr)
    sys.exit(1)


def notify(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"), timeout=10)
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}", file=sys.stderr, flush=True)


def check_config():
    if not MEET_URL:
        die(
            "MEET_URL is not set.\n"
            "Copy .env.example to .env and set MEET_URL to your own Google Meet link."
        )
    if not NTFY_TOPIC:
        die(
            "NTFY_TOPIC is not set.\n"
            "Copy .env.example to .env and set NTFY_TOPIC to a private topic name of your choosing."
        )
    if not Path(AUTH_STATE_PATH).is_file():
        die(
            f"No saved Google session found at '{AUTH_STATE_PATH}'.\n"
            "Run 'python auth_setup.py' first -- it opens a browser so you can log into\n"
            "your own Google account and saves the session for this script to reuse."
        )


def session_expired():
    die(
        "Google asked for a login, which means your saved session has expired.\n"
        "Run 'python auth_setup.py' again to refresh it."
    )


def main():
    check_config()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
            ],
        )
        context = browser.new_context(
            storage_state=AUTH_STATE_PATH,
            permissions=["camera", "microphone"],
        )
        page = context.new_page()
        page.goto(MEET_URL)

        if "accounts.google.com" in page.url:
            session_expired()

        try:
            page.get_by_role("button", name=JOIN_BUTTON_PATTERN).first.click(timeout=45000)
        except Exception:
            die(
                "Couldn't find the 'Join now' / 'Ask to join' button within 45 seconds.\n"
                "Check that MEET_URL points at a valid meeting you host. (Meet's UI also\n"
                "changes occasionally, which can break the selectors this script relies on.)"
            )

        # The waiting-room "Admit" prompt appears in the People panel.
        try:
            page.get_by_role("button", name="People").click(timeout=15000)
        except Exception as e:
            print(f"Could not open People panel (continuing anyway): {e}", file=sys.stderr, flush=True)

        last_count = 0
        notify("Monitor started ✅")

        while True:
            if "accounts.google.com" in page.url:
                notify("🚨 Meet watcher signed out — the saved Google session has expired. Re-run auth_setup.py.")
                browser.close()
                session_expired()

            try:
                admit_button = page.locator("text=/Admit \\d+ guests?/").first
                if admit_button.is_visible():
                    match = ADMIT_PATTERN.search(admit_button.inner_text())
                    count = int(match.group(1)) if match else 1
                else:
                    count = 0
            except Exception:
                count = 0

            if count > last_count:
                notify(f"👋 {count} guest(s) waiting to join!")

            last_count = count
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
