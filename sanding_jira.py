"""
Add sanding Hrs to Jira

@author Zaeem Rana
"""

from jira import JIRA
import pandas as pd

# Read credentials
creds = open("../config/creds.txt")
username = creds.readline()[:-1]
pwd = creds.readline()[:-1]

# Establish link
jiraURL = 'https://jira.cuauv.org/'
options = {'server': jiraURL}
jira = JIRA(options, auth=(username, pwd))

def log_hrs(netids, hrs):
    curr_proj = "KLMF-15"
    generalData_df = pd.read_csv('./Analysis/generalIssue'+curr_proj[:4]+'.csv')

    sandingissues_df = generalData_df[generalData_df["Parent Key"] == curr_proj]
    sandingIssues = sandingissues_df[["Name","Assignee Name"]]

    sandingIssues = sandingIssues.loc[sandingIssues['Assignee Name'].isin(netids)][["Name"]].values
    sandingIssues = sandingIssues.flatten().tolist()

    for name in sandingIssues:
        #issue = jira.issue(name)
        jira.add_worklog(name, timeSpent=hrs + "h")
