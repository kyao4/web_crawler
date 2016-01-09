'''
Created on 2016/1/7

@author: K.Yao
'''
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import random

class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
        self.__siteMap = set()
        
    
    def __getSoup(self, relativeurl = ''):
        try:
            conn = urlopen(self.__url + relativeurl)
        except HTTPError as e:
            print(e)
            return None
        try:
            soup = BeautifulSoup(conn.read())
        except AttributeError as e:
            print(e)
            return None
        return soup
    
    
    def getSiteMap(self, relativeurl = ''):
        soup = self.__getSoup(relativeurl)
        if soup == None:
            return
        try:
            print(soup.h1.get_text())
            print(soup.find('', {'id': 'mw-content-text'}).find('p').get_text())
            print(soup.find('', {'id': 'ca-edit'}).find('span').find('a').attrs['href'])
        except AttributeError:
            pass
        try:
            links = soup.body.find_all('a', {'href': re.compile('^(/wiki/)((?!:).)*$')})
        except AttributeError:
            return
        for link in links:
            if link.attrs['href'] not in self.__siteMap:
                newPage = link.attrs['href']
                self.__siteMap.add(newPage)
                print('\n------------->' + newPage)
                self.getSiteMap(newPage)
    
    
    def getTitle(self):
        '''
        return title of a page, if there is no title in this
        page return None
        '''
        try:
            title = self.__soup.title.get_text()
        except AttributeError:
            return None
        return title
    
    def getallLinks(self):
        return self.__soup.body.find_all('a', {'href' : re.compile('^(/wiki/)((?!:).)*$')})
        
    def getallLinksByURL(self, relativeurl):
        try:
            conn = urlopen(self.__url + relativeurl)
        except HTTPError as e:
            print(e)
            return None
        try:
            soup =  BeautifulSoup(conn.read())
            links = soup.body.find_all('a', {'href' : re.compile('^(/wiki/)((?!:).)*$')})
        except AttributeError as e:
            print(e)
            return None
        return links
    
    def sixDegree(self, relativeurl):
        links = self.getallLinksByURL(relativeurl)
        while links:
            nextLink = links[random.randint(0, len(links) - 1)].attrs['href']
            print(nextLink)
            links = self.getallLinksByURL(nextLink)
            
    def getHTML(self):
        '''
        If return None, There are errors in URL
        '''
        try:
            HTML = self.__soup.prettify()
        except AttributeError:
            return None
        return HTML
    
    def getRedTag(self):
        for span in self.__soup.find_all('span', {'class':'red'}):
            print(span.get_text())
            
    def getH1H2(self):
        for head in self.__soup.find_all(['h1', 'h2']):
            print(head.get_text())
            
    def getTableChildren(self):
        for child in self.__soup.find('table', {'id':'giftList'}).descendants:
            print(child)
            
    def getTableDataRow(self):
        for row in self.__soup.find('table', {'id':'giftList'}).tr.next_siblings:
            print(row)
    
    def getImagePrice(self):
        print(self.__soup.find('img', {'src': '../img/gifts/img1.jpg'}).parent.previous_sibling.get_text())
    
    def getImagebyRE(self):
        for img in self.__soup.find_all('img', {'src': re.compile("\.\.\/img\/gifts/img.*\.jpg")}):
            print(img)
            
            
            
url = 'https://en.wikipedia.org'
site = Website(url)
print(site.getTitle())

# for link in site.getallLinks():
#     print(link.attrs['href'])

# site.sixDegree('/wiki/Kevin_Bacon')

site.getSiteMap()
