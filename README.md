# Phreak Archive

Phreak Archive is a small console app written in Python. It holds records about
telephone phreaking. Phreaking was the practice of using tones and tricks to
control the phone network. It was most common from the late 1960s to the 1980s.

This app is for Lab 2.

## A note before you start

This app has security flaws. They are there on purpose, for the lab. The code is
for learning here. It is not a pattern to reuse in other projects.

Run the app only on your own computer.

## What you need

- Python 3
- VSCode, or another editor with a terminal

The app uses only modules that come with Python. There is nothing to install
with pip.

## Start the app

1. Open the project folder in VSCode.
2. Open the integrated terminal.
3. Run this command:

```
python app.py
```

On macOS and Linux, the command is sometimes `python3` instead.

A short history message shows first. Then the main menu appears. The whole app
runs in the terminal. There is no browser page.

## Accounts

Each account has a handle and a password. A handle is the name a phreaker went
by.

- Handle `capn_static`, password `tone99`
- Handle `bluebox_88`, password `bell123`
- Handle `ringmaster`, password `pbx456`
- Handle `dial_ghost`, password `trunk77`

## Using the menus

Each menu is a numbered list. Type a number and press Enter.

The main menu has four choices:

1. Log in
2. Browse archive
3. My account
4. Exit

My account asks you to log in first.

To leave a sub-menu, choose Back. To close the app, choose Exit from the main
menu. Ctrl+C also stops it.

## The database

The app keeps its data in a file named `data.db`. The app makes this file the
first time it runs.

The file is made in whatever folder the terminal is in. Run the app from the
project folder. Then there is only one `data.db`.

Sometimes the data changes while you work. A reset brings back the starting
accounts and records.

To reset:

1. Exit the app.
2. Delete `data.db`.
3. Run the app again.

Exit first. On Windows, the file can stay locked while the app is open.

## Version control

The `.gitignore` file keeps `data.db` out of your repository. The lab
instructions in LEARN explain the git steps.

## If something goes wrong

**The terminal says `python` is not recognized, or command not found.** The
terminal cannot find Python. Try `python3`. If that does not work, check that
Python is installed.

**The terminal says it can't open file `app.py`.** The terminal is in a
different folder. Open the project folder in VSCode, then open a new terminal.

**The app says Invalid credentials.** Check the handle and password against the
list above. Every handle is lowercase.

Your instructor can help if the app still will not start.
