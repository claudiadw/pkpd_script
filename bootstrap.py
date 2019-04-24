
#!/usr/bin/env python
# coding: utf-8

"""Performs bootstrap cross validation (cv=30) for the entire
'Relevant'/'Not Relevant' dataset
"""


import pickle
import random
import pandas as pd
import numpy as np
import time
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier
from sklearn.feature_selection import SelectFromModel
random.seed(61097)

__author__ = 'Claudia Dols Wong'
__date__ = '20/04/2019'

now=time.time()

print('\n\n\n')





################### 1) LOAD DATA
tfidf_matrix=pickle.load(open('tfidf_matrix', 'rb'))

tfidf_nofeats=pickle.load(open('tfidf_nofeats','rb'))
tfidf_nofeats=pd.DataFrame(tfidf_nofeats.toarray())

csv = '/Users/cdw/Desktop/pkpd_script/RNR_ANALYSIS/ready_processed.csv'
papers=pd.read_csv(csv)
y = papers.loc[:,'category']





################### 2) CREATE BOOTSTRAP LOOP

#create data structures for loop
accuracies={}
f1s={}

all_docs = list(tfidf_matrix.index.values)

number_of_iterations=30
rand_states = [random.randint(1,1000) for x in range(number_of_iterations)]



#bootstrap iterations
counter=1

for r in rand_states:
    print('Sample {}'.format(counter))
    counter+=1

    boot = resample(tfidf_matrix,replace=True,n_samples=1600,random_state=r)


    training_ind = list(boot.index.values)
    training_int = [int(doc[3:]) for doc in training_ind]
    testing_ind = [x for x in all_docs if x not in training_ind]
    testing_int = [int(doc[3:]) for doc in testing_ind]


    x_train=tfidf_nofeats.iloc[training_int]
    x_test = tfidf_nofeats.iloc[testing_int]
    y_train=y[training_int]
    y_test=y[testing_int]



    model=XGBClassifier(n_estimators=80,max_depth=3,
                           seed=61097,learning_rate=0.4,
                           reg_alpha=0.01,reg_lambda=0.01).fit(x_train,y_train)

    selection = SelectFromModel(model, threshold=0.013, prefit=True)
    select_x_train = selection.transform(x_train)
    select_x_test = selection.transform(x_test)

    model2=XGBClassifier(n_estimators=80,max_depth=3,
                           seed=61097,learning_rate=0.4,
                           reg_alpha=0.01,reg_lambda=0.01).fit(select_x_train,y_train)
    y_pred = model2.predict(select_x_test)

    accuracy = accuracy_score(y_test,y_pred)
    accuracies['sample{}'.format(counter)]=accuracy
    
    f1 = f1_score(y_test,y_pred,pos_label='Relevant')
    f1s['sample{}'.format(counter)]=f1

    print('acc={}    f1={}'.format(round(accuracy,2),round(f1,2)))
    print()





#################### 3) CALCULATE MEAN ACCURACY & F1

print('\n\n\n')
mean_acc=sum(accuracies.values())/len(accuracies)
mean_f1=sum(f1s.values())/len(f1s)
print('MEAN ACCURACY = {}'.format(mean_acc))
print('MEAN F1 = {}'.format(mean_f1))



print('\n\n\n')
print('accuracies:')
print(accuracies)
print()
print('f1s:')
print(f1s)


elapsed=time.time()-now
print('run time: {}'.format(elapsed))

