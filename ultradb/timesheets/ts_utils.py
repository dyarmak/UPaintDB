from ultradb.models import Timesheet
from sqlalchemy import create_engine
import os
import pandas as pd
import datetime
from ultradb import db, create_app
from ultradb import mail
from flask_mail import Message


def send_payroll_email(user, subject, message):
    
    msg = Message(subject=subject, 
                  sender='ultrapaintdb@gmail.com', 
                  recipients=[user.email])
    msg.body = message
    mail.send(msg)


# Function to query + merge timesheet info before returning it
def get_timesheets(user=None, getLastYear=False):
    """
    If a user IS NOT supplied, it returns all users
    If a user IS supplied, it filters to just that users data 
    
    When called from admin panel (for payroll), no user will be supplied 
    """
    # Set up connection
    postgres_connection_URL = os.environ.get('DATABASE_URL')
    engine = create_engine(postgres_connection_URL)
    # Run the queries
    users = pd.read_sql(
        'SELECT id as user_id, username FROM "user"', con=engine)
    
    # Need to use the current year going forward
    currentYear = "SELECT * FROM Timesheet WHERE EXTRACT(YEAR FROM date_of_work) =  EXTRACT(YEAR FROM now())"
    # For testing I need to use last years data
    lastYear = "SELECT * FROM Timesheet WHERE EXTRACT(YEAR FROM date_of_work) =  (EXTRACT(YEAR FROM now())-1)"
    
    if user:
        user_id = user.id
        currentYear += " AND user_id=" + str(user_id)
        lastYear += " AND user_id=" + str(user_id)
    if getLastYear:
        timesheets = pd.read_sql_query(lastYear, con=engine)
    else:
        timesheets = pd.read_sql_query(currentYear, con=engine)
    
    projects = pd.read_sql(
        'SELECT id as project_id, name as project_name, site_id FROM project', con=engine)
    sites = pd.read_sql(
        'SELECT id as site_id, code as site_code FROM site', con=engine)
    # merge user with timesheet
    tss = pd.merge(timesheets, users, on='user_id')
    tss = pd.merge(tss, projects, on="project_id")
    tss = pd.merge(tss, sites, on="site_id")
    # drop un-needed id columns
    tss = tss.drop(["user_id", "date_submit", "project_id",
                    "completed", "site_id"], axis=1)
    tss.date_of_work = tss.date_of_work.astype('datetime64')
    tss['workWeek'] = tss.date_of_work.dt.strftime("%V")
    tss.workWeek = tss.workWeek.astype(int)

    return tss



def timesheet_entry_to_string(df, ts_id):
    """This function will take a timesheet DF and the id value and output a string of the following format:
    {date_of_work}: {hours} hours @ {site_code} {project_name}. {comment}
    EX:
    Mon Sep 7, 2020: 10 hours @ KGH CCSI Office. prep
    """
    # String to be returned
    entry = ""
    # Grab the DF row
    dfRow = df.loc[df.id == ts_id]
    # Entry starts with date_of_work
    entry += dfRow.date_of_work.dt.strftime("%a %b %d, %Y").values[0]
    entry += ": "
    # hours
    entry += str(dfRow.hours.values[0]) + " hours @ "
    # site_code
    entry += dfRow.site_code.values[0] + " "
    # project_name
    entry += dfRow.project_name.values[0] + ". "
    # comment
    entry += str(dfRow.comment.values[0])

    return entry


def timesheet_to_email(tsdf, weeksBack=0):
    """
    Input: DataFrame of ALL Timesheets, int of how many weeks back we want to do
    Output: subjectline, msg body 
    """
    # Declare our ouput vars
    subject = ""
    msg = ""

    # Most recent weeknumber
    mostRecentWeek = tsdf.workWeek.max()
    df = tsdf.loc[tsdf.workWeek == (mostRecentWeek-weeksBack)]

    # list of usernames
    usernames = df.username.unique().tolist()
    # Create empty dict
    dfDict = {}
    # key = username, values = DF of tss
    # Sort so most recent is shown first
    for user in usernames:
        dfDict[user] = df.loc[df['username'] == user].sort_values(
            'date_of_work', ascending=True)

    # calc weekEnded
    # Get the max date_of_work
    for user in dfDict.keys():
        if len(dfDict[user]) > 0:
            lastDate = dfDict[user].date_of_work.max()
            weekEnded = (lastDate + datetime.timedelta(days=(5 -
                                                     lastDate.weekday()))).strftime("%a %b %d, %Y")
            subject = "Hours for the week ended " + weekEnded
            msg = "Details of Hours Worked for week ended " + weekEnded + "\n"
        else:
            lastDate = datetime.date.today()
            weekEnded = (lastDate + datetime.timedelta(days=(5 -
                                                     lastDate.weekday()))).strftime("%a %b %d, %Y")
            subject = "Hours for the week ended " + weekEnded
            msg = "Details of Hours Worked for week ended " + weekEnded + "\n"

    # create a blank dict to store the weeks timesheet entries. 
    # Will use username as the key
    user_entries = {}
    # Iterate over the users
    for user in dfDict.keys():
        # refresh list of entries for each user
        entries = []
        # Check that a user has timesheet entries
        if len(dfDict[user]) > 0:
            #
            for ts_id in dfDict[user].id.unique():
                entries.append(timesheet_entry_to_string(dfDict[user], ts_id))
            user_entries[user] = entries

    # Now we build the msg body
    for user in user_entries.keys():
        msg += "\n"
        msg += str(user) + ":"
        msg += "\n"
        for entry in user_entries[user]:
            msg += str(entry)
            msg += "\n"

    message = msg.split("\n")

    msg += "\n\n\n\nThis payroll report was automatically produced by UPaintDB"
    
    # If there is no entry, we want to return that there is no Timesheets for this period.
    if len(tsdf) == 0:
        msg = f"You have no timesheet entries for this timeframe.\nCheck that you have entered your time."    


    return subject, message, msg


def timesheet_to_email_summarized(tsdf, weeksBack=0):
    """
    Input: DataFrame of Timesheets, int of weeks back
    Output: # of hours to be paid for each employee
    """
    # Define ouput vars
    subject = ""
    msg = ""
    # Get INT of the most recent workWeek number
    mostRecentWeek = tsdf.workWeek.max()
    # weeksBack defaults to 0
    if weeksBack != 0:
        df = tsdf.loc[tsdf.workWeek == (mostRecentWeek-weeksBack)]
    else:
        df = tsdf.loc[tsdf.workWeek == mostRecentWeek]

    # Create empty dict to store the DataFrames, grouped by username
    dfDict = {}
    # key = username, values = DF of tss
    # Sort so most recent is shown first
    for user in df.username.unique().tolist():
        dfDict[user] = df.loc[df['username'] == user].sort_values(
            'date_of_work', ascending=True)

    # calc weekEnded
    # Get the max date_of_work
    for user in dfDict.keys():
        if len(dfDict[user]) > 0:
            lastDate = dfDict[user].date_of_work.max()
            weekEnded = (lastDate + datetime.timedelta(days=(5 -
                                                             lastDate.weekday()))).strftime("%a %b %d, %Y")
            subject = "Summary of hours for the week ended " + weekEnded
            msg = "Summary of hours worked for week ended " + weekEnded + "\n"
        else:
            lastDate = datetime.date.today()
            weekEnded = (lastDate + datetime.timedelta(days=(5 -
                                                             lastDate.weekday()))).strftime("%a %b %d, %Y")
            subject = "Summary of hours for the week ended " + weekEnded
            msg = "Summary of hours worked for week ended " + weekEnded + "\n"

    # blank dict to store the sum of the weeks timesheet entries.
    # key = username, value = df.hours.sum()
    hours_summary = {}
    # Iterate over the users
    for user in dfDict.keys():
        # Check that a user has timesheet entries
        if len(dfDict[user]) > 0:
            hours_summary[user] = dfDict[user].hours.sum()

    for user in hours_summary.keys():
        msg += "\n" + str(user) + ": "
        msg += str(hours_summary[user]) + " hours\n"

    message = msg.split("\n")

    msg += "\n\n\n\nThis payroll report was automatically produced by UPaintDB"

    return subject, message, msg
