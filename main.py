"""
Aerogest notification

Fetches JSON from the (undocumented) Aerogest API

Compares JSON data to find changes in the schedule for a given instructor ID.

Notifies user if a difference is found

"""

import requests
import time
import sys

from pushbullet import Pushbullet
import pushbullet.errors as PBerrors

from bs4 import BeautifulSoup

from jsondiff import diff

# set globals

# the email address used to log into aerogest
USERNAME = ''
# the aerogest password
PASSWORD = ''

# the ID of the instructor to check schedule for.
# note: you may also check schedules for individual users or aircraft. find the proper syntax in API.
INSTRUCTOR_ID = 2489  # zacharie clerc

# start date of the calendar. Aerogest's API will return the 16 days following this date.
DATE = "20190202"

INTERVAL = 300  # 300s = 5 mins

PUSHBULLET_API_KEY = ""

# only change this if the API changes
REQUEST_URL = "https://online.aerogest.fr/api/schedule/bookingapi/GetPlanningInstructor/" + str(
    INSTRUCTOR_ID) + "?d=" + DATE

previous_response = None

print("Initializing...")

# log into pushbullet
try:
    pb = Pushbullet(PUSHBULLET_API_KEY)
except PBerrors.InvalidKeyError:
    print("Invalid API key.")
    sys.exit()
except PBerrors.PushbulletError as e:
    print("Pushbullet error: " + str(e))
    sys.exit()

# log into Aerogest
with requests.Session() as session:
    login_url = 'https://online.aerogest.fr/Connection/logon'

    form_request = session.get(login_url)

    # get CSRF token from microsoft IIS
    soup = BeautifulSoup(form_request.text, 'html.parser')
    __RequestVerificationToken = soup.find('input', {'name': '__RequestVerificationToken'})['value']

    # submit form
    login_data = dict(__RequestVerificationToken=__RequestVerificationToken,
                      login=USERNAME,
                      password=PASSWORD,
                      # ReturnUrl='https://domain.com/',
                      rememberMe='false')

    page = session.post(login_url, data=login_data)

    print("Successfully logged in as " + USERNAME)

    # page = c.get('https://online.aerogest.fr/Schedule/planning/instructor/2489?d=20190202')
    # print(page.content)

    # once logged in, we enter a loop to check the JSON API periodically.
    while True:

        print("Checking now.")

        try:
            r = session.post(REQUEST_URL)
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            continue
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            continue
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print("Request error.")
            print(e)
            continue

        if not r:
            print("Empty response. This may mean your credentials are wrong. Check username/password.")
            continue

        if r.status_code != 200:
            print("Server returned an error. Error code: " + str(r.status_code))
            print(str(r.content))
            print("It is possible that the cookie is not valid anymore.")
            continue

        # TODO: catch exception if not json
        current_response = r.json()

        print(current_response)

        if current_response != previous_response and previous_response is not None:
            print("Found a difference in the schedule!")

            difference = diff(current_response, previous_response)
            print("Difference:")
            print(str(difference))

            push = pb.push_note("Aerogest schedule change", difference)

        else:
            print("No difference in schedule found.")

        previous_response = r.json()

        print("Will check again in " + str(INTERVAL) + " seconds.")
        time.sleep(INTERVAL)
