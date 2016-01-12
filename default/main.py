'''
Created on 2016/1/7

@author: K.Yao
'''


from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
import os
import time
import webbrowser

class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
    

    def __getSoup(self, rel_url = ''):
        try:
            conn = urlopen(self.__url + rel_url)
        except HTTPError as e: 
            # Server thinks this is a bot. so we use real broswer to access it!
            driver = webdriver.PhantomJS(executable_path = os.getcwd() + '\phantomjs.exe')
            driver.get(self.__url + rel_url)
            time.sleep(1) # wait for JavaScript executing
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.close()
            return soup
        except URLError as e:
            print(e, self.__url + rel_url)
            return None
        try:
            soup = BeautifulSoup(conn.read(), "html.parser")
        except AttributeError as e:
            print(e, self.__url + rel_url)
            return None
        return soup
    
    def getTitle(self):
        try:
            title = self.__soup.title.get_text().strip()
        except AttributeError:
            return None
        return title

    def openSite(self, rel_url = ''):
        webbrowser.open(self.__url + rel_url)
url = 'http://www.allstate.com/'
site = Website(url)
print(site.getTitle())
# with open('list_of_url.csv', 'rt') as urlFile:
#     csvReader = csv.reader(urlFile)
#     siteList = [ Website(url[0].strip()) for url in csvReader if url[0]]
#     for site in siteList:
#         print(site.getTitle())
        
         
    