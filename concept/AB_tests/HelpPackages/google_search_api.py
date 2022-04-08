import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from datetime import date, timedelta
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from collections import defaultdict
from dateutil import relativedelta
import argparse
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import re
import os
from urllib.parse import urlparse
from time import sleep

site = 'https://hauswasserpumpe.info'  # Property to extract
num_days = 365


# Get Domain Name to Create a Project
def get_domain_name(start_url):
    domain_name = '{uri.netloc}'.format(uri=urlparse(start_url))  # Get Domain Name To Name Project
    domain_name = domain_name.replace('.', '_')
    return domain_name


# Create a project Directory for this website
def create_project(directory):
    if not os.path.exists(directory):
        print('Create project: ' + directory)
        os.makedirs(directory)


def authorize_creds(creds):
    # Variable parameter that controls the set of resources that the access token permits.
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

    # Path to client_secrets.json file
    CLIENT_SECRETS_PATH = creds

    # Create a parser to be able to open browser for Authorization
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials and authorize HTTP
    # If they exist, get them from the storage object
    # credentials will get written back to a file.
    storage = file.Storage('authorizedcreds.dat')
    credentials = storage.get()

    # If authenticated credentials don't exist, open Browser to authenticate
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())
    webmasters_service = build('searchconsole', 'v1', http=http)
    return webmasters_service


# Create Function to execute your API Request
def execute_request(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()


# Create function to write to CSV
def write_to_csv(data, filename):
    if not os.path.isfile(filename):
        data.to_csv(filename)
    else:  # else it exists so append without writing the header
        data.to_csv(filename, mode='a', header=False)


# Read CSV if it exists to find dates that have already been processed.
def get_dates_from_csv(path):
    if os.path.isfile(path):
        data = pd.read_csv(path)
        data = pd.Series(data['date'].unique())
        return data
    else:
        pass


def get_graphic_from_data(data):
    data = [data['clicks'], data['date']]
    filter_data = {}
    dates = []

    for date_and_clicks_index in range(len(data[1])):
        if data[1][date_and_clicks_index] not in dates:
            dates.append(data[1][date_and_clicks_index])
            filter_data[str(data[1][date_and_clicks_index])] = data[0][date_and_clicks_index]

    axys_x = ()
    axys_y = ()
    for date in dates:
        if axys_x:
            axys_x += (axys_x[-1] + 1,)
        else:
            axys_x = (0,)
        axys_y += (filter_data[date],)
        print(f'date = {date} | axys_y = {axys_y}')

    print(f'axys_x = {axys_x}')
    print(f'axys_y = {axys_y}')
    plt.plot(axys_x, axys_y)
    return plt


# Create function to extract all the data
def extract_data(site, num_days):
    creds = 'AB_tests/HelpPackages/client_secrets.json'

    webmasters_service = authorize_creds(creds)

    # Set up Dates
    end_date = datetime.date.today() - relativedelta.relativedelta(days=3)
    start_date = end_date - relativedelta.relativedelta(days=num_days)
    scDict = defaultdict(list)

    maxRows = 25000  # Maximum 25K per call
    numRows = 0  # Start at Row Zero
    status = ''  # Initialize status of extraction

    while (status != 'Finished'):  # Test with i < 10 just to see how long the task will take to process.
        request = {
            'startDate': datetime.datetime.strftime(start_date, '%Y-%m-%d'),
            'endDate': datetime.datetime.strftime(end_date, '%Y-%m-%d'),
            'dimensions': ['date', 'page'],
            'rowLimit': maxRows,
            'startRow': numRows,
        }

        response = execute_request(webmasters_service, site, request)

        try:
            # Process the response
            for row in response['rows']:
                scDict['date'].append(row['keys'][0] or 0)
                scDict['clicks'].append(row['clicks'] or 0)
                scDict['ctr'].append(row['ctr'] or 0)
                scDict['impressions'].append(row['impressions'] or 0)
                scDict['position'].append(row['position'] or 0)
            print('successful at %i' % numRows)

        except:
            print('error occurred at %i' % numRows)

        # Add response to dataframe
        df = pd.DataFrame(data=scDict)
        df['clicks'] = df['clicks'].astype('int')
        df['ctr'] = df['ctr'] * 100
        df['impressions'] = df['impressions'].astype('int')
        df['position'] = df['position'].round(2)

        print('Numrows at the start of loop: %i' % numRows)
        try:
            numRows = numRows + len(response['rows'])
        except:
            status = 'Finished'
        print('Numrows at the end of loop: %i' % numRows)
        if numRows % maxRows != 0:
            status = 'Finished'
    write_to_csv(df)
    return df


def get_clicks_from_date_to_date(site, page, start_date, end_date):
    creds = 'AB_tests/HelpPackages/client_secrets.json'

    webmasters_service = authorize_creds(creds)

    scDict = defaultdict(list)

    maxRows = 25000  # Maximum 25K per call
    numRows = 0  # Start at Row Zero
    status = ''  # Initialize status of extraction

    while (status != 'Finished'):  # Test with i < 10 just to see how long the task will take to process.
        request = {
            'startDate': datetime.datetime.strftime(start_date, '%Y-%m-%d'),
            'endDate': datetime.datetime.strftime(end_date, '%Y-%m-%d'),
            'dimensions': ["date", "page"],
            'rowLimit': maxRows,
            'startRow': numRows,
        }

        response = execute_request(webmasters_service, site, request)

        try:
            # Process the response
            for row in response['rows']:
                scDict['date'].append(row['keys'][0] or 0)
                scDict['page'].append(row['keys'][1] or 0)
                scDict['clicks'].append(row['clicks'] or 0)
                scDict['ctr'].append(row['ctr'] or 0)
                scDict['impressions'].append(row['impressions'] or 0)
                scDict['position'].append(row['position'] or 0)
            print('successful at %i' % numRows)

        except:
            print('error occurred at %i' % numRows)

        # Add response to dataframe
        df = pd.DataFrame(data=scDict)
        if df.empty:
            return None
        df['clicks'] = df['clicks'].astype('int')
        df['ctr'] = df['ctr'] * 100
        df['impressions'] = df['impressions'].astype('int')
        df['position'] = df['position'].round(2)

        print('Numrows at the start of loop: %i' % numRows)
        try:
            numRows = numRows + len(response['rows'])
        except:
            status = 'Finished'
        print('Numrows at the end of loop: %i' % numRows)
        if numRows % maxRows != 0:
            status = 'Finished'

    clicks = 0
    index = 0
    for page_from_df in df['page']:
        if page_from_df == page:
            clicks += df['clicks'][index]
        index += 1
    return clicks


# Read CSV if it exists to find dates that have already been processed.
def get_graphic_from_csv(path):
    if os.path.isfile(path):
        data = pd.read_csv(path)
        data = [data['clicks'], data['date']]
        filter_data = {}
        dates = []

        for date_and_clicks_index in range(len(data[1])):
            if data[1][date_and_clicks_index] not in dates:
                dates.append(data[1][date_and_clicks_index])
                filter_data[str(data[1][date_and_clicks_index])] = data[0][date_and_clicks_index]


        axys_x = ()
        axys_y = ()
        for date in dates:
            if axys_x:
                axys_x += (axys_x[-1] + 1,)
            else:
                axys_x = (0,)
            axys_y += (filter_data[date],)
            print(f'date = {date} | axys_y = {axys_y}')

        print(f'axys_x = {axys_x}')
        print(f'axys_y = {axys_y}')
        plt.plot(axys_x, axys_y)
        return plt
    else:
        return None
