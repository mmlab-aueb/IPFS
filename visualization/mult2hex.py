#!/usr/bin/env python3

import os
import sys
import multihash
import hashlib
from typing import Union
import base58


def printb(bytes_array):
  return ''.join(format(x, '02x') for x in bytes_array)


def multihash_to_hex(b58_encoded_peer_id_str: str) -> str:
  """Converts base-58 multihash to hex representation"""
  bytes = base58.b58decode(b58_encoded_peer_id_str)
  bytes = bytes[2:]
  #sha256 = hashlib.sha256(bytes).digest()
  return printb(bytes)


for line in sys.stdin.readlines():
  line = line.strip()

  h = multihash_to_hex(line)
  print(h)

