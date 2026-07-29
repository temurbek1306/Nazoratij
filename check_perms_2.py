import requests

token = "EAAVZCPnlPl5sBSEh6hlkjB9KnAgvcQK3qWRImBStIHelIB3lgqyfQZBWZALP0kzPOjsYONBdzQkh4ZAXkirzKwZB6PamZCaAPS67RxzdjJBFIpDnY4oQOMqpCdCj96mZBVIP8KMxaBDZAfZBht3etXfCfc9aZBKUOVK6juC4IKpLAuWWa1q5R7ua9Tdrm0pn10wSrDNuh1u0JgzZB1sBihNt3lZBCDtGEtT1JhklJZAEGehgZD"

# Check page info
res = requests.get(f"https://graph.facebook.com/me?fields=id,name&access_token={token}").json()
print("Page Info:", res)

# Check permissions
perms = requests.get(f"https://graph.facebook.com/me/permissions?access_token={token}").json()
print("\nPermissions:")
if 'data' in perms:
    for p in perms['data']:
        if p.get('status') == 'granted':
            print(f"- {p.get('permission')}")
else:
    print(perms)
