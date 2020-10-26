#!/usr/bin/env python3

import boto3
import json
import os
from configparser import ConfigParser
from sys import argv

## parameters provided by Deluge
script_dir = os.path.dirname(os.path.realpath(__file__))
ini = script_dir + '/config.ini'
t_hash = argv[1]
t_name = argv[2]
t_path = argv[3]

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
msg_attrs['Hash']['StringValue'] = t_hash
msg_attrs['Name']['StringValue'] = t_name
msg_attrs['Path']['StringValue'] = t_path

if os.path.isdir(t_path + '/' + t_name):
  msg_attrs['Directory']['StringValue'] = 'True'

response = sqs.send_message(
  QueueUrl=queue_url,
  MessageBody='Ready to transfer file {}'.format(t_name),
  MessageAttributes=msg_attrs,
  MessageDeduplicationId=t_hash,
  MessageGroupId=t_path
)

print(response)
