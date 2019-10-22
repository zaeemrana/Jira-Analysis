"""
Add sanding Hrs to Jira

@author Zaeem Rana
"""

from jira import JIRA
import pandas as pd

# Read credentials
creds = open("./Analysis/creds.txt")
username = creds.readline()[:-1]
pwd = creds.readline()

# Establish link
jiraURL = 'https://jira.cuauv.org/'
options = {'server': jiraURL}
jira = JIRA(options, basic_auth=(username, pwd))

def log_hrs(netids):
    curr_proj = "OAMF-122"
    generalData_df = pd.read_csv('./Analysis/generalIssue.csv')
    
    sandingissues_df = generalData_df[generalData_df["Parent Kay"] == curr_proj]
    sandingIssues = sandingissues_df[["Name","Assignee Name"]]
    
    sandingIssues = sandingIssues.loc[sandingIssues['Assignee Name'].isin(netids)][["Name"]].values
    sandingIssues = sandingIssues.flatten().tolist()
    
    for name in sandingIssues:
        #issue = jira.issue(name)
        jira.add_worklog(name, timeSpent="1d")
