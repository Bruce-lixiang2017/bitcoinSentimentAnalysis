
# coding: utf-8

# In[11]:

import requests                   
from bs4 import BeautifulSoup  
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet
import re, string, csv

stop_words = stopwords.words('english')

# takes a string (document) as input and strips all tokens down to their root (lemmatized) form
def lemmatize(document):
    pattern=r'[a-zA-Z]+[a-zA-Z\-\.]'  
    tokens=[token.strip()     for token in nltk.regexp_tokenize(document, pattern)     if token.strip() not in stop_words and       token.strip() not in string.punctuation]
    wordnet_lemmatizer = WordNetLemmatizer()
    # find the POS tag of each word
    # tagged_token is a list of (word, pos_tag)
    tagged_tokens= nltk.pos_tag(tokens)

    # wordnet - treebank map tagging system function
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

    # get lemmatized tokens
    # lemmatize every word in tagged_tokens
    le_words=[wordnet_lemmatizer.lemmatize(word, get_wordnet_pos(tag))               # tagged_tokens is a list of tuples (word, tag)
              for (word, tag) in tagged_tokens \
              # remove stop words
              if word not in stop_words and \
              # remove punctuations
              word not in string.punctuation]
    return le_words


def get_headlines():
    headlines=[]  # list variable to store headlines
    dates = []    # list variable to store dates
    page_number = 1
    print 'scraping page %s' % page_number
    page_url="https://www.bloomberg.com/search?query=bitcoin&sort=time:desc&endTime=2017-10-13T04:36:58.003Z&page="+str(page_number)
    while page_url!="https://www.bloomberg.com/search?query=bitcoin&sort=time:desc&endTime=2017-10-13T04:36:58.003Z&page=76":
        page_url="https://www.bloomberg.com/search?query=bitcoin&sort=time:desc&endTime=2017-10-13T04:36:58.003Z&page="+str(page_number)        
        page = requests.get(page_url) 
        page_number += 1
        print 'scraping page %s' % page_number
        if page.status_code!=200:  
            page_number = 76 #if page status code fails to equal 200, connection failed; set page_num to while loop condition
        else:                   
            soup = BeautifulSoup(page.content, 'html.parser')                        
            
#-----------scrape and clean all headlines and append to a list called headlines----------------------------------------------
            for header in soup.find_all('h1', class_ ='search-result-story__headline'):
                headline = header.get_text().lower()
                headlines.append(lemmatize(headline))
                

#-----------scrape all dates and append to a list called dates---------------------------------------------------------------
            for date in soup.find_all('time', class_ = 'published-at'):
                date_published = date.get_text()
                dates.append(date_published)
                
                
#---convert headlines into tuples--------------------------------------------------------------------------------------------
    for idx, headline in enumerate(headlines):
        headlines[idx] = tuple(headline)
    
#---join headlines list and dates list into a list of tuples called data-----------------------------------------------------
    data = zip(headlines, dates)
    
#---remove headlines without these keywords----------------------------------------------------------------------------------
    keywords = ['bitcoin', 'cryptocurrency', 'cryptocurrencies', 'crypto', 'blockchain']
    filtered_data = filter(lambda x: any(word in x[0] for word in keywords), data)
    
    return filtered_data

            
if __name__ == "__main__":  
    
    cleaned_data = get_headlines()
    print("%s" % len(cleaned_data) + " headlines were scraped; stopwords were removed; data lemmatized; data written to csv file")

    with open("bloomberg.csv", "w") as f:                    
        writer=csv.writer(f, delimiter=',')          
        writer.writerows(cleaned_data)


# In[ ]:



