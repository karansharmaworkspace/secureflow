import sys
sys.path.insert(0, 'demo/dashboard')
from app import scan_codebase, score_code_endpoint

with open('demo/test-codebase/banking-api.zip', 'rb') as f:
    data = scan_codebase(f.read())

print(f"Files scanned: {data['files_scanned']}")
print(f"Frameworks: {data['frameworks_found']}")
print(f"Total routes: {data['total_routes']}")

zombies = 0
for ep in data['endpoints']:
    scoring = score_code_endpoint(ep)
    if scoring['is_zombie']:
        zombies += 1
        print(f"  [ZOMBIE] {ep['framework']} {ep['method']} {ep['route']}")

print(f"\nZombie APIs found: {zombies}")
