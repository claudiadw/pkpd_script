#!/usr/bin/env python
# coding: utf-8

"""Various text mining functions written for
pre-processing of pubmed papers for NLP
"""


import pubmed_parser as PP
import pandas as PD
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import os

__author__ = "Claudia Dols Wong"
__date__ = '20/04/2019'






def strip_non_ascii(string):
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)

def find(s, c1):
    return [i for i, c2 in enumerate(s) if c2 == c1]






def remove_duplicates(csv,by_col):
	df = PD.read_csv(csv)
	print(len(df))
	df.drop_duplicates(inplace=True,subset=by_col)
	print(len(df))
	df.to_csv(csv,index=None)







#makes raw csv from dataframe input containing pmids, returns outfile name
def make_csv(catfile):

	headers = ['pmid','title','abstract','journal','affiliation','authors','year','keywords','category']
	csv_db = PD.DataFrame(columns=headers,index=None)

	labelled = PD.read_csv(catfile)
	pmids = labelled.loc[:,'pubmed_id']
	pmid_cat = labelled.loc[:,'paper_category']

	for n,c in zip(pmids,pmid_cat):
		paper = PP.parse_xml_web(n)
		paper_row = [n,paper['title'],paper['abstract'],paper['journal'],paper['affiliation'],\
					paper['authors'],paper['year'],paper['keywords'],c]
		csv_db.loc[len(csv_db)+1] = paper_row

	outfile_name = catfile[:-4]+'_processed.csv'

	csv_db.to_csv(outfile_name,index=None)
	return outfile_name





#same as previous function but written to manipulate a slightly different dataframe ....
#makes raw csv file from dataframe input containing pmids, returns outfile name
def make_csv_(catfile,outfile_name):

	headers = ['pmid','title','abstract','journal','affiliation','authors','year','keywords','category']
	csv_db = PD.DataFrame(columns=headers,index=None)

	labelled = catfile
	pmids = labelled.loc[:,'id']
	pmid_cat = labelled.loc[:,'label']

	counter=0
	for n,c in zip(pmids,pmid_cat):
		paper = PP.parse_xml_web(n)
		paper_row = [n,paper['title'],paper['abstract'],paper['journal'],paper['affiliation'],\
					paper['authors'],paper['year'],paper['keywords'],c]
		csv_db.loc[len(csv_db)+1] = paper_row
		counter+=1
		if counter%10==0:
			print(counter,end=' ')

	csv_db.to_csv(outfile_name,index=None)
	return outfile_name






#removes the entries with no abstract as these can't be used for classification!
def abs_csv(file):
	csv_db = PD.read_csv(file)


	no_abs_list = []
	for i,abs in enumerate(csv_db.loc[:,'abstract']):
		if not isinstance(abs,str):
			no_abs_list.append(i)
			continue
		abs = strip_non_ascii(abs)
		csv_db.at[i,'abstract'] = abs

	csv_db = csv_db.drop(no_abs_list)

	csv_db.to_csv(file,index=None)





#cleans the csv raw info so some of the columns are tokenised.
def clean_csv(file):
	
	csv_db = PD.read_csv(file, encoding = 'ISO-8859-1')

	for i,title in enumerate(csv_db.loc[:,'title']):
		try:
			if title[0] == '[':
				title = title[1:-2]+'.'
				csv_db.at[i,'title'] = title
		except TypeError:
			csv_db.at[i,'title'] = ''

	for i,af in enumerate(csv_db.loc[:,'affiliation']):
		if isinstance(af,str) == False:
			import math
			if math.isnan(af) == True:
				continue
		stop = af.find('.')
		af = af[:stop]
		csv_db.at[i,'affiliation'] = af

	for i,a_raw_str in enumerate(csv_db.loc[:,'authors']):
		print(i)
		if isinstance(a_raw_str,float):
			csv_db.at[i,'authors'] = ''
		else:
			a_raw_list = strip_non_ascii(a_raw_str).split('; ')
			a_list = []
			for x in a_raw_list:
				ind = find(x,' ')
				last_name = x[ind[-1]+1:]
				first_name = x[:ind[-1]]
				if find(first_name,' '):
					first_names = first_name.split(' ')
					first_initials = [a[0] if a[0].islower()==False else a for a in first_names]
					full_name = ' '.join(first_initials)+' '+last_name
				else:
					full_name = first_name[0]+' '+last_name
				a_list.append(full_name)
			a_str = ' ## '.join(a_list)
			csv_db.at[i,'authors'] = a_str

	for i,kw_raw_str in enumerate(csv_db.loc[:,'keywords']):
		if isinstance(kw_raw_str,float):
			csv_db.at[i,'keywords'] = ''
		else:
			try:
				start = find(kw_raw_str,':')
				stop = find(kw_raw_str,';')
				kw_list = [kw_raw_str[x+1:y].lower() for x,y in zip(start,stop)]
				kw_list.append(kw_raw_str[start[-1]+1:])
			except IndexError:
				kw_list = kw_raw_str.split(';')

			kw_str = ' ## '.join(kw_list)
			csv_db.at[i,'keywords'] = kw_str


	csv_db.to_csv(file,index=None)






#creates a list of tokens for each paper and changes the csv
def features_db(prepro_csv):
	ps = PorterStemmer()

	csv_db = PD.read_csv(prepro_csv)

	stop_corpus = open('english.txt')
	stop_words = [line.strip() for line in stop_corpus]

	headers = ['pmid','words','category']
	features = PD.DataFrame(columns=headers,index=None)

	for index,row in csv_db.iterrows():
		bag = word_tokenize(row['abstract'])
		bag = [w.lower() for w in bag if w.lower() not in stop_words]
		bag = [ps.stem(w) for w in bag]
		for word in bag:
			if word.isnumeric():
				bag.remove(word)
			try:
				if float(word):
					bag.remove(word)
			except: continue
		
		try:
			title_w = row['title'].split(' ')
			title_w = [w.lower() for w in title if w.lower() not in stop_words]
			title_w = [ps.stem(w) for w in title_w]
			title_w = [w+'T' for w in title_w]
			for w in title_w:
				bag.append(w)
		except: pass

		try:
			mesh_w = row['keywords'].split(' ## ')
			mesh_w = [w+'M' for w in mesh_w]
			for w in mesh_w:
				bag.append(w)
		except: pass

		try:
			author_w = row['authors'].split(' ## ')
			author_w = [w+'A' for w in author_w]
			for w in author_w:
				bag.append(w)
		except: pass

		try:
			bag.append(row['journal']+'J')
		except: pass

		words = '!$!'.join(bag)

		new_row = [row['pmid'],words,row['category']]

		features.loc[len(features)+1] = new_row

	features.to_csv(prepro_csv,index=None)






def tidy_categories(path_to_csv):
	labelled_papers = PD.read_csv(path_to_csv,index_col=None)
	labelled_papers = labelled_papers.replace('NCA','Non-compartmental')
	labelled_papers = labelled_papers.replace('Non-compartmental Analysis','Non-compartmental')
	labelled_papers = labelled_papers.replace('Not Relevant','Not relevant')
	labelled_papers = labelled_papers.replace('Compartmental','Modelling')
	labelled_papers = labelled_papers.replace('Non-compartmental analysis','Non-compartmental')
	mask = labelled_papers['category'] != '-'
	labelled_papers = labelled_papers[mask]
	labelled_papers.to_csv(path_to_csv,index=False)





#converts 'modelling' and 'nca' to 'relevant'
def binary_categories(path_to_csv):
	papers = PD.read_csv(path_to_csv,index_col=None)
	papers = papers.replace('Non-compartmental','Relevant')
	papers = papers.replace('Modelling','Relevant')
	#return papers
	papers.to_csv(path_to_csv,index=False)






#combines all the csvs in a directory to one BIG csv
def generate_allcsv(directory,out_name):
	all = PD.DataFrame(columns=['pmid','words','category'],index=None)
	for filename in os.listdir(directory):
		if filename.endswith(".csv"):
			all = PD.concat([all,PD.read_csv(directory+filename)])
		else: continue
	all.to_csv(out_name,index=False)







def print_proportions(train,test):
    print('TRAINING\n',(train.value_counts()/train.count())*100)
    print()
    print('TESTING\n',(test.value_counts()/test.count())*100)