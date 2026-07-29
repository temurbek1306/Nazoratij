import requests

token = "EAAVZCPnlPl5sBSJQLw2OirDeLMk0wUC2OyxVffx8SFfXgdO7OxGKOahgBtMfdfrWbhCZC1S9qAHZAt2KiJIBKR5LmEhZCmBYQ2MilD276ZAkHT3fS8ZAozvsiLGjdBJ9QLFhwhk8Wc0f0smWPwMYq9hdcKZCITFvCLr182NZA02NEwhWzWex2cK8G8vgrPlZA01hcLwZDZD"

res = requests.get(f"https://graph.facebook.com/v19.0/me/accounts?access_token={token}").json()
print(res)
