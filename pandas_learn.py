import pandas

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

df.ix[]

