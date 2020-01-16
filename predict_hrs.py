"""
Predict Jira hours based on previous sample of Jira issues

Will use:
XBGoost

@author Zaeem
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn import preprocessing
import os
import seaborn as sns
import re
import itertools
sns.set(style="darkgrid")

# Plotting fucntions for later
def learning_curve(train, test):
    fig = plt.figure(figsize=(12, 7))
    plt.plot(range(1,len(train)+1), train, range(1,len(test)+1), test)
    plt.xlabel("Epochs")
    plt.ylabel("Eval")
    plt.gca().legend(('train','test'))
    plt.savefig("./Predict/learning_curve.png")
    plt.show()
    
def scatter_preds(preds, truth, test):
    fig = plt.figure(figsize=(12, 7))
    sns.regplot(preds, truth, marker="+")
    x = np.linspace(min(preds), max(preds) ,100)
    y120 = x * 1.2
    y80 = x * 0.8
    plt.plot(x,x, 'g', linewidth=3)
    plt.plot(x, y120, 'y', linewidth=3)
    plt.plot(x, y80, 'y', linewidth=3)
    plt.xlabel("predictions")
    plt.ylabel("truth")
    plt.title("Pred. vs. Truth "+ test)
    plt.savefig("./Predict/pred_scatter_"+test +".png")
    plt.show()

def detetermine_accuracy(preds, truth):
    n = truth.shape[0]
    x =(np.absolute(preds - truth) / truth) <= 0.15
    y =(np.absolute(preds - truth) / truth) <= 0.1
    w =(np.absolute(preds - truth) / truth) <= 0.2
    print("Percent within 20%: ",np.sum(w)/n * 100 )
    print("Percent within 15%: ",np.sum(x)/n * 100 )
    print("Percent within 10%: ",np.sum(y)/n * 100 )
    return np.sum(w)/n * 100, np.sum(x)/n * 100, np.sum(y)/n * 100

#=================================
# Data acquisition and pre-processing
timeIssueOA_df = pd.read_csv('./Analysis/timeIssueOAMF.csv')
genIssueOA_df = pd.read_csv('./Analysis/generalIssueOAMF.csv')
timeIssueMech2_df = pd.read_csv('./Analysis/timeIssueMech2.csv')
genIssueMech2_df = pd.read_csv('./Analysis/generalIssueMech2.csv')

timeIssueOA_df = timeIssueOA_df.append(timeIssueMech2_df)
genIssueOA_df = genIssueOA_df.append(genIssueMech2_df)

joined_df = genIssueOA_df.set_index('Name').join(timeIssueOA_df.set_index('Name'),  lsuffix='_caller', rsuffix='_other')

joined_prefeatures_df = joined_df[["Summary", "Parent Key", "Parent Sumamry", "Assignee Name", "Time Spent", 'WorkRatio','AggregateTimeOriginial', 'original estimate']]

def preprocessWords(s):
    s = s.replace("(","")
    s = s.replace(")","")
 
    if "_" in s and " " in s:
        lst = s.split("_")
        lst = [word.split(" ") for word in lst]
    elif "_" in s:
        lst = s.split("_")
    elif " " in s:
        lst = s.split(" ")
    else:
        lst = []

    retlst = []
    for word in lst:
        if type(word) == list:
            retlst = retlst + word
        else:
            retlst.append(word)

    #for word in retlst:
    retlst = [re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", word ) for word in retlst]
    
    comblst = []
    for word in retlst:
        comblst = comblst + word.split(" ")

    retlst = comblst
    retlst = [word.lower() for word in retlst]
    return retlst

totWords = []
lstSummaries = []
for index, row in joined_prefeatures_df.iterrows():
    #print(row["Summary"])
    lstWords = preprocessWords(row["Summary"])
    #print(lstWords)
    lstSummaries.append(" ".join(lstWords))
    for subWord in lstWords:
        if subWord not in totWords:
            totWords = totWords + [subWord]

#print(len(totWords))
#print(totWords)
#print("$"*30)
#print(lstSummaries)
vectorizer = HashingVectorizer(n_features=2**8)
X = vectorizer.fit_transform(lstSummaries)
arr = X.toarray()
df = pd.DataFrame(arr)
df.to_csv('./Predict/hashedVectorizorMatrix.csv', index = False)

dictwords={}
count = 0
for words in totWords:
    if words != "":
        dictwords[words] = count
        count = count + 1

wordVectors = []
for sentance in lstSummaries:
    vector = [0]*len(totWords)
    for word in sentance.split(" "):
        if word != "":
            vector[dictwords[word]] = 1
    wordVectors.append(vector)

df1 = pd.DataFrame(np.array(wordVectors), columns = list(totWords))
# df1["Summary"] = joined_prefeatures_df["Summary"].values
df1['original estimate'] = joined_prefeatures_df['original estimate'].values
df1["WorkRatio"] = joined_prefeatures_df["WorkRatio"].values
df1["Time Spent"] = joined_prefeatures_df["Time Spent"].values


df1 = df1[np.isfinite(df1["Time Spent"])]
df1 = df1[np.isfinite(df1['original estimate'])]
df1 = df1[np.isfinite(df1["WorkRatio"])]
df1.to_csv("./Predict/xyVectors.csv")

#=======================================

# Train and Run
issueMetricData = []
rowMetrics = []

# Normalize data
xy = df1.values
#scaler = preprocessing.MinMaxScaler()
#x_scaled = scaler.fit_transform(xy)
#df1 = pd.DataFrame(x_scaled)
df1 = pd.DataFrame(xy)

# Extract, Shuffle & Split Data
df1 = shuffle(df1)
print("Total Shape: ", df1.shape)
train, test = train_test_split(df1, test_size=0.3)
test, vali = train_test_split(test, test_size=0.5)

# Define Parameters & Estimators
x = train.iloc[:,:-1].to_numpy()
y = train.iloc[:,-1].to_numpy()
testX = test.iloc[:,:-1].to_numpy()
testY = test.iloc[:,-1].to_numpy()
valiX = vali.iloc[:,:-1].to_numpy()
valiY = vali.iloc[:,-1].to_numpy()

dtrain = xgb.DMatrix(x, label = y)
dtest = xgb.DMatrix(testX, label = testY)
dvali= xgb.DMatrix(valiX, label = valiY)
# Create Parameters for model
param = {
    'eval metric': 'rmse',
    'verbosity': 0,
    'max_depth': 2,
    'eta':0.01,
    'gamma': 0.5,
    'min_child_weight': 1
}
evallist = [(dvali, 'eval'), (dtrain, 'train')]
progress = dict()

# Train
num_round = 750
print("Training: ")
bst = xgb.train(param, 
                dtrain, 
                num_round,
                evals = evallist, 
                early_stopping_rounds = 15,
                verbose_eval = 50,
                evals_result = progress
                )

bst.dump_model("./Predict/models/dump.txt")
bst.save_model("./Predict/model.txt")

# Predicted for test data
ypred_train = bst.predict(dtrain, ntree_limit = bst.best_ntree_limit)
ypred_test = bst.predict(dtest)

# Get Testing Metrics
bst_mse_error_test = mean_squared_error(testY, ypred_test)
bst_mae_error_test = mean_absolute_error(testY, ypred_test)
rowMetrics = rowMetrics + [bst_mse_error_test, bst_mae_error_test]
feature_importance = bst.get_fscore()

# TODO: Feature Importance (word rankings) 

# Get Training Metrics
bst_mse_error_train = mean_squared_error(y, ypred_train)
bst_mae_error_train = mean_absolute_error(y, ypred_train)
rowMetrics = rowMetrics + [bst_mse_error_train, bst_mae_error_train]

# Plotting
#xgb.plot_importance(bst)
#print(ypred_test)
#print("*"*50)
#print(testY)
#print(xy.shape)
#print(scaler.inverse_transform(xy))
#print(scaler.inverse_transform(ypred_test))

#scatter_preds(scaler.inverse_transform(ypred_test.reshape(-1,1)),scaler.inverse_transform(testY.reshape(-1,1)))

scatter_preds(ypred_test, testY,"test_vali")
scatter_preds(ypred_train, y, "train_vali")
learning_curve(progress['train']['rmse'] ,  progress['eval']['rmse'])

within2per, within5per, within10per = detetermine_accuracy(ypred_test, testY)
issueMetricData.append(rowMetrics+[within2per,within5per,within10per])
