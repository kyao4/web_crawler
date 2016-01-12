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
import re

class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
        
        #variables for searching for premium (function:getPremium)
        self.__currentSoup = self.__soup 
        self.__targeturl = set()
        self.__internalurl = set()
        self.__externalurl = set()
        
        
    def getPremium(self):
        self.getTargeturl()
        return 0
        targetData = self.getTargetData()
        result = 0
        for v in targetData:
            if v > result:
                result = v
        return result

    def getTargeturl(self, rel_url = ''):
        # first get all internal and external links 
        #caution: add all the internals to internal set before filter
        self.getInternalLinks('')
        #filter all the links with keywords
        
        #add filtered links to target set
        
        #search all the internal set recursively
        pass
    
    def getInternalLinks(self, includeurl):
        for tag in self.__currentSoup.find_all('a', {'href': re.compile('^(/|.*' + self.splitRooturl()[0] + ')')}):
            if tag.attrs['href'] not in self.__internalurl:
                href = tag.attrs['href']
                self.__internalurl.add(href)
                print(href)
    
        
    def getTargetData(self):
        
        pass
    
    def splitRooturl(self):
        addressParts = self.__url.replace("http://", "").split("/")
        return addressParts
    
      
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
    
    
    
        
# url = 'http://www.allstate.com/'
# site = Website(url)
# print(site.getTitle())
with open('list_of_url.csv', 'rt') as urlFile:
    csvReader = csv.reader(urlFile)
    #                                                  stop when shortest sequence is done
    siteList = [ Website(url[0].strip())  for url,i in zip(csvReader, range(5)) if url[0].strip()]
    for site in siteList:
        print(site.getTitle())
        print('premium', site.getPremium())
        
        
         
    