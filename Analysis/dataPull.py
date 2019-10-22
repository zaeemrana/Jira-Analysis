"""
Jira Analysis

@author Zaeem Rana
"""
from jira import JIRA
import pandas as pd

def main():
    # Read credentials
    creds = open("creds.txt")
    username = creds.readline()[:-1]
    pwd = creds.readline()

    # Establish link
    jiraURL = 'https://jira.cuauv.org/'
    options = {'server': jiraURL}
    jira = JIRA(options, basic_auth=(username, pwd))

    # Fetch projects and gather preliminary data
    projects = jira.projects()
    lstIssues =  jira.search_issues('project =OAMF', maxResults = 200) 
    lstOfIssueKeys = [x.key for x in lstIssues]
    lstOfIssueNames = [x.id for x in lstIssues]

    lstOfIssuesErrors = []
    general_df = []
    time_df = []
    comments_df = []

    for issue in lstIssues:
        try:
            issue_key = str(issue)
            issue_id = issue.id
            parent_id = issue.fields.parent.id
            parent_key = issue.fields.parent.key
            parent_summary = issue.fields.parent.fields.summary
            issue_summary = issue.fields.summary
            status = issue.fields.status.name

            project_key = issue.fields.project.key
            watchers = jira.watchers(issue).watchers[0].key
            
            try:
                assignee_name = issue.fields.assignee.name
                assignee_displayName = issue.fields.assignee.displayName
            except:
                assignee_name = "Not Assigned"
                assignee_displayName = "NA"
            
            row_gen = [issue_id, issue_key, issue_summary, parent_id, parent_key, parent_summary, project_key, status, assignee_name, assignee_displayName, watchers]
            general_df.append(row_gen)

            # Create the time df
            timespent = issue.fields.timespent
            aggregatetimespent = issue.fields.aggregatetimespent
            workratio = issue.fields.workratio
            agg_time_original = issue.fields.aggregatetimeoriginalestimate
            original_estimate = issue.fields.timeoriginalestimate
            estimate = issue.fields.timeestimate
            agg_progress = issue.fields.aggregateprogress

            row_time = [issue_id, issue_key,timespent, aggregatetimespent, workratio, agg_time_original, original_estimate, estimate, agg_progress]
            time_df.append(row_time)

            # Create the comments df
            issue = jira.issue(issue_key)
            issue_worklogs = issue.fields.worklog.worklogs
            
            for worklog in issue_worklogs:
                row_worklog = [issue_id, issue_key, worklog.author.key, worklog.timeSpent, worklog.started]    
                comments_df.append(row_worklog)
            
        except Exception as e:
            #print(e)
            #print("-------\n",issue, "\n-----")
            lstOfIssuesErrors.append(issue)
    print(lstOfIssuesErrors)
    
    gen_info_df = pd.DataFrame(general_df, columns = ['ID', 'Name', 'Summary', 'Parent ID', 'Parent Kay', 'Parent Sumamry', 'Project Key', 'Status', 'Assignee Name', 'DisplayName', 'Watchers'])
    gen_info_df.to_csv("generalIssue.csv" ,index = False)

    time_info_df = pd.DataFrame(time_df, columns = ['ID', 'Name', 'Time Spent', 'Aggreagte Time Spent', 'WorkRatio', 'AggregateTimeOriginial', 'original estimate', 'estimate', 'Aggregate progress'])
    time_info_df.to_csv("timeIssue.csv" ,index = False)

    comments_info_df = pd.DataFrame(comments_df, columns = ['ID', 'Name', 'Author', 'time spent', 'logged at'])
    comments_info_df.to_csv("commentsIssue.csv", index=False)
    
    file = open("issue_example.txt", "a+") 
    #print(jira.issue("OAMF-100").fields.assignee.name)
    #print(jira.issue("OAMF-100").fields.parent.key)
    #print("-"*30)


    issue = jira.issue("OAMF-109")
    #print(issue)


    #watcher = jira.watchers(issue)
    #print(watcher.watchers)

    # Framework for pulling worklog comments
    
    """
    issue_worklogs = issue.fields.worklog.worklogs
    for x in issue_worklogs:
        print(x.author)
        print(x.comment)
        print(x.id)
        print(x.self)
        print(x.started)
        print(x.timeSpent)
        print(x.timeSpentSeconds)
        print(x.updateAuthor)
        print("*"*30)
    """
    

    #comment = jira.comments(issue)
    #print(issue.fields.comment.comments)

    for issue in lstIssues[133:134]:
         for field_name in issue.raw['fields']:
              file.write("Field: " + str(field_name) + " Value: "+ str(issue.raw['fields'][field_name]) + "\n")
    file.close()
    

if __name__== "__main__" :
     main()