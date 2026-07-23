import urllib.request, json
req = urllib.request.Request('https://api.github.com/repos/temurbek1306/InstagaramAvtoReels/actions/runs', headers={'Accept': 'application/vnd.github.v3+json'})
res = urllib.request.urlopen(req)
data = json.loads(res.read())
for run in data.get('workflow_runs', [])[:5]:
    print(f"{run['name']} - {run['status']} - {run['conclusion']} - {run['created_at']}")
