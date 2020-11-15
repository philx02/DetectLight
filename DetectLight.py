#!/usr/bin/python2

import socket
import struct
import sys
import requests
from time import localtime, strftime

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 14500

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MCAST_GRP, MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                             # to MCAST_GRP, not all groups on MCAST_PORT
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def check_notify(light_status):
  check_sms = open('SmsAlarm.txt', 'r')
  if (check_sms.read(1) == '0'):
    return 0
  url = 'https://voip.ms/api/v1/rest.php'
  message = 'Basement lights ' + ('ON' if light_status == 1 else 'OFF')
  payload = {'api_username': 'pcayouette@spoluck.ca', 'api_password': '0TH7zRXKINXj7Exz8S0c', 'method': 'sendSMS', 'did': '4503141161', 'dst': '5144760655', 'message': message}
  return requests.get(url, params=payload)

def check_light_on(hysteresis, light_status):
  hysteresis += 1
  if hysteresis >= 10:
    if light_status != 1:
      print "[" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "] ON"
      sys.stdout.flush()
      light_status = 1
      check_notify(light_status)
    hysteresis = 10
  return (hysteresis, light_status)

def check_light_off(hysteresis, light_status):
  hysteresis -= 1
  if hysteresis <= 0:
    if light_status != 0:
      print "[" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "] OFF"
      sys.stdout.flush()
      light_status = 0;
      check_notify(light_status)
    hysteresis = 0
  return (hysteresis, light_status)
  
hysteresis = 5
light_status = -1

while True:
  frame = sock.recv(10240)
  if len(frame) > 0:
    if frame[0] == '1':
      (hysteresis, light_status) = check_light_on(hysteresis, light_status)
    elif frame[0] == '0':
      (hysteresis, light_status) = check_light_off(hysteresis, light_status)
