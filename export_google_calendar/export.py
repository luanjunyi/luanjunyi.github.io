from __future__ import print_function
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import dateutil.parser
import dateutil.tz
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar Export'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def parse_date(data):
    bjtz = dateutil.tz.gettz("Asia/Shanghai")
    local_tz_str = data.get("timeZone", "America/Los_Angeles")
    tz = dateutil.tz.gettz(local_tz_str)
    date_str = data.get('dateTime', data.get('date'))
    dt = dateutil.parser.parse(date_str).replace(tzinfo = tz)
    bj_dt = dt.astimezone(bjtz)
    return bj_dt

def parse_event(event):
    start = parse_date(event['start'])
    end = parse_date(event['end'])
    return {
        "start": start,
        "end": end
    }

def print_all(events):
    now = datetime.datetime.now().replace(tzinfo = dateutil.tz.gettz("America/Los_Angeles")).astimezone(dateutil.tz.gettz("Asia/Shanghai"))
    print("<h1>last updated at: %s</h1>" % now.strftime("%Y-%m-%d  %H:%M"))
    for event in events:
        print(event["start"].strftime("%b %d %H:%M:%S") + " - " + event["end"].strftime("%b %d %H:%M:%S"))
        print("<br />")

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    all_events = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        event = parse_event(event)
        all_events.append(event)

    print_all(all_events)

if __name__ == '__main__':
    main()
