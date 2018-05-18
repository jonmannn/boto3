import datetime
import time
import numpy as np
import boto3
from pprint import pprint
from atreides.client import google_sheets

def get_cpu_utilization(instance_id):
    """
    Retrieves CPU Utilization for the past hour at 5-minute intervals
    for a given user's instance.
    """

    now = datetime.datetime.utcnow()
    all_ordered_data = []
    cloudwatch = boto3.resource('cloudwatch')
    metric = cloudwatch.Metric('AWS/EC2', 'CPUUtilization')

    # date_list contains everyday for the past 30 days as a datetime object
    a = datetime.datetime.today()
    numdays = 30
    date_list = []
    for x in range(0, numdays):
        date_list.append(a - datetime.timedelta(days=x))

    # loop through each of those days and pull max cpu for every 5 min
    for date in date_list:
        end_time = date + datetime.timedelta(days=1)
        response = metric.get_statistics(
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id},
            ],
            StartTime= date,
            EndTime= end_time,
            Period=300,
            Statistics=['Maximum'],
        )
        # return chronological results
        ordered_data = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
        all_ordered_data.append(ordered_data)
    return all_ordered_data

max_cpu_list = []
date_time_list = []
x = get_cpu_utilization('i-0c00710a04ff04190')
for item in x:
    for thing in item:
        max_cpu = thing['Maximum']
        date_time = thing['Timestamp']
        date_time = date_time.strftime('%-m/%d %H:%M')
        date_time_list.append(date_time)
        max_cpu_list.append(max_cpu)

data_dict = dict(zip(date_time_list, max_cpu_list))
pprint(data_dict)

# for key in data_dict:
#     if data_dict[key] > 70:
#         print('{}: {}'.format(key, data_dict[key]))

google_sheets.put_cells(
    workbook_title='AppStream 2.0 CPU Usage',
    sheet_title='test',
    records=data_dict,
    overwrite=False,
)