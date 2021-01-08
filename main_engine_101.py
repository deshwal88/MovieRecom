import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
import recom_func as func
import recom_al as al


file_names=['movies_metadata.csv','ratings_small.csv','links_small.csv','keywords.csv']
folder_name='movies_40k'
comp='./movies_40k.zip'

if not(func.checker(file_names,folder_name)):
    if os.path.exists(comp):
        func.unzip(comp,folder_name)
        
    else:                           
        if input('Data not found! Would you like to download the data and continue?\n').lower()=='yes':
            func.data_retrieval(comp)
            func.unzip(comp)
        else:
            exit()


##Building Model

print('Uploading data...')
warnings.filterwarnings('ignore')
movies=pd.read_csv(f'./{folder_name}/{file_names[0]}')
ratings=pd.read_csv(f'./{folder_name}/{file_names[1]}')
links=pd.read_csv(f'./{folder_name}/{file_names[2]}')
keywords=pd.read_csv(f'./{folder_name}/{file_names[3]}')
print('done!')

print('Preparing data for modeling...')
ratings=pd.merge(links,ratings,on=['movieId'])

req_columns=['id','title','release_date','production_companies','genres','vote_average','popularity','vote_count','imdb_id']
movies=movies[req_columns]

keywords['words']=keywords['keywords'].apply(func=func.eval_extract,string='name')
keywords.id=keywords.id.astype('str')
movies=pd.merge(movies,keywords,on='id').drop('keywords',axis=1)

movies.genres=movies.genres.apply(func.eval_extract,string='name')
movies.production_companies=movies.production_companies.apply(func=func.eval_extract,string='name')

movies['year']=movies.release_date.str.extract('(\d\d\d\d)')
movies.genres=movies.genres.fillna('not_listed')
movies.production_companies=movies.production_companies.fillna('not_listed')
movies.words=movies.words.fillna('not_listed')

movies=movies.dropna()
movies=movies.groupby('id',sort=False).head(1).reset_index()
movies=movies.drop(['release_date','index'],axis=1)

print('done!')


### 1. Demographic recommendations

##### Creating IMDB based rating function

m=movies.vote_count.quantile(0.90)
C=movies.vote_average.mean()

print('Calculating Demographic rating of movies...')
dem_ratings=movies.apply(al.get_rating,C=C,m=m,axis=1)
output_dem=movies[['title','imdb_id','id','year']]
output_dem['ratings']=dem_ratings
output_dem=output_dem.sort_values(by='ratings',ascending=False)
print('Done!')


##### Showing results

func.show_output(output_dem)

##### Content-based recommendations

print('Preparing the system...')

vect_gen=TfidfVectorizer()
vect_key=TfidfVectorizer()

vectorised_gen=vect_gen.fit_transform(movies.genres).toarray()
vectorised_key=vect_key.fit_transform(movies.words).toarray()

feature_set=np.append(vectorised_gen,vectorised_key,axis=1)
print('done')

print('calculating...')
inp_frame=func.search_eng(output_dem)
output_cont=al.cont_based(inp_frame,feature_set,output_dem)

##### Showing results
func.show_output(output_cont)
exit()
