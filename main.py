#!/usr/bin/env python

import io
import json
from pprint import pprint

import click

from monday_api import update_task_time
from wakatime_parser import wakafile_to_daysums


@click.command(no_args_is_help=True)
@click.argument('waka_csv', type=click.File('r'))
def parse_wakafile(waka_csv:io.TextIOWrapper):
    print(wakafile_to_daysums(waka_csv))

@click.command(no_args_is_help=True)
@click.argument('waka_csv', type=click.File('r'))
@click.argument('item_id', type=int)
@click.option('--board_id', type=int, help="The ID of the board to update", default=1883170887, show_default=True)
def update_task(waka_csv, item_id, board_id):
    # get the time per day from the waka CSV as a dict in the form {<datetime>: <timedelta>, ...}
    daysums = wakafile_to_daysums(waka_csv)
    pprint(daysums)
    
    # udate the specified task
    resp = update_task_time(board_id=board_id, item_id=item_id, time_per_day=daysums)
    
    # FIXME: currently monday's API doesn't allow you to update time-tracking columns
    # specifically, so the above will fail with the following error:
    # {
    #     "error_code": "ColumnValueException",
    #     "status_code": 200,
    #     "error_message": "This column type is not supported yet in the api",
    #     "error_data": {
    #         "column_type": "DurationColumn"
    #     }
    # }
    # related issues on monday's dev community board:
    # - https://community.monday.com/t/mutate-timetracking-info/18447/2
    # - https://community.monday.com/t/timetracking-substitute-columns/18614

    print("Response:")
    print(json.dumps(resp.json(), indent=4, default=str))

if __name__ == '__main__':
    update_task()
