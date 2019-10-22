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
import os
import seaborn as sns
import re
import itertools
sns.set(style="darkgrid")

# Plotting fucntions for later
def learning_curve(train, test,file):
    fig = plt.figure(figsize=(12, 7))
    plt.plot(range(1,len(train)+1), train, range(1,len(test)+1), test)
    plt.xlabel("Epochs")
    plt.ylabel("Eval")
    plt.gca().legend(('train','test'))
    plt.savefig("./Images/Model_Pred/learning_curve_"+ file +".png")
    plt.show()
    
def scatter_preds(preds, truth,file, test):
    fig = plt.figure(figsize=(12, 7))
    sns.regplot(preds, truth, marker="+")
    x = np.linspace(min(preds), max(preds) ,100)
    y105 = x * 1.05
    y95 = x * 0.95
    plt.plot(x,x, 'g', linewidth=3)
    plt.plot(x, y105, 'y', linewidth=3)
    plt.plot(x, y95, 'y', linewidth=3)
    plt.xlabel("predictions")
    plt.ylabel("truth")
    plt.title("Pred. vs. Truth " + file + " " + test)
    plt.savefig("./Images/Model_Pred/pred_scatter_"+ file+ "_"+test +".png")
    plt.show()

def detetermine_accuracy(preds, truth):
    n = truth.shape[0]
    x =(np.absolute(preds - truth) / truth) <= 0.05
    y =(np.absolute(preds - truth) / truth) <= 0.1
    w =(np.absolute(preds - truth) / truth) <= 0.02
    print("Percent within 2%: ",np.sum(w)/n * 100 )
    print("Percent within 5%: ",np.sum(x)/n * 100 )
    print("Percent within 10%: ",np.sum(y)/n * 100 )
    return np.sum(w)/n * 100, np.sum(x)/n * 100, np.sum(y)/n * 100

#=================================
# Data acquisition and pre-processing
timeIssue_df = pd.read_csv('./Analysis/timeIssue.csv')
genIssue_df = pd.read_csv('./Analysis/generalIssue.csv')

joined_df = genIssue_df.set_index('Name').join(timeIssue_df.set_index('Name'),  lsuffix='_caller', rsuffix='_other')

# print(joined_df.head())
# print(joined_df.columns)

joined_prefeatures_df = joined_df[["Summary", "Parent Kay", "Parent Sumamry", "Assignee Name", "Time Spent", 'WorkRatio','AggregateTimeOriginial', 'original estimate']]

bag_o_words = {}
# flatten = lambda l: [item for sublist in l for item in sublist]
def preprocessWords(s):
    s = s.replace("(","")
    s = s.replace(")","")
    #s = re.sub(r"(\w)([A-Z])", r"\1 \2", s)
    #s = s.lower()
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
            print(lst)
        else:
            retlst.append(word)

    #print(retlst)
    #lst = list(itertools.chain.from_iterable(lst))
    lst = [words.lower() for words in retlst]


    return lst

for index, row in joined_prefeatures_df.iterrows():
    print(row["Summary"])
    lstWords = preprocessWords(row["Summary"])
    print(lstWords)

"""
#=======================================
# Train and Run
xgbMetricData = []
xgbPredData = np.zeros((4516,40))
rowMetrics = [file]
uniqIdent = file[5:-4]
numFile = file[10:-5]

# Extract, Shuffle & Split Data
"""
#df = pd.read_csv("../0_Data/" + file)
"""
df = shuffle(df)
train, test = train_test_split(df, test_size=0.3)
test, vali = train_test_split(test, test_size=0.5)

# Define Parameters & Estimators
x = train.iloc[:,3:-1].to_numpy()
y = train.iloc[:,-1].to_numpy()
testX = test.iloc[:,3:-1].to_numpy()
testY = test.iloc[:,-1].to_numpy()
valiX = vali.iloc[:,3:-1].to_numpy()
valiY = vali.iloc[:,-1].to_numpy()

dtrain = xgb.DMatrix(x, label = y)
dtest = xgb.DMatrix(testX, label = testY)
dvali= xgb.DMatrix(valiX, label = valiY)
# Create Parameters for model
param = {
    'eval metric': 'mse',
    'verbosity': 0,
    'max_depth': 9,
    'eta':0.06
    #'gamma': 0.1,
    #'min_child_weight':1
}
evallist = [(dvali, 'eval'), (dtrain, 'train')]
progress = dict()

# Train
num_round = 750
bst = xgb.train(param, dtrain, num_round,
                evals = evallist, 
                early_stopping_rounds = 15,
                verbose_eval = 50,
                evals_result = progress
                )

bst.dump_model("./dumps/dump_" + uniqIdent + ".txt")
bst.save_model("./Models/model_" + uniqIdent + ".txt")

# Predicted for test data
ypred_train = bst.predict(dtrain, ntree_limit = bst.best_ntree_limit)
ypred_test = bst.predict(dtest)

# Get Testing Metrics
bst_mse_error_test = mean_squared_error(testY, ypred_test)
bst_mae_error_test = mean_absolute_error(testY, ypred_test)
rowMetrics = rowMetrics + [bst_mse_error_test, bst_mae_error_test]
feature_importance = bst.get_fscore()

pd.DataFrame(data= [inlineParamLst[i] for i in [ int(k[1:]) for k in list(feature_importance.keys()) ] ], columns = ["Featuer_importance"]).to_csv("feature_importance.csv",index=False)

# Get Training Metrics
bst_mse_error_train = mean_squared_error(y, ypred_train)
bst_mae_error_train = mean_absolute_error(y, ypred_train)
rowMetrics = rowMetrics + [bst_mse_error_train, bst_mae_error_train]

# Plotting
xgb.plot_importance(bst)

scatter_preds(ypred_test, testY,uniqIdent,"test_vali")
scatter_preds(ypred_train, y,uniqIdent, "train_vali")
learning_curve(progress['train']['rmse'] ,  progress['eval']['rmse'], uniqIdent)

within2per, within5per, within10per = detetermine_accuracy(ypred_test, testY)
xgbMetricData.append(rowMetrics+[within2per,within5per,within10per])

xgbPredData[:,int(numFile)-1] = testY
xgbPredData[:,int(numFile)+19] = ypred_test

print("*"*100)
"""