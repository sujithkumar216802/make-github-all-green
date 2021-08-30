import json
import http.client
import uuid

config = json.load(open('config.json'))

conn = http.client.HTTPSConnection("api.github.com")
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {}'.format(config['access_token']),
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
}


# commit count
payload = "{\"query\":\"{  user(login: \\\"%s\\\") {    contributionsCollection{\\n      contributionCalendar{\\n        weeks{\\n          contributionDays {\\n            date\\ncontributionCount\\n          }\\n        }\\n      }\\n    }  }}\"}" % (config['user_name'])
conn.request("POST", "/graphql", payload, headers)
res = conn.getresponse()
count_data = json.loads(res.read().decode('utf-8'))


#reponame

name_is_not_unique = True

while name_is_not_unique:
    repo_name = str(uuid.uuid4().hex)

    #repo exixts
    payload = "{\"query\":\"{\\n  user(login: \\\"%s\\\") {\\n    repository(name:\\\"%s\\\") {\\n      description\\n    }\\n  }\\n}\"" % (config['user_name'], repo_name)
    conn.request("POST", "/graphql", payload, headers)
    res = conn.getresponse()
    repo_data = json.loads(res.read().decode('utf-8'))
    if repo_data['data']['user']['repository']==None:
        name_is_not_unique = False
