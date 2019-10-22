"""
Read in data and effectivly analyze it
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt
from matplotlib.ticker import PercentFormatter
sns.set()

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

"""
Class to track the hours in the format they come in as. 
Possibly useless as it could just be subsituted by the parse
function instead of it being contained in a object

TODO: decide whether to swap out the class for the function or not
"""
class jiraHrs():
    def __init__(self, s):
        self.timeTotal = self.parse(s)

    """
    Parse the time commited as they come in form Jira into hrs
    Ex:
    1d -> 3hrs
    30m -> 0.5hrs
    """
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

# Read in csv data and grab columns of interest
comments_df = pd.read_csv("commentsIssue.csv")
time_per_person = comments_df[["Name","Author", "time spent", "logged at"]]

# Start by creating dictionaries for sanding and machining hrs and total commited per member
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

# Plot sanding vs machining hrs
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

#======================================================================
# Annotate each point with the netid
for i, txt in enumerate(label_sanding_vs_nonsanding):
    ax.annotate(txt, (plot_sanding_vs_nonsanding[:,0][i],  plot_sanding_vs_nonsanding[:,1][i]))
plt.title("Sanding vs Non-Sanding hrs")
plt.xlabel("machine (hrs)")
plt.ylabel("sand (hrs)")
plt.savefig("./Graphs/sanding_vs_machining.png")
plt.show()


"""
Creates a pareto plot from a label and data list

@param values: data to input. list
@param name_of_val: str for pareto index
@param index: label of each pareto bar. list
"""
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
    plt.savefig("./Graphs/Pareto_"+name_of_val+"_time.png")
    plt.show()

create_pareto_chart(plot_sanding_vs_nonsanding[:,0], "machine", label_sanding_vs_nonsanding)
create_pareto_chart(plot_sanding_vs_nonsanding[:,1], "sanding", label_sanding_vs_nonsanding)

#======================================================
# Plot accumalted time contibuted per member over the year
mem_to_machine_time = {}

# Sort comments_df
comments_df = comments_df.sort_values(by = "logged at")

# Generate cummalative hours from the comments
for index,row in comments_df.iterrows():
    if row["Name"] not in sanding:
        if row["Author"] not in mem_to_machine_time:
            mem_to_machine_time[row["Author"]] = [( jiraHrs(row["time spent"]).getHrs() , row["logged at"] )]
        else:
            temp = mem_to_machine_time[row["Author"]]
            temp.append( (mem_to_machine_time[row["Author"]][-1][0] + jiraHrs(row["time spent"]).getHrs(), row["logged at"] ) )
            mem_to_machine_time[row["Author"]] = temp

# Create DF from data
total_time_df = pd.DataFrame(mem_to_machine_time[list(members.keys())[0] ])

# concatenate data across members into one DF
for mem in list(members.keys())[1:]:
    total_time_df = pd.concat( [total_time_df, pd.DataFrame(mem_to_machine_time[mem])] , ignore_index=True, axis=1)
total_time_df.columns = np.array([[x, x + " logged at"] for x in list(members.keys())]).flatten()

total_time_df.to_csv("time_total.csv", index = False)

# Plotting data
fig, ax = plt.subplots(figsize = (12,8))
for mem in members:
    dates = [dt.datetime.strptime(dates_logged, "%Y-%m-%dT%H:%M:00.000+0000") for dates_logged in total_time_df[mem+" logged at"].dropna().values.tolist()]
    date_for_mem = [mdates.date2num(date) for date in dates]
    ax.plot(date_for_mem, total_time_df[mem].dropna().values.tolist(), '-o')

ax.legend(loc = "upper left", labels = list(members.keys()) )
ax.set(xlabel="Date", ylabel="Cumalative Hrs",
       title="Tracked hours over the year. Total: " 
       + str(round(sum([total_time_df[mem].dropna().values.tolist()[-1] for mem in members]), 3)) )
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%y"))
plt.savefig("./Graphs/Cummalative_Hrs_over_time_per_member.png")
plt.show()
    