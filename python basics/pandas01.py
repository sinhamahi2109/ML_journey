import pandas as pd
data1={'Student':['David','Samuel','Terry','Evan'],'Age':['27','24','22','32'],'Country':['UK','Canada','China','USA'],'Marks':['85','72','89','76']}
df=pd.DataFrame(data1)
print(df)
b=df[['Country','Marks']]
print(b)
c=df.iloc[0,0]
print(c)