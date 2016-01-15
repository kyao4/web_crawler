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
        self.__currentSoup = None
        self.__interalurl = set()
        self.__interalTargetTag = set()
        self.__exteralTargetTag = set()
        
        
    def getPremium(self):
        self.getTargeturl()
        print('------------------------->internal_target')
        #add filtered tag to target set
        for tag in self.__interalTargetTag:
            print(tag)        
        
        print('------------------------->external_target')
        for tag in self.__exteralTargetTag:
            print(tag)        
        return 0
        targetData = self.getTargetData()
        result = 0
        for v in targetData:
            if v > result:
                result = v
        return result

    def getTargeturl(self, rel_url = '', abs_url = ''):
        
        self.__currentSoup = self.__getSoup(rel_url, abs_url)
        #if current url is not accessible stop recurrence
        if not self.__currentSoup:
            return
        
        # first get all internal and external tags and links
        #caution: add all the internal url to internalurl set before filter
        cur_inter_tag = self.getInternalLinks()
        for tag in cur_inter_tag:
            if tag.attrs['href'] == '//s1.q4cdn.com/405296365/files/doc_financials/2015/ACE-Limited-2014-Annual-Report.pdf':
                pass
        cur_exter_tag = self.getExternalLinks()
        self.__interalurl = self.__interalurl.union({tag.attrs['href']for tag in cur_inter_tag})
        self.__interalTargetTag = self.__interalTargetTag.union(cur_inter_tag)
        self.__exteralTargetTag = self.__exteralTargetTag.union(cur_exter_tag)
        #filter all the tags with keywords
        cur_inter_tag = {tag for tag in cur_inter_tag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}
        self.__interalTargetTag = {tag for tag in self.__interalTargetTag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}
        self.__exteralTargetTag = {tag for tag in self.__exteralTargetTag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}        
        print('------------------------->internal')
        #add filtered tag to target set
        for tag in cur_inter_tag:
            print(tag)
#         print('------------------------->external')
#         for tag in self.__exteralTargetTag:
#             print(tag)
        #search all the internal set recursively
        for tag in cur_inter_tag:
            if re.search('^(http|www)', tag.attrs['href'], re.IGNORECASE):
                self.getTargeturl(abs_url = tag.attrs['href']) #this is internel link but have http://, so don't add root
            else:
                self.getTargeturl(tag.attrs['href'])
                
        pass
    
    def getInternalLinks(self):
        internalTag = set()
        for tag in self.__currentSoup.find_all('a', {'href': re.compile('^(/|.*' + self.extractRooturl() + ')')}): #include root url
            if tag.attrs['href'] not in self.__interalurl:
#                 href = tag.attrs['href']
#                 self.__internalurl.add(href)
                internalTag.add(tag)
#                 print(href)
#                 print(tag)
        return internalTag
            
    def getExternalLinks(self):
        externalTag = set()
        for tag in self.__currentSoup.find_all('a', {'href': re.compile('^(http|www)((?!' + self.extractRooturl() + ').)*$')}): #exclude root url
            if tag not in self.__exteralTargetTag:
#                 href = tag.attrs['href']                
#                 self.__externalurl.add(href)
                externalTag.add(tag)
#                 print(href)
#                 print(tag)
        return externalTag
    
    def getTargetData(self):
        #at this point we should have all the target tag(url) in this website, all we need 
        #to do is search each page's table and search pdf for target data.
        targetpdf_internal = {tag.attrs['href'] for tag in self.__interalTargetTag if tag.attrs['href'].search(r'?!' + self.extractRooturl() + '.*\.pdf')}
        targetpdf_internal.union({tag.attrs['href'] for tag in self.__interalTargetTag})
        targetpdf_external = set()
        
        
        
        pass
    
    def extractRooturl(self):
        url = re.sub('http://|www.', '', self.__url)
        addressParts = url.split("/")
        return addressParts[0]
    
      
    def __getSoup(self, rel_url = '', abs_url = ''):
        #eliminate escape characters content with UTF-8
        rel_url = bytes(rel_url, 'UTF-8')
        rel_url = rel_url.decode('ascii', 'ignore')
        abs_url = bytes(abs_url, 'UTF-8')
        abs_url = abs_url.decode('ascii', 'ignore')
        
        try:
            if abs_url:
                conn = urlopen(abs_url)
            else:
                conn = urlopen(self.__url + rel_url)
        except HTTPError as e: 
            # Server thinks this is a bot. so we use real broswer to access it!
            driver = webdriver.PhantomJS(executable_path = os.getcwd() + '\phantomjs.exe')
            if abs_url:
                driver.get(abs_url)
            else:
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
        
        
#         if self.__url == 'http://www.aegislink.com/':
#             pass
        #if this site content meta redirect, attach new url to root url and reopen it.
        #eg. <meta content="1; URL=/aegislink.html" http-equiv="Refresh">
        redirectTag = soup.find('meta', {'content' : re.compile('url=', re.IGNORECASE), 'http-equiv' : re.compile('Refresh', re.IGNORECASE)} )
        if redirectTag:
            m = re.search(r'url=/(.*)', redirectTag.attrs['content'], re.IGNORECASE)
            return self.__getSoup(self.__url + m.group(1))
#TODO not working!!

        # <link href="http://www.acegroup.com" rel="canonical"/>
        # if this site use link to redirect url to real one, we have to recognize it
        linkTag = soup.find('link', {'rel' : re.compile('canonical', re.IGNORECASE)} )
        if linkTag and linkTag.attrs['href']:
            self.__url = linkTag.attrs['href']
            try:
                if abs_url:
                    conn = urlopen(abs_url)
                else:
                    conn = urlopen(self.__url + rel_url)
            except HTTPError as e: 
                # Server thinks this is a bot. so we use real broswer to access it!
                driver = webdriver.PhantomJS(executable_path = os.getcwd() + '\phantomjs.exe')
                if abs_url:
                    driver.get(abs_url)
                else:
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
        
        
         
    