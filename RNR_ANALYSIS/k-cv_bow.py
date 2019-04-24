#!/usr/bin/env python
# coding: utf-8

"""Performs k-fold cross validation (k=10) for the entire
'Relevant'/'Not Relevant' dataset
"""

import pickle
import pandas as pd
import time
from xgboost import XGBClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split



__author__ = 'Claudia Dols Wong'
__date__ = '20/04/2019'

now=time.time()

print('\n\n\nBoW')




################### 1) LOAD DATA

bow_nofeats=pickle.load(open('bow_nofeats','rb'))
bow_nofeats=pd.DataFrame(bow_nofeats.toarray())

csv = '/Users/cdw/Desktop/pkpd_script/RNR_ANALYSIS/ready_processed.csv'
papers=pd.read_csv(csv)
y = papers.loc[:,'category']

x_train,x_test,y_train,y_test=train_test_split(bow_nofeats,y,test_size=0.15,random_state=61097,stratify=y)


################# 2) FEATURE SELECTION

print('model training...')
model = XGBClassifier(learning_rate=1,
					max_depth=3,
					n_estimators=25,
					random_state=61097).fit(x_train,y_train)
print('model trained')
selection = SelectFromModel(model, threshold=0.007, prefit=True)
bow_nofeats = selection.transform(bow_nofeats)
print(bow_nofeats.shape[1])
print('^^^ that value should be 51')



############### 3) K-FOLD CROSS VALIDATION

skf = StratifiedKFold(n_splits=10, random_state=61097, shuffle=True)

print('crossvalidating...')
cv_scores = cross_val_score(model,bow_nofeats,y,cv=skf)

print('cross val scores:')
print(cv_scores)



###
elapsed = time.time()-now
print('\n\ntime elapsed: {}'.format(int(elapsed)))

