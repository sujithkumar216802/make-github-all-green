import json
import http.client

config = json.load(open('config.json'))

conn = http.client.HTTPSConnection("api.github.com")
payload = "{\"query\":\"{  user(login: \\\"sujithkumar216802\\\") {    contributionsCollection{\\n      contributionCalendar{\\n        weeks{\\n          contributionDays {\\n            date\\ncontributionCount\\n          }\\n        }\\n      }\\n    }  }}\"}"
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {}'.format(config['access_token']),
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
}
conn.request("POST", "/graphql", payload, headers)
res = conn.getresponse()
data = res.read()
print(data)