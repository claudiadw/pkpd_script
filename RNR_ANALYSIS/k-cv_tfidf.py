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

print('\n\n\nTFIDF')




################### 1) LOAD DATA


selected_tfidf=pickle.load(open('selected_tfidf','rb'))
print(selected_tfidf.shape[1])
print('^^ this shld be 51')

csv = '/Users/cdw/Desktop/pkpd_script/RNR_ANALYSIS/ready_processed.csv'
papers=pd.read_csv(csv)
y = papers.loc[:,'category']






############### 3) K-FOLD CROSS VALIDATION

model=pickle.load(open('optimal_xgb_tfidf','rb'))

skf = StratifiedKFold(n_splits=10, random_state=61097, shuffle=True)

print('crossvalidating...')
cv_scores = cross_val_score(model,selected_tfidf,y,cv=skf)


print('cross val scores:')
print(cv_scores)



###
elapsed = time.time()-now
print('\n\ntime elapsed: {}s'.format(int(elapsed)))

