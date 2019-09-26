"""
Read in data and effectivly analyze it
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
sns.set()
plt.show()

class jiraHrs():
    def __init__(self, s):
        self.timeTotal = self.parse(s)

    def parse(self, s):
        lstTime = s.split(' ')

        hrsTotal = 0
        for time in lstTime:
            if time[-1] == "d":
                hrsTotal += int(time[:-1])*3
            elif time[-1] == "h":
                hrsTotal += int(time[:-1])
            else:
                hrsTotal =+ int(time[:-1])/60
        return hrsTotal

    def getHrs(self):
        return self.timeTotal

comments_df = pd.read_csv("commentsIssue.csv")
time_per_person = comments_df[["Name","Author", "time spent", "logged at"]]

members = {}
members_sanding = {}
sanding = ["OAMF-123","OAMF-124","OAMF-125","OAMF-126","OAMF-127","OAMF-128","OAMF-129","OAMF-130","OAMF-131","OAMF-132","OAMF-133","OAMF-134","OAMF-135"]

for index, row in time_per_person.iterrows():
    if row["Name"] not in sanding:
        if row["Author"] not in members:
            members[row["Author"]] = jiraHrs(row["time spent"]).getHrs()
        else:
            members[row["Author"]] = members[row["Author"]] + jiraHrs(row["time spent"]).getHrs()
    else:
        if row["Author"] not in members_sanding:
            members_sanding[row["Author"]] = jiraHrs(row["time spent"]).getHrs()
        else:
            members_sanding[row["Author"]] = members_sanding[row["Author"]] + jiraHrs(row["time spent"]).getHrs()


print(members)
print(members_sanding) 
print(members.values())
print(members_sanding.values())

lsttemp = []
for s in members:
    if s in members_sanding:
        lsttemp.append( (members[s], members_sanding[s]) )

lsttemp = np.asarray(lsttemp)
print(lsttemp)
plt.scatter(lsttemp[:,0], lsttemp[:,1] )
plt.title("Sanding vs non-sanding hrs")
plt.xlabel("sanding")
plt.ylabel("non-sanding")
plt.show()