import csv
from datetime import timedelta, datetime
from io import StringIO, TextIOWrapper
import pandas as pd

def wakafile_to_csv(fp:TextIOWrapper):
    """
    Takes a file pointer to a wakafile pseudo-CSV, returns a StringIO containing a properly-formatted CSV.

    Specifically, wakatime includes two spurious lines before the header and excludes the 'resource'
    and 'total' columns in the header. This method removes those two lines and fixes the header.
    """
    # skip the first two lines; the first is metadata about the export, the second is blank
    wakalines = fp.readlines()[2:]
    # rewrite the header to add a label for the first and last columns
    wakalines[0] = "resource%s,total" % wakalines[0].strip()
    return StringIO("\n".join(x for x in wakalines if x.strip() != ''))

def wakafile_to_df(fp:TextIOWrapper):
    """
    Parses a wakatime CSV-esque export to a pandas dataframe, with the index being filenames and the columns being dates plus
    a final "total" column.

    Note that wakatime excludes the 'resource' and 'total' columns in the header, so they have to be added
    """

    return pd.read_csv(wakafile_to_csv(fp))

def wakafile_to_daysums(fp:TextIOWrapper, discard_empties=True):
    """
    Given a file pointer to a wakatime pseudo-CSV, return a dict of the following form:
    {<date>: <time in HH:MM>}.

    fp: the file pointer to read from
    discard_empties: if True, excludes dates from the resulting dict that have no time recorded
    """
    reader = csv.DictReader(wakafile_to_csv(fp))

    # the last line contains totals for each day, regardless of resource
    # split into total set, last
    *_, last = reader

    # create a dict of dates, total times
    # also parse the value into a python timedelta
    result = {
        datetime.strptime(k, '%Y-%m-%d'): timedelta(**dict(zip(('hours', 'minutes'), (int(x) for x in v.split(":")))))
        for k, v in last.items()
        if k not in ('resource', 'total')
    }

    return {k: v for k, v in result.items() if v > timedelta(0)} if discard_empties else result


def wakafile_df_to_daysums(df:pd.DataFrame, use_last_row_total=True):
    """
    Reference implementation for summing the hours per day for a dataframe
    derived from a wakatime CSV.

    (Note that this method isn't used; wakafile_to_daysums() does the same thing, but better.)
    """
    # remove resource, total columns
    df_datecells = df.iloc[:,1:-1]
    # add seconds to timedeltas (wakatime just reports HH:MM)
    df_datecells = df_datecells + ':00'

    if use_last_row_total:
        # extract the last row, which is apparently a total for each column
        date_totals = df_datecells.iloc[-1,:].apply(pd.to_timedelta)

        # for days where time was recorded, return only the HH:MM:SS section
        nonzero_dates = (
            date_totals[date_totals > pd.Timedelta(0)]
                .astype('str')
                .map(lambda x: x.split('days', maxsplit=1)[1].strip())
        )

        return nonzero_dates
    else:
        # sum columns over all rows except the last, since the last
        # row is a summary itself
        summed_dates_df = (
            df_datecells.iloc[:-1,:]
                .apply(pd.to_timedelta)
                .sum(axis=0)
        )

        return summed_dates_df[summed_dates_df > pd.Timedelta(0)]

