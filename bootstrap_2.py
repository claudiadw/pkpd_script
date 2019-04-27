import pickle
import random
import pandas as pd
import numpy as np
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier


##  choose dataset
dataset=input('\n\n\n\nBig/small dataset? -->      ')


#### set number of validations
number_of_iterations=int(input('Number of iterations -->    '))
random.seed(61097)
rand_states = [random.randint(1,1000) for x in range(number_of_iterations)]
print()


### set conditional args
if dataset == 'big':
    bow_matrix=pickle.load(open('bow_matrix','rb'))
    bow_nofeats=pickle.load(open('selected_bow','rb'))
    csv = 'ready_processed.csv'
    params=dict(n_estimators=80,max_depth=3,learning_rate=0.4,reg_alpha=0.01,reg_lambda=0.01)

elif dataset == 'small':
    bow_matrix=pickle.load(open('bow_matrix_small','rb'))
    bow_nofeats=pickle.load(open('selected_bow_small','rb')).toarray()
    csv='all-old.csv'
    params=dict(n_estimators=25,learning_rate=0.771,max_depth=3)


#### make input data
bow_nofeats=pd.DataFrame(bow_nofeats)
papers=pd.read_csv(csv)
y = papers.loc[:,'category']
all_docs = list(bow_matrix.index.values)


#### bootstrap loop
accuracies=[]
f1s=[]
n_samples=int(bow_matrix.shape[1]*0.85)

for r in rand_states:
    boot = resample(bow_matrix,replace=True,n_samples=n_samples,random_state=r)
    ## generate train&test sets
    training_ind = list(boot.index.values)
    training_int = [int(doc[3:]) for doc in training_ind]
    testing_ind = [x for x in all_docs if x not in training_ind]
    testing_int = [int(doc[3:]) for doc in testing_ind]
    x_train=bow_nofeats.iloc[training_int]
    x_test = bow_nofeats.iloc[testing_int]
    y_train=y[training_int]
    y_test=y[testing_int]
    ## train & evaluate model
    model=XGBClassifier(random_state=61097).set_params(**params)
    model.fit(x_train,y_train)
    y_pred = model.predict(x_test)
    accuracies.append(accuracy_score(y_test,y_pred))
    f1s.append((y_test,y_pred,pos_label='Relevant'))


#### evaluation metrics
mean_acc=np.mean(accuracies)
std_acc=np.std(accuracies)
mean_f1=np.mean(f1s)
std_f1=np.std(f1s)

print('RESULTS FOR BIG DATASET:')
print('accuracy mean: {}, std: {}'.format(round(mean_acc,5),round(std_acc,5)))
print('f1       mean: {}, std: {}'.format(round(mean_f1,5),round(std_f1,5)))
print('\n\n\n')




