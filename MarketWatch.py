
# coding: utf-8

# In[8]:

import requests
from datetime import datetime
from bs4 import BeautifulSoup
import nltk, re, string
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet
wordnet_lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(pos_tag):
    
    # if pos tag starts with 'J'
    if pos_tag.startswith('J'):
        # return wordnet tag "ADJ"
        return wordnet.ADJ
    
    # if pos tag starts with 'V'
    elif pos_tag.startswith('V'):
        # return wordnet tag "VERB"
        return wordnet.VERB
    
    # if pos tag starts with 'N'
    elif pos_tag.startswith('N'):
        # return wordnet tag "NOUN"
        return wordnet.NOUN
    
    elif pos_tag.startswith('R'):
        return wordnet.ADV
    else:
        # be default, return wordnet tag "NOUN"
        return wordnet.NOUN


def tokenize(s):

    text= s

    pattern= r'[a-zA-Z]+[a-zA-Z\-\.]*'                        

    tokens=nltk.regexp_tokenize(text, pattern)

    vocabulary= tokens
    return vocabulary;

def tokenize_date(s):
    pattern=r'[a-z{3}]+[\.\s]+[\d{1,2}\,\s]+[\d{4}]+'                        
    tokens=nltk.regexp_tokenize(s, pattern)
    date = tokens
    return date;

stop_words = stopwords.words('english')

headlines=[]
    
page_url= "https://www.marketwatch.com/search?q=bitcoin&m=Keyword&rpp=500&mp=806&bd=false&bdv=&rs=false"

while page_url!=None:
    page = requests.get(page_url) 
    
    if page.status_code!=200:
         page_url=None
    else:
        all_data = []
        
        page_url = "https://www.marketwatch.com/search?q=bitcoin&m=Keyword&rpp=500&mp=806&bd=false&bdv=&rs=false"
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", class_ = "searchresult")
        titles_list = []
        titles_dictionary = []
        for idx, div in enumerate(divs):
            titles = div.select("a")
            if titles != []:
                title = titles[0].get_text().lower()
                titles_list.append(title)
                title = tokenize(title)
                tagged_tokens = nltk.pos_tag(title)
                le_words =[wordnet_lemmatizer.lemmatize(word, get_wordnet_pos(tag))                            for (word, tag) in tagged_tokens                            if word not in stop_words and                            word not in string.punctuation]
                vocabulary = set(le_words)
                dictionary={word: title.count(word) for word in vocabulary}
                filtered_dictionary={word: dictionary[word] for word in dictionary if word not in stop_words}
                titles_dictionary.append(filtered_dictionary)
        divs_dates = soup.find_all("div", class_ = "deemphasized")
        dates_list = []
        for idx, div in enumerate(divs_dates):
            date = div.get_text().lower()
            date = str(tokenize_date(date)[0])
            dates_list.append(date)
        data = zip(titles_list, titles_dictionary,dates_list)  
        all_data.extend(data)
    
    page_url = None

keywords = ['bitcoin','cryptocurrency','cryptocurrencies', 'crypto', 'blockchain']
filtered_data = filter(lambda x: any(word in x[0] for word in keywords), all_data)
data_frame = pd.DataFrame.from_records(filtered_data, columns = ["Title", "Tokenized Title", "Date"])
data_frame.to_csv("marketwatch.csv", encoding='utf-8')


# In[ ]:



