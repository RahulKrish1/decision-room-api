import hashlib
import secrets
import random
from typing import Sequence

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make_seed() -> str:
    # 32 bytes -> 64 hex chars
    return secrets.token_hex(32)

def pick_index(seed: str, n: int) -> int:
    rng = random.Random(seed)   # deterministic given seed
    return rng.randrange(n)     # uniform among [0, n)
