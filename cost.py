# -*- coding: utf-8 -*-
"""
Created on Mon May 20 13:50:10 2019

@author: aritra.chatterjee
"""
import boto3
import json
import pandas as pd
import numpy as np
from datetime import datetime,timedelta

with open('rootkey.csv') as key_file:
    keyfile = key_file.readlines()
    
client = boto3.client(
    'ce',
    aws_access_key_id=keyfile[0].split('=')[1][:-1],

    aws_secret_access_key=keyfile[1].split('=')[1])

"""Computation of starting day of the month from current date"""

current_year_month = datetime.now().strftime('%Y-%m')
first_day = '01'
start_bill_date = current_year_month+'-'+first_day

response = client.get_cost_and_usage(
            TimePeriod={
        'Start':start_bill_date,
        'End': datetime.now().strftime('%Y-%m-%d')
    },
     Granularity = 'MONTHLY',
     Metrics= ['USAGE_QUANTITY','AMORTIZED_COST'],
     GroupBy=[{
             'Type': 'DIMENSION',
             'Key': 'INSTANCE_TYPE'}
             ]
        )

# =============================================================================
# with open("cost.json","w") as cost:
#     json.dump(response,cost)
#     
# =============================================================================
results=response['ResultsByTime']
results=results[0]
usage=results['Groups']
keys=[usage[i]['Keys'] for i in range(len(usage))]
cost = usage[0]['Metrics']['AmortizedCost']['Amount']
hours=[usage[i]['Metrics']['UsageQuantity']['Amount']for i in range(len(usage))]
hours_consumption=[round((float(usage[i]['Metrics']['UsageQuantity']['Amount'])/750)*100,2) for i in range(len(usage))]
Cost = float(cost)
total_cost=round( Cost*70.716463,2)
usage_df=pd.DataFrame(np.column_stack([keys,hours,hours_consumption]),columns=['Instance Type','Hours Consumed(750)','Hours Consumption(%)'])


"""Switch of the ec2 instance"""
data=usage_df[usage_df['Instance Type']=='t2.micro']
hours=(data['Hours Consumption(%)'].values)
hours = int(float(hours[0]))

if hours > 95:
    
    instance_id='i-0e803b92bf78d32ee'
    
    ec2=boto3.client('ec2','ap-south-1',
    aws_access_key_id=keyfile[0].split('=')[1][:-1],
    aws_secret_access_key=keyfile[1].split('=')[1])
    
    ec2.describe_regions()
    ec2 = boto3.resource('ec2',
                         'ap-south-1',
                             aws_access_key_id=keyfile[0].split('=')[1][:-1],
                             aws_secret_access_key=keyfile[1].split('=')[1])
    instance = ec2.Instance(instance_id)
    
    instance.stop(True)
    with open('cost_log.txt', 'a+') as log_note:
        log_note.write("{}: ec2 instance stopped. \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

else: 
    with open('cost_log.txt', 'a+') as log_note:
        log_note.write("{}: ec2 instance total hour consumption is {} \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),hours_consumption[2]))

    

"""Switch of the RDS Database"""
rds=usage_df[usage_df['Instance Type']=='db.t2.micro']
hours=(rds['Hours Consumption(%)'].values)
hours = int(float(hours[0]))

if hours > 95:
    client = boto3.client('rds','us-east-1',
                          aws_access_key_id=keyfile[0].split('=')[1][:-1],
                          aws_secret_access_key=keyfile[1].split('=')[1])
    client.stop_db_instance(DBInstanceIdentifier='richie-database')
    with open('cost_log.txt', 'a+') as log_note:
        log_note.write("{}: db2 database instance stopped. \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


else: 
    with open('cost_log.txt', 'a+') as log_note:
        log_note.write("{}: db2 instance total hour consumption is {} \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),hours_consumption[1]))

with open('cost_log.txt', 'a+') as log_note:
    log_note.write("{}: The total cost for AWS till this moment is {} \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),total_cost))

import yagmail
password='Anahata@123' ### Password is changed now and cryptography is used on the user credentials.
yagmail.register("richie.chatterjee31@gmail.com", password)
yag = yagmail.SMTP("richie.chatterjee31@gmail.com", password)
html_msg = ["{}: The total cost as of now is Rs {} \r\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),total_cost),
            r"C:\Users\aritra.chatterjee\Desktop\AWS_API_Key\cost_log.txt"]
yag.send('richie.chatterjee31@gmail.com', "AWS Bill Till This Moment!", html_msg)


