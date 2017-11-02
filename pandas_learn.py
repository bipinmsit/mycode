import pandas
import matplotlib.pyplot as plt
%matplotlib inline
import numpy as np
from numpy import NaN, NAN, nan

df = pandas.read_csv("csv_doc", sep="separater")

df.head()  # first couple of rows

type(df)

df.shape

df.columns

df.dtypes

country_df = df['country']   # name of particular column

country_df.head()

subset = df[['country', 'continent']]   # name of all the column that want to display

subset.head()

#we can also do the above task by giving the no. inplace of column name.

subset = df[[1,2,3]]

subset = df[range(1,3)] #subset = df[list(range(1,3))]

df.loc[0]   # subsetting the rows

row_100 = df.loc[99]  # 100th rows

type(row_100)

df.iloc[0]

df.ix[0]	# first row

df.ix[[0,99]]

#df.ix[rows,columns]

df.ix[0,'country']

df.ix[0,1]

df.ix[[0,99,999], ['continent', 'year']]

df.groupby('year')['lifeExp'].mean()

df.groupby(['year','continent'])['lifeExp'].mean()

df.groupby('year')['lifeExp'].mean().plot()





# COMBINING THE DATA


df1 = pandas.read_csv('concat_1.csv')
df2 = pandas.read_csv('concat_2.csv')
df3 = pandas.read_csv('concat_3.csv')

#concatanating the rows

row_concat = pandas.concat([df1, df2, df3])

row_concat.shape

#concatanating the columns

col_concat = pandas.concat([df1,df2,df3], axis=1) # axis=0 means row wise

col_concat['A']	# subset the column by column name

df1.columns = ['A','B','C','D']	# Renaming the column

concanated = pandas.concat([df1,df2,df3])

concanated.to_csv('concatenated.csv')	# save it by given name



# MERGING DATA



person = pandas.read_csv('survey_person.csv')
site = pandas.read_csv('survey_site.csv')
survey = pandas.read_csv('survey_survey.csv')
visited = pandas.read_csv('survey_visited.csv')

o_2_o = site.merge(visited, left_on='name', right_on='site')	# One to One merge



# MISSING DATA

NaN == True

NaN == False

pandas.isnull(NaN)

visited = pandas.read_csv('survey_visited.csv')

visited = pandas.read_csv('survey_visited.csv',keep_default_na=False)	# it replaces NaN to Empty cell

visited = pandas.read_csv('survey_visited.csv',keep_default_na=False, na_values=[''])

#visited.ix[visited.dated,]

pandas.isnull(visited.dated)







