#!/usr/bin/env python3

import os
import sys
import multihash
import hashlib
from typing import Union
import base58


def peerID_to_kademliaID(b58_encoded_peer_id_str: str) -> str:
  """Converts base-58 multihash to hex representation"""
  bytes = base58.b58decode(b58_encoded_peer_id_str) 
  sha256 = hashlib.sha256(bytes).digest()
  return sha256.hex()


for line in sys.stdin.readlines():
  line = line.strip()

  h = peerID_to_kademliaID(line)
  print(h,'('+line+')')

