from datetime import timedelta, datetime
import os
from pprint import pprint
from dotenv import load_dotenv
import requests
import json

load_dotenv()

API_URL = os.getenv('MONDAY_API_URL', "https://api.monday.com/v2")
MONDAY_API_KEY = os.getenv('MONDAY_API_KEY')

# the time of day at which we start working (e.g., 8am)
DAY_START = timedelta(hours=8)

# monday.com API helpers

def do_query(query, extra_headers=None):
    headers = {"Authorization" : MONDAY_API_KEY}
    data = {'query' : query}
    return requests.post(url=API_URL, json=data, headers={
        **headers, **(extra_headers if extra_headers else {})
    })

def get_project_meta(board_id, item_id):
    resp = do_query("""
    query {
        me {
            id name
        }
        
        boards(ids:[%(board_id)d]) {
            name
            id

            items(ids:[%(item_id)d]) {
                name
                id
                creator {
                    id, name
                }
                
                group {
                    id
                }
                
                column_values(ids:["time_tracking"]) {
                    id
                    value
                    text
                }
            }
        }
    }
    """ % {'board_id': board_id, 'item_id': item_id})

    return resp.json()

def dt_to_monday_datestr(dt):
    return f"{datetime.utcnow().isoformat().split('.')[0]}Z"

def update_task_time(board_id, item_id, time_per_day, start_time=DAY_START, column_id='time_tracking', verbose=False):
    """
    Updates a given task's time_tracking column with the value 'time_per_day', which
    should be a dict in the format {<"YYYY-MM-DD">: <timedelta>, ...}.

    Since wakatime doesn't report time intervals worked, this method simply adds the day's
    worked time to the default start time for that date and reports that as the
    period worked. For example, if one worked for 6h30m on 2021-01-01, the reported
    interval would be 9am + 6h30m = 9:00am to 3:30pm.
    """

    utcnow_iso = f"{datetime.utcnow().isoformat().split('.')[0]}Z"
    start_date = min(x for x in time_per_day.keys())
    total_time = sum(time_per_day.values(), timedelta(0))

    # first, query for some metadata about us and the project
    meta = get_project_meta(board_id, item_id)

    if verbose:
        print("Got meta:")
        pprint(meta)
    
    timedata = {
        # 'duration': total_time.total_seconds(),
        'running': False,
        # 'startDate': start_date.timestamp(),
        'additional_value': [
            {
                'id': 158785194,
                'project_id': 1916012594,
                'account_id': meta['account_id'],
                'column_id': 'time_tracking',
                'created_at': utcnow_iso,
                'updated_at': utcnow_iso,
                'started_at': dt_to_monday_datestr(date + start_time),
                'ended_at': dt_to_monday_datestr(date + start_time + duration),
                'started_user_id': meta['data']['me']['id'],
                'ended_user_id': meta['data']['me']['id'],
                'manually_entered_end_date': True,
                'manually_entered_end_time': True,
                'manually_entered_start_date': True,
                'manually_entered_start_time': True,
                'status': 'active',
            }
            for date, duration in time_per_day.items()
        ],
    }

    payload = (
        """
        mutation {
            change_column_value (board_id: %d, item_id: %d, column_id: "%s", value: %s) {
                id
            }
        }
        """ % (board_id, item_id, column_id, json.dumps(json.dumps(timedata)))
    )

    if verbose:
        print("Payload:")
        print(payload)

    resp = do_query(payload)
    return resp
