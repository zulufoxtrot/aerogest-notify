# Aerogest-notify

## Get schedule change notifications for Aerogest.

Aerogest is an instructor/aircraft reservation tool for flight schools. The current version does not support email notifications when a reservation is modified or cancelled. This is particularly useful for schools with a small fleet and a tight schedule.

This is a small script that takes advantage of Aerogest's undocumented API to check for changes in the reservations.

If a change is detected, the script uses the Pushbullet API to notify the user. Pushbullet is an easy way to pass messages programmatically.

## Installing

This setup uses pipenv.

```
pipenv install
```

## Configuring

Edit the global variables (username, password, instructor ID) directly in the source.

## Running

```
pipenv run python main.py
```