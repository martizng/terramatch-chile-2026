"""Checks the demonstration's published scientific files against the original GitHub blob IDs."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    'results/mars_scores_web.csv':'016a5cadb36081a70af2e0014816a5b88b3db0df',
    'results/moon_scores_web.csv':'2d7392dc93f6c96c041f9eff134d6d1929fbf794',
    'results/sites_summary.csv':'fb6e34ef2e8a0e0f2c0637312afb675b7106245e',
    'results/validation.json':'05b89d9db6c8e5c2569aa5a4dcc9c521abaca491',
    'data/targets.json':'b2251c5ae14f5200a95f70273534afd0425c3057',
}
for rel,expected in EXPECTED.items():
    data=(ROOT/rel).read_bytes()
    blob=b'blob '+str(len(data)).encode()+b'\x00'+data
    digest=hashlib.sha1(blob).hexdigest()
    assert digest==expected, f'Scientific source changed: {rel}; expected {expected}, got {digest}'
print('PASS: All five original scientific inputs match published GitHub source blob IDs')
