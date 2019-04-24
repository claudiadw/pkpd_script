#!/usr/bin/env python
# coding: utf-8

"""Performs k-fold cross validation (k=10) for the entire
'Relevant' dataset
"""

import pickle
import pandas as pd
import time
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import StratifiedKFold, cross_val_score



__author__ = 'Claudia Dols Wong'
__date__ = '20/04/2019'

now=time.time()

print('\n\n\nLinearSVC')




################### 1) LOAD DATA

selected_tfidf=pickle.load(open('tfidf_nofeats_selected','rb'))
print(selected_tfidf.shape[1])
print('^^ this shld be 320')

csv = '/Users/cdw/Desktop/pkpd_script/MNCA_ANALYSIS/ready_processed_2.csv'
papers=pd.read_csv(csv)
relevant = ['Non-compartmental','Modelling']
relevant_papers = papers.loc[papers['category'].isin(relevant)]
y = relevant_papers.loc[:,'category']



############### 2) K-FOLD CROSS VALIDATION

model=LinearSVC(random_state=61097,max_iter=10000)
skf = StratifiedKFold(n_splits=10, random_state=61097, shuffle=True)

print('crossvalidating...')
cv_scores = cross_val_score(model,selected_tfidf,y,cv=skf)

print('cross val scores:')
print(cv_scores)



###
elapsed = time.time()-now
print('\n\ntime elapsed: {}s'.format(int(elapsed)))

