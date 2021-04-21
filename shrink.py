#!/usr/bin/env python3

import os
import sys
import hashlib
import base58

def get_hex(b58_encoded_peer_id_str: str) -> str:
  """Converts base-58 multihash to hex representation"""
  bytes = base58.b58decode(b58_encoded_peer_id_str)
  sha256 = hashlib.sha256(bytes).digest()
  return sha256.hex()[:6]

def shorten(str):
  if str.startswith('Qm') or str.startswith('12D3Koo'):
    if str.endswith(':'):
      str = str[:-1]
    return '<%s>' % (get_hex(str))
  else:
    return str


for line in sys.stdin:
  words = line.split()
  words = tuple(map(shorten, words))
  print('%s '*len(words) % words, flush=True)
