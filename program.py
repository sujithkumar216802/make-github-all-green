import http.client
import json
import subprocess
import os
import time
import uuid
from datetime import date, timedelta

config = json.load(open('config.json'))

conn = http.client.HTTPSConnection("api.github.com")
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(config['access_token']),
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
}


today = date.today()
delta = timedelta(config['no_of_days'])
old_date = today - delta

# commit count
payload = "{\"query\":\"{  user(login: \\\"%s\\\") {    contributionsCollection(from:\\\"%sT00:00:00.000+00:00\\\", to:\\\"%sT00:00:00.000+00:00\\\"){\\n      contributionCalendar{\\n        weeks{\\n          contributionDays {\\n            date\\ncontributionCount\\n          }\\n        }\\n      }\\n    }  }}\"}" % (
    config['user_name'], old_date, today)
conn.request("POST", "/graphql", payload, headers)
res = conn.getresponse()
count_data = json.loads(res.read().decode('utf-8'))
weeks = count_data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

new_count = []

for week in weeks:
    for day in week['contributionDays']:
        if(day['contributionCount'] < config['commits_per_day']):
            new_count.append(
                {'date': day['date'], 'count': config['commits_per_day']-day['contributionCount']})

if len(new_count) == 0:
    exit()


# reponame
name_is_not_unique = True

while name_is_not_unique:
    repo_name = str(uuid.uuid4().hex)

    # repo exixts
    payload = "{\"query\":\"{\\n  user(login: \\\"%s\\\") {\\n    repository(name:\\\"%s\\\") {\\n      description\\n    }\\n  }\\n}\"" % (
        config['user_name'], repo_name)
    conn.request("POST", "/graphql", payload, headers)
    res = conn.getresponse()
    repo_data = json.loads(res.read().decode('utf-8'))
    if repo_data['data']['user']['repository'] == None:
        name_is_not_unique = False


curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_dir = os.path.join(curr_dir, repo_name)

# create repo
subprocess.run(['git', 'init', repo_name])

# create repo in github
conn.request('POST',  '/user/repos',
             '{"name":"%s", "private":"false"}' % (repo_name), headers)

# if the number of commits to be made it low it fails. To mitigate that a 3 second delay
time.sleep(3)

# add remote to repo
subprocess.run(['git', 'remote', 'add', 'origin', 'https://%s@github.com/%s/%s' %
                (config['access_token'], config['user_name'], repo_name)], cwd=repo_dir)

# set config
subprocess.run(['git', 'config', 'user.name', '"%s"' %
               (config['user_name'])], cwd=repo_dir)

subprocess.run(['git', 'config', 'user.email', '"%s"' %
               (config['email'])], cwd=repo_dir)


# commiting
for day in new_count:
    os.environ["GIT_AUTHOR_DATE"] = day['date'] + " 00:00:00"
    os.environ["GIT_COMMITTER_DATE"] = day['date'] + " 00:00:00"
    for i in range(day['count']):
        subprocess.run(['git', 'commit', '--allow-empty',
                       '-m', 'commit'], cwd=repo_dir)
        print('day : %s  commit: %d/%d' % (day['date'], i, day['count']))

subprocess.run(['git', 'push', 'origin', 'master'], cwd=repo_dir)
