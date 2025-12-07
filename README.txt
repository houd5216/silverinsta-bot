SilverInstaEye-like Telegram Bot - Package
-----------------------------------------
Files included:
  - bot_silverinsta.py    : The Telegram bot script (Python)
  - requirements.txt     : Python dependencies
  - run.sh               : Simple startup script
  - README.txt           : This file

Quick Termux setup (on your Android phone):
  1) Install Termux from F-Droid or your app store.
  2) Open Termux and run:
     pkg update -y && pkg upgrade -y
     pkg install python git -y
  3) Copy the ZIP to your phone and unzip, or clone the repo if hosted.
  4) In Termux: cd to the package folder
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
  5) Set your bot token:
     export BOT_TOKEN="your_bot_token_here"
     export ADMIN_IDS="12345678"   # optional: your Telegram user id
  6) Start the bot:
     bash run.sh

Notes:
  - The bot fetches only public information from Instagram pages.
  - If Instagram blocks scraping, results may fail. For larger scale use, consider using official APIs and proxies.
