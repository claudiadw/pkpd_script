import pickle
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


########## LOAD DATA

bow_nofeats=pickle.load(open('bow_nofeats','rb'))
bow_nofeats=pd.DataFrame(bow_nofeats.toarray())

s_bow_matrix=pickle.load(open('selected_bow','rb'))

csv = '/Users/cdw/Desktop/pkpd_script/RNR_ANALYSIS/ready_processed.csv'
papers=pd.read_csv(csv)
y = papers.loc[:,'category']



######### TRAIN FULL SET 30 TIMES, FIND AV

time_f=[]
for i in range(30):
	x_train_f,x_test_f,y_train_f,y_test_f=train_test_split(bow_nofeats,y,test_size=0.15,stratify=y)
	model1=XGBClassifier()
	start_f = time.time()
	model1.fit(x_train_f,y_train_f)
	elapsed_f = time.time()-start_f
	time_f.append(elapsed_f)

av_time_f=np.mean(time_f)
print(av_time_f)



###### TRAIN SMALLER SET 30 TIMES, FIND AV

time_s=[]
for  i in  range(30):
	x_train_s,x_test_s,y_train_s,y_test_s=train_test_split(s_bow_matrix,y,test_size=0.15,stratify=y)
	model_s=XGBClassifier()
	start_s = time.time()
	model_s.fit(x_train_s,y_train_s)
	elapsed_s=time.time()-start_s
	time_s.append(elapsed_s)

av_time_s=np.mean(time_s)
print(av_time_s)




######## calculate difference in time.

dif = av_time_f-av_time_s
reduction = dif/av_time_f*100
print('reduction: {}%'.format(round(reduction)))
