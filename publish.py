#!/usr/bin/env python3

import boto3
import json
import os
from configparser import ConfigParser
from sys import argv

## parameters provided by Deluge
script_dir = os.path.dirname(os.path.realpath(__file__))
ini = script_dir + '/config.ini'
file_id = argv[1]
file_name = argv[2]
file_path = argv[3]

if os.path.isfile(ini):
  config = ConfigParser()
  config.read(ini)
  queue_url = config.get('SQS', 'URL')
else:
  queue_url = os.environ['SQS_URL']

sqs = boto3.client('sqs')

with open(script_dir + '/attributes.json', 'r') as f:
    attrs = f.read()

msg_attrs = json.loads(attrs)
msg_attrs['FileHash']['StringValue'] = file_id
msg_attrs['FileName']['StringValue'] = file_name
msg_attrs['FilePath']['StringValue'] = file_path

response = sqs.send_message(
  QueueUrl=queue_url,
  MessageBody='Ready to transfer file {}'.format(file_name),
  MessageAttributes=msg_attrs,
  MessageDeduplicationId=file_id,
  MessageGroupId=file_path
)

print(response)
