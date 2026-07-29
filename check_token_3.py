import requests

token = "EAAVZCPnlPl5sBSEh6hIkjB9KnAgvcQK3qWRImBStIHelIB3lgqyfQZBWZALP0kzPOjsYONBdzQkh4ZAXkirzKwZB6PamZCaAPS67RxzdjJBFIpDnY4oQOMqpCdCj96mZBVIP8KMxaBDZAfZBht3etXfCfc9aZBKUOVK6juC4IKpLAuWWa1q5R7ua9Tdrm0pn10wSrDNuh1u0JgzZB1sBihNt3lZBCDtGEtT1JhklJZAEGehgZD"

print("Token length:", len(token))

res = requests.get(f"https://graph.facebook.com/me?access_token={token}").json()
print("ME:", res)
