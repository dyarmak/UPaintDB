import datetime
import psycopg2
import os
import pandas as pd
import numpy as np
from jinjasql import JinjaSql
from sqlalchemy import create_engine
nan = np.nan


def build_upcomingDF(site_id):
    """
    Create a Pandas DataFrame of the upcoming rooms within the select site_id
    """

    postgres_connection_URL = os.environ.get('DATABASE_URL')
    engine = create_engine(postgres_connection_URL)
    
    template = """SELECT *
    FROM room
    WHERE site_id = {{site_id}}
    """
    data = {
    "site_id": site_id
    }
    j = JinjaSql()
    query, bind_params = j.prepare_query(template, data)

    rooms = pd.read_sql(sql=query, con=engine, params=bind_params)

    # drop any rooms that have never been painted
    rooms = rooms.loc[~rooms.date_last_paint.isna()]

    # Convert to datetime
    rooms.date_last_paint = pd.to_datetime(rooms.date_last_paint)
    rooms.date_next_paint = pd.to_datetime(rooms.date_next_paint)

    today = datetime.date.today()
    for row in rooms.index:
        try:
            date_diff = rooms.loc[row, 'date_next_paint'].date() - today
            years_till_paint = round(date_diff.days/365, 1)
        except TypeError:
            years_till_paint = nan
        if rooms.loc[row, 'freq'] == -1:
            rooms.loc[row, 'due_in_X_years'] = nan
        else:
            rooms.loc[row, 'due_in_X_years'] = years_till_paint

    rooms = rooms.loc[rooms.due_in_X_years <=1].copy()

    rooms.sort_values('date_next_paint', inplace=True)

    rooms = rooms[['bm_id', 'name', 'date_last_paint', 'freq', 'date_next_paint', 'due_in_X_years']].copy()

    rooms.rename({'bm_id':'BM ID', 'name':'Room Name', 'date_last_paint':'Date of last Painting', 'freq':'Frequency', 'date_next_paint':'Next Painting', 'due_in_X_years':'Years till due'}, axis=1, inplace=True)

    rooms.reset_index(drop=True, inplace=True)

    return rooms


def build_asneededDF(site_id, area_id=None):
    """
    Create a Pandas DataFrame of the as needed rooms within the select site_id
    """

    postgres_connection_URL = os.environ.get('DATABASE_URL')
    engine = create_engine(postgres_connection_URL)
    
    # Potentially add an area filter as well?
    # if area_id:
    #     template with area_id
    # else
    #     template

    template = """SELECT *
    FROM room
    WHERE site_id = {{site_id}}
    AND freq = -1"""
    
    data = {
    "site_id": site_id
    }

    j = JinjaSql()
    query, bind_params = j.prepare_query(template, data)
    
    # Make DF of just as needed rooms for selected site.
    as_neededDF = pd.read_sql(sql=query, con=engine, params=bind_params)
    as_neededDF = as_neededDF[['bm_id', 'name', 'date_last_paint']].copy()

    # split dated from non-dated
    no_dateDF = as_neededDF.loc[as_neededDF.date_last_paint.isna()].copy()
    datedDF = as_neededDF.loc[~as_neededDF.date_last_paint.isna()].copy()

    # Set to datetime, and drop the time part.
    datedDF.date_last_paint = datedDF.date_last_paint.astype('datetime64[ns]')
    datedDF.date_last_paint = datedDF.date_last_paint.dt.strftime('%Y-%m-%d')

    # Sort them by date and bm_id
    no_dateDF.sort_values(['bm_id'],inplace=True)
    datedDF.sort_values(['date_last_paint','bm_id'],ascending=True, inplace=True)

    sortedDF = no_dateDF.append(datedDF)
    sortedDF.rename({'bm_id':'BM ID', 'name':'Room Name', 'date_last_paint':'Date of last Painting'}, axis=1, inplace=True)
    # sortedDF.set_index('BM ID', inplace=True)
    sortedDF.reset_index(drop=True, inplace=True)

    return sortedDF