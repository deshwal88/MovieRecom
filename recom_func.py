import os
import numpy as np
import pandas as pd
from zipfile import ZipFile
import ibm_boto3
from ibm_botocore.client import Config
from skimage.io import imread
import matplotlib.pyplot as plt
import requests
import nltk


def checker(file_names,file): 
    """
    Checks whether the files in file_names exists in the given folder or not.
    
    Args:
        file_names: name of the files.
        file: the folder name in the relative path.
        
    Returns:
        bool(True or False)
    """
    
    print('ckecking data...')
    cond=False
    if os.path.exists(f'./{file}'):     
        cond=True
        for item in file_names:
            if os.path.exists(f'./{file}/'+str(item)):
                continue
            else:
                cond=False
        print('completed')
    return cond


def unzip(comp,file):
    """
    Unzips or extracts the file into a folder given by the user.
    
    Args:
        comp: name of the compressed file in the relative path.
        file: folder name in which the compressed file is extracted.
    
    Returns:
        does not have a return value.
    """
    
    with ZipFile(comp) as compressed:
        print('unzipping data...')
        compressed.extractall(f'./{file}/')
        print('completed')
        
        
def data_retrieval(comp):
    """
    the given file will be retrived or downloaded in the relative path from the cloud object storage.

    Args:
        comp: filename to be retrieved.
        
    Returns:
        does not have a return value.
    """
    
    print('downloading data...(227MB)')
    credentials={"api_key": "QouAvUnBFzdt8WgugSwEdk3cvFvGWFtaLVSqOOmdID6B",\
             "bucket":"moviesdataset",\
             "endpoint_url":"https://s3.eu-de.cloud-object-storage.appdomain.cloud",\
             "service_id":"crn:v1:bluemix:public:cloud-object-storage:global:a/7952d450a1c747d6a4fd528ca95a95\
             2c:b8d2f94f-1bca-442a-ae31-0ba42b0ce6ec::"}
    cos=ibm_boto3.client("s3",\
                         ibm_api_key_id=credentials['api_key'],\
                         ibm_service_instance_id=credentials['service_id'],\
                         config=Config(signature_version='oauth'),\
                         endpoint_url=credentials['endpoint_url'],\
                         region_name='ap-standard')
    print('it may take a few minutes depending upon the connection speed')
    cos.download_file(comp,f'{comp}.zip',f'./{comp}.zip')
    print('downloaded.')
    
    
def eval_extract(row,string):
    """
    It is used when json dictionary is treated as a string when loading data.
    json dictionary when evaluated as expression is a list of dictionaries containing information in key-value pairs.
    The value corresponding to the given key embedded in a list is extracted.
    
    Args:
        row: list in the form of a string object.
        string: key of the dictionary whose value is to be extracted.
        
    Returns:
        list or nan.
    """
    
    try:
        row=eval(row)
        value=''
        for element in row:
            value+=' '+element[string].replace(' ','_')
        if len(value)<2:
            return np.nan
        else:
            return value
    except:
        return np.nan


def get_req(cred,string,query):
    """
    Pulls requests according to the credentials provided.
    
    Args:
        string: comes after the base url of the api.
        query: comes after string to form end pint url.
        
    Returns:
        request object.
    """
    
    end_point_url=f"{cred['api_base_url']}/{string}/{query}?"
    req=requests.get(end_point_url,params={'api_key':cred['api_key']})
    return req


def show_output(output,query_str='images',size='w185',return_order=(3,3)):
    """
    It extracts the posters from tmdb api according to the imbd id enlisted in the output with  year and demographic ratings calculated.
    the credentials of imbd api are also specified in this function.

    Args:
        output: a dataframe containing information about the movies.(imdb_id, year, ratings, etc)
        query_string: is the query to the tmdb api which completes the endpoint url.(default: 'images')
        size: size of the images. (default: 'w185')
        return_order: subplot order to show output movies arranged in rows and columns.(default: (3,3))
        
    Returns:
        no return value
    """
    
    print('Fetching results...') 
    cred={"api_base_url":"https://api.themoviedb.org/3/movie","api_key":"30d7de721f9ac1c958640499561b574a"}
    plt.rcParams['figure.figsize']=(22,13)
    fig,ax=plt.subplots(return_order[0],return_order[1])
    ax=ax.ravel()

    print('Showing results...')
    default_img=imread('https://uxwing.com/wp-content/themes/uxwing/download/07-design-and-development/image-not-found.png')
    img_base_url=f"https://image.tmdb.org/t/p/{size}/"
    for i in range(0,return_order[0]*return_order[1]):
        try:
            req=get_req(cred,output.imdb_id.values[i],query=query_str)
            img=req.json()['posters'][0]['file_path']
            ax[i].imshow(imread(img_base_url+img))
        except:
            ax[i].imshow(default_img)

        name,y=output[['title','year']].values[i]
        r=output[['ratings']].values[i]
        ax[i].set_xlabel("{0}\nYear:{1}\nRating:{2}/10".format(name,y,'%.1f'%(r)))
        ax[i].set_yticklabels('')
        ax[i].set_xticklabels('')
    plt.show()
    
    
def search_mov(inp,movies):
    """
    It calculates the levenshtien distance between the input titles and all the movie titles in the frame and returns the bottom 6.

    Args:
        inp: user input.
        movies: the reference dataframe.
        
    Returns:
        index for bottom 6.
    """
    
    print('searching...')
    def leven_sim(s1,s2):
        return nltk.edit_distance(s1,s2)/max(len(s1),len(s2))
    search=movies['title'].apply(leven_sim,s2=inp)
    print('done.')
    return search.sort_values().head(6)


def search_eng(frame):
    """
    This function takes input from the user and provides assistance to the user to select the exact movie with poster.

    Args:
        frame: the reference dataframe.
        
    Returns:
        returns DataFrame.
    """
    
    inp_frame=pd.DataFrame(columns=['imdb_id','title'])
    rating=[]

    print('type DONE to exit the search process and RESET to reset inputs.')
    while(True):
        inp=str(input('Enter movie name: ')).lower()

        if inp=='done':
            break
            
        if inp=='reset':
            inp_frame=pd.DataFrame(columns=['imdb_id','title'])
            continue

        index=search_mov(inp,frame)
        temp=frame.loc[index.keys()]
        show_output(temp,return_order=(2,3)) 

        print('If movie not found type any string(not found!)')
        ind=str(input('Select from the movies. Enter choice number(1-6)\n'))
        if ind.isnumeric():
            inp_frame=inp_frame.append(temp.iloc[int(ind)-1][['imdb_id','title']])
            r=float(input('Rate the movies out of 10: '))
            rating.append(r)
        else:
            continue

    inp_frame['ratings']=rating
    return inp_frame

