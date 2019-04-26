import pickle
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier



csv = '/Users/cdw/Desktop/pkpd_script/RNR_ANALYSIS/ready_processed.csv'
papers=pd.read_csv(csv)
y = papers.loc[:,'category']

bow_nofeats=pickle.load(open('bow_nofeats','rb'))
bow_nofeats=pd.DataFrame(bow_nofeats.toarray())

x_train_f,x_test_f,y_train_f,y_test_f=train_test_split(bow_nofeats,y,test_size=0.15,random_state=61097,stratify=y)

print(bow_nofeats.shape[1])
print('^^ shld be 42056\n')


x_train_s,x_test_s,y_train_s,y_test_s=train_test_split(bow_nofeats,y,test_size=0.15,random_state=61097,stratify=y)

s_bow_matrix=pickle.load(open('selected_bow','rb'))

print(s_bow_matrix.shape[1])
print('^^ should be 55\n')





model1=XGBClassifier()
start_t = time.time()

model1.fit(x_train_f,y_train_f)

elapsed_t = time.time()-start_t
print('full: {}s'.format(elapsed_t))
print()





model2=XGBClassifier()
start_s = time.time()

model2.fit(x_train_s,y_train_s)

elapsed_s=time.time()-start_x
print('selected: {}s'.format(elapsed_s))
