#!/usr/bin/env python3

import boto3
import json
import os
from configparser import ConfigParser
from sys import argv
from sys import exit

## parameters provided by Deluge
script_dir = os.path.dirname(os.path.realpath(__file__))
ini = script_dir + '/config.ini'

if os.path.isfile(ini):
  config = ConfigParser()
  config.read(ini)
  user = config.get('Main', 'User')
  t_host = config.get('Main', 'Host')
  target_dir = config.get('Main', 'Target')
  streams = config.get('Main', 'Streams')
  queue_url = config.get('SQS', 'URL')

  try:
    profile = config.get('Credentials', 'Profile')
  except:
    print('No AWS credentials profile provided. Using default...')
    profile = 'default'
else:
  queue_url = os.environ['SQS_URL']

with open(script_dir + '/attributes.json', 'r') as f:
    attrs = f.read()

session = boto3.session.Session(profile_name=profile)
sqs = session.client('sqs')

message = sqs.receive_message(
  QueueUrl=queue_url,
  MessageAttributeNames=['All'],
  MaxNumberOfMessages=1
)

try:
  handles = [msg['ReceiptHandle'] for msg in message['Messages']]
  attrs = [msg['MessageAttributes'] for msg in message['Messages']]
except:
  print('No messages in queue.')
  exit(0)

for handle in handles:
  deleted = sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=handle
  )
  print('Deleted message {}'.format(handle))

p = 5

for attr in attrs:
  t_path = attr['Path']['StringValue']
  t_name = attr['Name']['StringValue']
  is_dir = attr['Directory']['StringValue']

  if is_dir == 'True':
    cmd = "bbcp -Ar -P {} -s {} {}@{}:{}/'{}' {}/'{}'".format(p, streams, user, t_host, t_path, t_name, target_dir, t_name)
  else:
    cmd = "bbcp -Ar -P {} -s {} {}@{}:{}/'{}' {}".format(p, streams, user, t_host, t_path, t_name, target_dir)

  print(cmd)
  res = os.system(cmd)
