import requests, json, time

start = time.time()
print('Uploading real PDF to Render...')
r = requests.post(
    'https://synaptica-7ha3.onrender.com/api/upload', 
    files={'file': ('END1.pdf', open('D:/Desktop/Vault/B-TECH ON BLUNT/SEM-1/CSA/END 1.pdf','rb'), 'application/pdf')},
    timeout=300
)
elapsed = time.time() - start
print(f'Response in {elapsed:.1f}s, status: {r.status_code}')
data = r.json()
print('fact_count:', data.get('fact_count'))
print('debug:', data.get('debug'))
print('facts returned:', len(data.get('facts', [])))
if data.get('facts'):
    print('\nSample facts:')
    for f in data['facts'][:3]:
        print(f"  - [{f['category']}] {f['statement'][:80]}")
else:
    print('Still 0 facts.')
    print('Full response:', json.dumps(data, indent=2)[:600])
