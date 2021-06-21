#!/usr/bin/env python3

import os
import sys
import multihash
import hashlib
from typing import Union
import base58


def printb(bytes_array):
  print(''.join(format(x, '02x') for x in bytes_array))


def hex_to_multihash(hexString: str) -> str:
  """Converts hex string to base-58 multihash"""
  b = bytearray.fromhex(hexString)
  b = b.rjust(32, b'\0')

  prefix = int.to_bytes(18,1,'big') + int.to_bytes(32,1,'big')

  b = prefix+b

  multStr = base58.b58encode(bytes(b))
  return multStr.decode('utf-8')


for line in sys.stdin.readlines():
  line = line.strip()

  h = hex_to_multihash(line)
  print(h)

