import urllib.request, json, zipfile, io
req = urllib.request.Request('https://api.github.com/repos/temurbek1306/InstagaramAvtoReels/actions/runs', headers={'Accept': 'application/vnd.github.v3+json', 'Authorization': 'token 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'})
res = urllib.request.urlopen(req)
runs = json.loads(res.read())['workflow_runs']
failed_run = next(r for r in runs if r['event'] == 'repository_dispatch')
print(f"Run ID: {failed_run['id']}, Conclusion: {failed_run['conclusion']}")
req2 = urllib.request.Request(f"https://api.github.com/repos/temurbek1306/InstagaramAvtoReels/actions/runs/{failed_run['id']}/logs", headers={'Accept': 'application/vnd.github.v3+json', 'Authorization': 'token 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'})
res2 = urllib.request.urlopen(req2)
z = zipfile.ZipFile(io.BytesIO(res2.read()))
log_file = [f for f in z.namelist() if 'Run Telegram Command' in f][0]
print("\nLOGS:\n" + z.read(log_file).decode('utf-8'))
