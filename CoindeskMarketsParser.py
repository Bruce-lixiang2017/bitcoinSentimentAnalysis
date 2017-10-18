
# coding: utf-8

# In[1]:

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

    pattern=r'[a-zA-Z]+[a-zA-Z\-\.]*'                        

    tokens=nltk.regexp_tokenize(text, pattern)

    vocabulary= tokens
    return vocabulary;

stop_words = stopwords.words('english')

headlines=[]
    
page_url= "https://www.coindesk.com/category/markets-news/markets-markets-news/markets-bitcoin/"

while page_url!=None:
    page = requests.get(page_url) 
    
    if page.status_code!=200:
         page_url=None
    else:
        all_data = []
        for num in range(1,20):
            page_url = "https://www.coindesk.com/category/markets-news/markets-markets-news/markets-bitcoin/page/"+str(num)+"/"
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, "html.parser")
            titles = soup.find_all("a", class_ = "fade")
            titles_list = []
            titles_dictionary = []
            for i in titles:
                title = i.get_text().lower()
                titles_list.append(title)
                title = tokenize(title)
                tagged_tokens = nltk.pos_tag(title)
                le_words =[wordnet_lemmatizer.lemmatize(word, get_wordnet_pos(tag))                            for (word, tag) in tagged_tokens                            if word not in stop_words and                            word not in string.punctuation]
                vocabulary = set(le_words)
                dictionary={word: title.count(word) for word in vocabulary}
                filtered_dictionary={word: dictionary[word] for word in dictionary if word not in stop_words}
                titles_dictionary.append(filtered_dictionary)
            dates = soup.find_all("time")
            dates_list = []
            for i in dates:
                date = i.get_text().lower()
                date = date.replace(' at', '')
                date = datetime.strptime(date, '%b %d, %Y %H:%M')
                date = datetime.strftime(date,'%b-%d-%Y')
                dates_list.append(date)
            authors = soup.find_all("cite")
            authors_list = []
            for i in authors:
                author = i.get_text().lower()
                authors_list.append(author)
            data = zip(titles_list, titles_dictionary,dates_list,authors_list)  
            all_data.extend(data)
    
    page_url = None
data_frame = pd.DataFrame.from_records(all_data, columns = ["Title", "Tokenized Title", "Date", "Authors"])
data_frame.to_csv("coindesk_markets.csv", encoding='utf-8')


# In[ ]:



