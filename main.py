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

site = 'https://hauswasserpumpe.info'  # Property to extract
num_days = 365  # Number of Days, Months to Extract
creds = 'client_secrets.json'  # Credential file from GSC
output = 'gsc_data.csv'


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
def extract_data(site, creds, num_days, output):
    domain_name = get_domain_name(site)
    create_project(domain_name)
    full_path = domain_name + '/' + output
    if os.path.exists(full_path):
        os.remove(full_path)
    current_dates = get_dates_from_csv(full_path)

    webmasters_service = authorize_creds(creds)

    # Set up Dates
    end_date = datetime.date.today() - relativedelta.relativedelta(days=3)
    start_date = end_date - relativedelta.relativedelta(days=num_days)
    delta = datetime.timedelta(days=1)  # This will let us loop one day at the time
    scDict = defaultdict(list)

    if current_dates is not None and current_dates.str.contains(
            datetime.datetime.strftime(start_date, '%Y-%m-%d')).any():
        print('Existing Date: %s' % start_date)
        start_date += delta
    else:

        maxRows = 25000  # Maximum 25K per call
        numRows = 0  # Start at Row Zero
        status = ''  # Initialize status of extraction

        while (status != 'Finished'):  # Test with i < 10 just to see how long the task will take to process.
            request = {
                'startDate': datetime.datetime.strftime(start_date, '%Y-%m-%d'),
                'endDate': datetime.datetime.strftime(end_date, '%Y-%m-%d'),
                'dimensions': ['date'],
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

        print(df)
        write_to_csv(df, full_path)
    return df


df = extract_data(site, creds, num_days, output)
df.sort_values('clicks', ascending=False)
plt = get_graphic_from_data(df)


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


# plt = get_graphic_from_csv('./hauswasserpumpe_info/gsc_data.csv')
plt.savefig('graphic.jpg')