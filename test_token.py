import urllib.request
import json
import urllib.error

TOKEN = "EAAVZCPnlPl5sBSMn3RbpGlYpT2zBnEfRQ6A6CVD9I2gCT04wI9ukhzkLTLUiSIy7IUZBeBQgRdIYXWC6AgAW6zfeC7HlZCj6pu2fyQKnmLwXZC3CJnVmU4t0FpO2UWtV3eUZBnei2TTRs5PEjmArGg67FG5wQz2dRbtyq3c0HqacRZCqqW4ZCPHIwcHkj8ouoMkqwPq8ZBMNPbuPlZBrRXOC1Snqqi54QLNN7UXhY7hZCrS7L3"
URL = f"https://graph.facebook.com/v20.0/1240423202480355?fields=instagram_business_account&access_token={TOKEN}"

try:
    req = urllib.request.Request(URL)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    print("SUCCESS:", data)
except urllib.error.HTTPError as e:
    err = e.read().decode('utf-8')
    print("HTTP ERROR:", err)
except Exception as e:
    print("OTHER ERROR:", e)
