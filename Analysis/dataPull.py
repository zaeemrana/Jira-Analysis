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
    pwd = creds.readline()[:-1]

    # Establish link
    jiraURL = 'https://jira.cuauv.org/'
    options = {'server': jiraURL}
    jira = JIRA(options, auth=(username, pwd))

    # Fetch projects and gather preliminary data
    projects = jira.projects()

    projects = {"Mech2": [10400, "Artemis & Apollo Mechanical Fabrication"] ,"OAMF": [10600,"Odysseus & Ajax Mechanical Fabrication"],"KLMF": [10700,"Kraken & Leviathan Mechanical Fabrication"]}

    # This list contains the project keys for member projects. These projects in jira have no parent so this list helps with logic tracking
    memProj = ['MECH2-134', 'MECH2-93', 'MECH2-84', 'MECH2-33', 'MECH2-32', 'MECH2-27', 'MECH2-26', 'MECH2-25', 'MECH2-24', 'MECH2-23', 'MECH2-22',
                'MECH2-21', 'MECH2-20', 'MECH2-19', 'MECH2-18', 'MECH2-17', 'MECH2-16', 'MECH2-15', 'MECH2-14', 'MECH2-13', 'MECH2-8', 'MECH2-6',
                'MECH2-5', 'MECH2-4', 'MECH2-3', 'MECH2-2','OAMF-122', 'OAMF-92', 'OAMF-14', 'OAMF-13', 'OAMF-12', 'OAMF-11', 'OAMF-10', 'OAMF-9',
                'OAMF-8', 'OAMF-7', 'OAMF-6', 'OAMF-5', 'OAMF-4', 'OAMF-3','KLMF-14', 'KLMF-13', 'KLMF-12', 'KLMF-11', 'KLMF-10', 'KLMF-9', 'KLMF-8',
                'KLMF-7', 'KLMF-6', 'KLMF-5', 'KLMF-4', 'KLMF-3','KLMF-2', 'KLMF-1']

    for proj in projects:
        lstIssues =  jira.search_issues('project ='+proj, maxResults = 200)

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

                if issue.key not in memProj:
                    parent_id = issue.fields.parent.id
                    parent_key = issue.fields.parent.key
                    parent_summary = issue.fields.parent.fields.summary
                else:
                    parent_id = projects[proj][0]
                    parent_key = proj
                    parent_summary = projects[proj][1]

                issue_summary = issue.fields.summary
                status = issue.fields.status.name

                project_key = issue.fields.project.key
                try:
                    watchers = jira.watchers(issue).watchers[0].key
                except:
                    watchers = None

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

                print(e, issue.fields.summary)
                lstOfIssuesErrors.append(issue)
        #print([x.key for x in lstOfIssuesErrors])

        gen_info_df = pd.DataFrame(general_df, columns = ['ID', 'Name', 'Summary', 'Parent ID', 'Parent Key', 'Parent Sumamry', 'Project Key', 'Status', 'Assignee Name', 'DisplayName', 'Watchers'])
        gen_info_df.to_csv("generalIssue"+proj+".csv" ,index = False)

        time_info_df = pd.DataFrame(time_df, columns = ['ID', 'Name', 'Time Spent', 'Aggreagte Time Spent', 'WorkRatio', 'AggregateTimeOriginial', 'original estimate', 'estimate', 'Aggregate progress'])
        time_info_df.to_csv("timeIssue"+proj+".csv" ,index = False)

        comments_info_df = pd.DataFrame(comments_df, columns = ['ID', 'Name', 'Author', 'time spent', 'logged at'])
        comments_info_df.to_csv("commentsIssue"+proj+".csv", index=False)

        file = open("issue_example"+proj+".txt", "a+")


        for issue in lstIssues[133:134]:
            for field_name in issue.raw['fields']:
                file.write("Field: " + str(field_name) + " Value: "+ str(issue.raw['fields'][field_name]) + "\n")
        file.close()


if __name__== "__main__" :
     main()
