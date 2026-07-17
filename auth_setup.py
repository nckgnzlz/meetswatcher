"""One-time setup: log into your own Google account and save the session.

Run this once (and again whenever the session expires):

    python auth_setup.py

It opens a real browser window, lets you log into Google yourself, and then
saves the resulting session to auth.json so monitor.py can reuse it without
ever seeing your password.
"""

import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

AUTH_STATE_PATH = os.getenv("AUTH_STATE_PATH", "auth.json")


def main():
    print()
    print("=" * 70)
    print("  Google session setup")
    print("=" * 70)
    print()
    print("A browser window is about to open at accounts.google.com.")
    print()
    print("  1. Log into the Google account that HOSTS your meeting.")
    print("     (Use the normal login flow -- password, 2-step verification,")
    print("     whatever your account requires. This script never sees any")
    print("     of it; it only saves the logged-in session afterwards.)")
    print()
    print("  2. Wait until you're fully logged in and can see your account")
    print("     page or inbox.")
    print()
    print("  3. Come back to this terminal and press Enter.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://accounts.google.com")

        input("Press Enter here once you're fully logged in... ")

        context.storage_state(path=AUTH_STATE_PATH)
        browser.close()

    print()
    print(f"✅ Session saved to {AUTH_STATE_PATH}")
    print()
    print("Treat this file like a password -- anyone who has it can act as your")
    print("Google account. It's already in .gitignore, so it won't be committed.")
    print()
    print("Next step: fill in your .env (see .env.example) and run:")
    print()
    print("    python monitor.py")
    print()


if __name__ == "__main__":
    main()
