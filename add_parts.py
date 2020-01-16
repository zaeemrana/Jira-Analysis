"""
Add Parts quickly to Jira

@author Zaeem Rana
"""

import sys, os
import add_parts_fetch
import download_parts
import update_issue
import zipfile
from jira import JIRA
import pandas as pd

# Read credentials
creds = open("./Analysis/creds.txt")
username = creds.readline()[:-1]
pwd = creds.readline()[:-1]

# Establish link
jiraURL = 'https://jira.cuauv.org/'
options = {'server': jiraURL}
jira = JIRA(options, auth=(username, pwd))

if __name__ == "__main__":
    row_range = str(sys.argv[1])
    row = add_parts_fetch.main(row_range)[0]

    zipLoc = row[1].split("=")[1]
    txtLoc = row[2].split("=")[1]
    projName = row[5]
    netid = [row[4]]


    curr_proj = "KLMF"
    generalData_df = pd.read_csv('./Analysis/generalIssue'+curr_proj[:4]+'.csv')

    memProjects_df = generalData_df[generalData_df["Parent Key"] == curr_proj]
    subProj = memProjects_df[["Name","Assignee Name"]]

    subProj = subProj.loc[subProj['Assignee Name'].isin(netid)][["Name"]].values
    subProj = subProj.flatten().tolist()
    print(subProj)
    print(projName)
    subProj = subProj[0]

    download_parts.main(zipLoc,"zip"+projName+".zip")

    with zipfile.ZipFile('./AddParts/'+"zip"+projName+'.zip', 'r') as zip_ref:
        zip_ref.extractall('./AddParts/'+projName+"/")

    download_parts.main(txtLoc,"/"+projName+"/txt"+projName +".txt")
    fileTxt = "./AddParts/"+projName + "/txt" + projName + ".txt"
    with open(fileTxt) as f:
        lines = f.readlines()
    lines = [line.rstrip('\n') for line in open(fileTxt)]

    def getListOfFiles(dirName):
        # create a list of file and sub directories
        # names in the given directory
        listOfFile = os.listdir(dirName)

        allFiles = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(fullPath):
                allFiles = allFiles + getListOfFiles(fullPath)
            else:
                allFiles.append(dirName +"/"+ entry)
        return allFiles


    files = getListOfFiles('./AddParts/'+projName+'/')
    pdfs = []
    for file in files:
        if  file[-3:] == 'PDF':
            pdfs.append(file)

    print(pdfs)
    print(lines)
    # print(netid)
    # print(subProj)
    issueLst = []

    for i,file_name in enumerate(pdfs):
        
        issue_name = file_name.split("/")[-1][:-4] 
        
        issue_dict = {
            'project': {'key': curr_proj},
            'parent': {'key': subProj},
            'assignee': {'self': 'http://jira.cuauv.org/rest/api/2/user?username='+netid[0], 'name': netid[0], 'key': netid[0], 'emailAddress': netid[0]+'@cornell.edu'},
            'priority': {'name': 'Medium', 'id': '3'},
            'summary': issue_name,
            'description': 'Enter Description here',
            'issuetype':{'self': 'http://jira.cuauv.org/rest/api/2/issuetype/10003', 'id': '10003', 'description': 'The sub-task of the issue', 'iconUrl': 'http://jira.cuauv.org/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype', 'name': 'Sub-task', 'subtask': True},
        }
        #new_issue = jira.create_issue(fields = issue_dict)
        #issueLst.append(new_issue.key)    
        #jira.add_attachment(issue= new_issue, attachment= file_name)

    for i,x in enumerate(issueLst):
            print(x, str(lines[i])+"h")
            #update_issue.set_time_remaing(jira, x, str(lines[i])+"h")

