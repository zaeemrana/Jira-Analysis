"""
Read in data and effectivly analyze it
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime
from matplotlib.ticker import PercentFormatter

sns.set()

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

"""
# format the ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.xaxis.set_minor_locator(months)

# round to nearest years.
datemin = np.datetime64(data['date'][0], 'Y')
datemax = np.datetime64(data['date'][-1], 'Y') + np.timedelta64(1, 'Y')
ax.set_xlim(datemin, datemax)

# format the coords message box
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = lambda x: '$%1.2f' % x  # format the price.
ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()
"""

class weirdDateTime():
    def __init__(self, s):
        self.currentDT = np.datetime64(s)

    def getCurrentDT(self):
        return self.currentDT

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

#=================================================================
plot_sanding_vs_nonsanding = []
label_sanding_vs_nonsanding = []
for s in members:
    if s in members_sanding:
        label_sanding_vs_nonsanding.append(s)
        plot_sanding_vs_nonsanding.append( (members[s], members_sanding[s]) )
plot_sanding_vs_nonsanding = np.asarray(plot_sanding_vs_nonsanding)

fig, ax = plt.subplots()

fig.set_size_inches(8, 6)
ax.scatter(plot_sanding_vs_nonsanding[:,0], plot_sanding_vs_nonsanding[:,1] )


for i, txt in enumerate(label_sanding_vs_nonsanding):
    ax.annotate(txt, (plot_sanding_vs_nonsanding[:,0][i],  plot_sanding_vs_nonsanding[:,1][i]))
plt.title("Sanding vs non-sanding hrs")
plt.xlabel("machine (hrs)")
plt.ylabel("sand (hrs)")
plt.savefig("./Graphs/sanding_vs_machining.png")
plt.show()
#=================================================================


def create_pareto_chart(values, name_of_val, index ):
    df = pd.DataFrame({name_of_val: values})
    df.index = index
    df = df.sort_values(by=name_of_val,ascending=False)
    df["cumpercentage"] = df[name_of_val].cumsum()/df[name_of_val].sum()*100


    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    ax.bar(df.index, df[name_of_val], color="C0")
    ax2 = ax.twinx()
    ax2.plot(df.index, df["cumpercentage"], color="C1", marker="D", ms=7)
    ax2.yaxis.set_major_formatter(PercentFormatter())

    ax.tick_params(axis="y", colors="C0")
    ax2.tick_params(axis="y", colors="C1")
    ax2.set_xlabel("Members")
    ax2.set_ylabel("Total "+name_of_val+" Hrs")
    ax2.set_title("Pareto of "+name_of_val+" Contribution")
    plt.show()

#create_pareto_chart(plot_sanding_vs_nonsanding[:,0], "machine", label_sanding_vs_nonsanding)
#create_pareto_chart(plot_sanding_vs_nonsanding[:,1], "sanding", label_sanding_vs_nonsanding)

mem_to_machine_time = {}
for index,row in comments_df.iterrows():
    if row["Name"] not in sanding:
        if row["Author"] not in mem_to_machine_time:
            mem_to_machine_time[row["Author"]] = [( jiraHrs(row["time spent"]).getHrs() , row["logged at"] )]
        else:
            temp = mem_to_machine_time[row["Author"]]
            temp.append( (mem_to_machine_time[row["Author"]][-1][0] + jiraHrs(row["time spent"]).getHrs(), row["logged at"] ) )
            mem_to_machine_time[row["Author"]] = temp

total_time_df = pd.DataFrame(mem_to_machine_time[list(members.keys())[0] ])

for mem in list(members.keys())[1:]:
    total_time_df = pd.concat( [total_time_df, pd.DataFrame(mem_to_machine_time[mem])] , ignore_index=True, axis=1)
total_time_df.columns = np.array([[x, x + " logged at"] for x in list(members.keys())]).flatten()
total_time_df.to_csv("time_total.csv", index = False)


plt.plot(total_time_df["zmr5 logged at"].dropna(), total_time_df["zmr5"].dropna())
plt.show()
    