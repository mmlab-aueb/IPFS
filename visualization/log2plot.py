#!/usr/bin/env python3

###################################################
#                                                 #
# Written by Spyros Voulgaris (voulgaris@aueb.gr) #
# April 2021                                      #
#                                                 #
# Mobile Multimedia Lab                           #
# Athens University of Economics and Business     #
# Athens, Greece                                  #
#                                                 #
###################################################

import sys
import re
from datetime import datetime
from datetime import timedelta
import collections
import base58
import hashlib




####
# Global variables
####

ID_LEN = 6

requests = collections.defaultdict(dict)
order = []
causality = []

startTime=None
endTime=None
lastResponse=None

context_canceled = collections.defaultdict(int)

target_determined = collections.defaultdict(int)

unmatched_lines = []



####
# Function that converts a multihash to its hex representation
####

def get_hex(b58_encoded_peer_id_str: str) -> str:
  """Converts base-58 multihash to hex representation"""
  bytes = base58.b58decode(b58_encoded_peer_id_str)
  sha256 = hashlib.sha256(bytes).digest()
  return sha256.hex()



####
# The handle_<EVENT> functions are called by the main loop when
# a line matching the respective event's regex is found.
####

def handle_querying(time, match):
    peer = get_hex(match.group(2))

    if peer not in order:
      order.append(peer)

    requests[peer]['query_start'] = time

    # set query_end to this time too, in case it never ends
    #requests[peer]['query_end'] = time

    # if a dialing had started, record that it just ended
    if 'dial_start' in requests[peer]:
      requests[peer]['dial_end'] = time

def handle_dialing(time, match):
    global lastResponse
    peer = get_hex(match.group(2))

    if peer not in order:
      order.append(peer)

    requests[peer]['dial_start'] = time

    # set dial_end to this time too, in case it never ends
    requests[peer]['dial_end'] = time

    if lastResponse!=None:
      causality.append( (lastResponse[0], lastResponse[1], peer, time) )

def handle_says_use(time, match):
    global lastResponse
    peer = get_hex(match.group(2))
    requests[peer]['query_end'] = time
    lastResponse = (peer, time)

def handle_dial_error(time, match):
    global lastResponse
    peer = get_hex(match.group(2))
    requests[peer]['dial_error'] = time
    requests[peer]['dial_end'] = time
    lastResponse = (peer, time)

def handle_context_canceled(time, match):
    context_canceled[time] += 1

def handle_target_found(time, match):
    global endTime
    peer = get_hex(match.group(2))
    target_determined[time] += 1
    endTime = time
    requests[peer]['in_targets'] = True



####
# The following function returns the 'relative time', i.e.,
# the time in seconds since the beginning of this query,
# for a the time when 'event_type' occured for this 'peer'.
####

def relative_time(peer, event_type):
  one_sec = timedelta(seconds=1)
  minus_one = startTime - one_sec

  time = requests[peer].get(event_type, minus_one)
  rel_time = (time - startTime).total_seconds()

  return rel_time



####
# REGULAR EXPRESSIONS
#
# The following statements define the regular expressions
# to use for parsing logs.
#
# The regex dict associated to each event type a tuple <regex,func>,
# containing the regex to detect that event and the handler function.
####

# Time format
re_time = '(\d\d:\d\d:\d\d.\d\d\d)'

# Multihashes
re_Qm = 'Qm\w{44}'  # Qm multihash
re_12D3KooW = '12D3KooW\w{44}'  # 12D3KooW multihash
re_multihash = '('+re_Qm+'|'+re_12D3KooW+')'

# Lines
regex = {}
regex['querying'] = (re_time + ': \* querying ' + re_multihash, handle_querying)
regex['dialing'] = (re_time + ': dialing peer: ' + re_multihash, handle_dialing)
regex['says_use'] = (re_time + ': \* ' + re_multihash + ' says use(?: '+re_multihash+')*', handle_says_use)
regex['dial_error'] = (re_time + ': error: failed to dial ' + re_multihash + ': all dials failed', handle_dial_error)
regex['context_canceled'] = (re_time + ': error: context canceled$', handle_context_canceled)
regex['target_found'] = (re_time + ': ' + re_multihash, handle_target_found)





####
# The main loop of the parser, iterating through stdin lines, one at a time.
# For each line, it first tried to match a time regex in the beginning.
# Then, it loops through all patterns defined in the regex dict, and if
# one is found, it calls the respective handler function.
####

lineNum = 0
for line in sys.stdin:
  line = line.strip()
  #print(line)

  lineNum += 1

  # First, parse time, which is common for most lines.
  # If a line does not report a time keep the previous time,
  # as it probably refers to the same event.
  match = re.match(re_time, line)
  if match:
    time = datetime.strptime(match.group(1), '%H:%M:%S.%f')
    if startTime==None:
      startTime = time


  # Check all regular expressions for a match
  matched = False
  for r in regex:
    m = re.match(regex[r][0], line)
    if m:
      regex[r][1](time, m)
      matched = True
      break
  
  if not matched:
    unmatched_lines.append( (lineNum, time, line) )





####
# Parsing is complete. Let's output the results!
#
# First output for each peer contacted the times for starting/ending
# the respective dialing and querying,as well as whether there was
# an error with dialing, and whether that peer was eventually
# among the set of K peers selected as targets.
####

peerIndex = {}
numRequests = len(order)

print('#hop\tdial_st\tdial_end\tdial_err\tquery_st\tquery_end\tpeer_hash\ttarget')

for i,peer in enumerate(order):

  dial_start = relative_time(peer, 'dial_start')
  dial_end = relative_time(peer, 'dial_end')
  dial_error = relative_time(peer, 'dial_error')

  query_start = relative_time(peer, 'query_start')
  query_end = relative_time(peer, 'query_end')

  in_targets = int('in_targets' in requests[peer])

  if query_start > query_end and endTime != None :  # i.e., this query started but never ended
    query_unfinished = (endTime - startTime).total_seconds()
  else:
    query_unfinished = -1

  print('%d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%d' % (i+1, dial_start, dial_end, dial_error, query_start, query_end, query_unfinished, peer[0:ID_LEN], in_targets))

  peerIndex[peer] = i+1




####
# Output the causality relations between events,
# namely providing coordinates for the respective red arrows in the plot.
#
# The causality relations are determined in a best effort way,
# which is *not* error-proof.
####

print('\n\n#Causality')
print('#timeA\tpeerA\ttimeB\tpeerB')

for (peer1, time1, peer2, time2) in causality:
  time1 = (time1 - startTime).total_seconds()
  time2 = (time2 - startTime).total_seconds()

  if peer1 in peerIndex:
    index1 = peerIndex[peer1]
  else:
    index1 = 0

  if peer2 in peerIndex:
    index2 = peerIndex[peer2]
  else:
    index2 = numRequests

  print('%f\t%d\t%f\t%d' % (time1, index1, time2, index2))




####
# Output the times when 'context canceled' events occured.
# These are plotted as thick vertical dashed lines in black.
####

print('\n\n#Context canceled')
print('#time\tnumPeers\tlabel')

for time in context_canceled:
  count = context_canceled[time]
  rel_time = (time - startTime).total_seconds()
  print('%.2f\t%.2f\t%d' % (rel_time, len(order)+1, count) )




####
# Output the times when peers are reported as selected targets.
# These are plotted as thick vertical dashed lines in green.
####

print('\n\n#Time(s) when the K closest peers to the target ID were determined')
print('#time\tnumPeers\tlabel')

for time in target_determined:
  count = target_determined[time]
  rel_time = (time - startTime).total_seconds()
  print('%.2f\t%.2f\t%d' % (rel_time, len(order)+1, count) )



####
# Finally, output the list of lines that have *not* matched any
# regex pattern during parsing.
#
# These lines are not included in the plots, but they are very useful
# when trying to interpret the logs in full detail, and to see
# what has been left out in special cases, for future improvements
# of this parser.
####

print('\n\n#Lines ignored while parsing')

for line in unmatched_lines:
  dtStr = ''
  
  if line[1] != None:
    dt = (line[1] - startTime).total_seconds()
    dtStr = ' (time: %.2f)' % dt
  print('%d%s: %s' % (line[0], dtStr, line[2]) )
