# Monday-Wakatime Importer

This tool is intended to help import timetracking data from [Wakatime](https://wakatime.com/)
into [Monday.com](https://monday.com/), specifically into the "time_tracking" column in a given
board.

## IMPORTANT: Currently Not Functioning

Currently monday's API doesn't allow you to update time-tracking columns
specifically, so the above will fail with the following error:

```json
{
    "error_code": "ColumnValueException",
    "status_code": 200,
    "error_message": "This column type is not supported yet in the api",
    "error_data": {
        "column_type": "DurationColumn"
    }
}
```

Related issues on monday's dev community board:
- https://community.monday.com/t/mutate-timetracking-info/18447/2
- https://community.monday.com/t/timetracking-substitute-columns/18614


## Initial Setup

You'll need a version of Python 3.x (I'm running 3.10), and likely virtualenv.
You should ideally create a virtualenv and populate it with the project dependencies, e.g.:

```
virtualenv .venv \
 && source .venv/bin/activate \
 && pip install -r requirements.txt
```

You can then run `main.py`, which will output help documentation if it's run without
arguments.

## Usage

Once you're ready to import a Wakatime CSV, go to the Wakatime dashboard, filter by
the full time interval that you want reported (greater than two weeks in the past requires
a paid account), then export the tracked time as a CSV.

In Monday.com, go to the board for which you want to track time, then click the row with
a time tracking column in it. Make note of the integer after `/boards/`, which will be
the board ID, and the integer after `/pulses/`, which will be the task ID of the task you
want to populate with time.

Run `main.py` with the following arguments:

```
./main.py --board_id <board ID> <path to wakatime CSV> <task ID>
```

After a bit of chewing, the API will throw an error about not being able to update
the time tracking column, as mentioned above. 🎉
