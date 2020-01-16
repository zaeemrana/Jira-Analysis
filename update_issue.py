import requests

creds = open("./Analysis/creds.txt")
username = creds.readline()[:-1]
pwd = creds.readline()[:-1]

def update(jira, issue_key, fields):
    issue = jira.issue(issue_key)
    issue_id = issue.id
    url = issue._get_url("issue/" + issue_id)
    data = {"fields": fields}
    r = requests.put(url, json=data, auth=(username, pwd))
    #print(r)
    #print(r.text)

def set_time_remaing(jira, issue_key, remaining):
    fields = {"timetracking": {"remainingEstimate": remaining}}
    update(jira, issue_key, fields)
